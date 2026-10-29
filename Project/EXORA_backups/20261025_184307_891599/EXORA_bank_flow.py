"""Manual bank settlement. Bank transfers and identity checks are performed outside EXORA."""
import json,re,secrets,time,sqlite3,shutil,uuid
from pathlib import Path
from datetime import datetime
from PIL import Image
import EXORA_database as db

STATES={'identity_pending':'รอตรวจข้อมูลผู้รับ','identity_verified':'ตรวจข้อมูลแล้ว / รอรับราคา','quoted':'รอโอนชำระ','payment_pending':'รอตรวจเงินเข้า','payment_verified':'รับชำระแล้ว / รอโอนจ่าย','payout_processing':'กำลังดำเนินการโอนจ่าย','completed':'โอนจ่ายสำเร็จ','rejected':'ไม่ผ่านการตรวจข้อมูล'}
STATES['route_pending']='ยืนยันตัวตนแล้ว / รอตรวจบัญชีรับเงิน'
STATES['quote_pending_route']='คำนวณแล้ว / รอตรวจช่องทางโอน'

# เก็บขั้นตอนใหม่โดยไม่แปลงข้อมูลจำลองเป็นธุรกรรมจริง
def migrate(conn):
    from EXORA_identity import migrate as migrate_identity
    migrate_identity(conn)
    conn.execute('''CREATE TABLE IF NOT EXISTS bank_flow(number TEXT PRIMARY KEY,user_id INTEGER NOT NULL,
        recipient TEXT,bank TEXT,account TEXT,country TEXT,source TEXT,target TEXT,amount TEXT,status TEXT,
        quote TEXT,identity_note TEXT,route_note TEXT,payment_ref TEXT,payout_ref TEXT,payout_proof TEXT)''')
    conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS bank_flow_payout_reference ON bank_flow(payout_ref) WHERE payout_ref IS NOT NULL')
    conn.execute('CREATE TABLE IF NOT EXISTS bank_flow_audit(id INTEGER PRIMARY KEY,number TEXT,actor INTEGER,action TEXT,note TEXT,created_at TEXT)')
    if 'feedback' not in {row[1] for row in conn.execute('PRAGMA table_info(bank_flow)')}:conn.execute('ALTER TABLE bank_flow ADD COLUMN feedback TEXT')

# ตรวจบัญชีและสิทธิ์จากฐานข้อมูลจริง
def role(conn,actor):
    row=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()
    if not row:raise PermissionError('บัญชีไม่พร้อมใช้งาน')
    return row[0]

def audit(conn,number,actor,action,note=''):
    conn.execute('INSERT INTO bank_flow_audit(number,actor,action,note,created_at) VALUES (?,?,?,?,?)',(number,actor,action,note,datetime.now().isoformat(timespec='seconds')))

# จำกัดเจ้าของหรือ admin ไม่คืนเลขบัญชีให้ผู้ใช้คนอื่น
def get(number,actor):
    conn=db.getconnect()
    try:
        access=role(conn,actor);conn.row_factory=sqlite3.Row
        row=conn.execute('SELECT * FROM bank_flow WHERE number=?',(number,)).fetchone()
        if not row:raise ValueError('ไม่พบรายการ')
        if row['user_id']!=actor and access!='admin':raise PermissionError('เฉพาะเจ้าของรายการ')
        return dict(row)
    finally:conn.close()

def listing(actor,own_only=False):
    conn=db.getconnect()
    try:
        access=role(conn,actor);conn.row_factory=sqlite3.Row
        own=access!='admin' or own_only
        return [dict(row) for row in conn.execute('SELECT * FROM bank_flow'+(' WHERE user_id=?' if own else '')+' ORDER BY rowid DESC',(actor,) if own else ())]
    finally:conn.close()

# บัญชีรับเงินเป็นสำเนาของรายการ ไม่เปลี่ยนตามโปรไฟล์ภายหลัง
def create(actor,recipient,bank,account,country,source,target,amount):
    fields=[str(v).strip() for v in (recipient,bank,account,country)]
    if any(not v or len(v)>120 for v in fields):raise ValueError('กรุณากรอกข้อมูลให้ครบทุกช่อง')
    account=re.sub(r'[ -]','',account).upper()
    if not re.fullmatch(r'[A-Z0-9]{6,34}',account):raise ValueError('เลขบัญชีรับเงินไม่ถูกต้อง')
    from EXORA_security import validate_transaction_amount
    value=validate_transaction_amount(amount)
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');role(conn,actor)
        codes={row[0] for row in conn.execute('SELECT currency_code FROM currencies')}
        if source==target or source not in codes or target not in codes or 'THB' not in (source,target):raise ValueError('เลือกซื้อหรือขายเงินต่างประเทศกับ THB')
        number='EXB-'+secrets.token_hex(8).upper()
        from EXORA_identity import valid
        state='identity_verified' if valid(conn,actor,fields[0]) else 'identity_pending'
        conn.execute('INSERT INTO bank_flow(number,user_id,recipient,bank,account,country,source,target,amount,status) VALUES (?,?,?,?,?,?,?,?,?,?)',(number,actor,fields[0],fields[1],account,fields[3],source,target,str(value),state))
        audit(conn,number,actor,'created');conn.commit();return number
    finally:conn.close()

# ตรวจข้อมูลและช่องทางโอนโดยเจ้าหน้าที่ ต้องบันทึกวิธีตรวจ ไม่ใช่การตรวจ eKYC อัตโนมัติ
def verify(number,actor,identity_note,route_note,method='document_video',valid_until=None,expected_document_id=None):
    if not 10<=len(route_note.strip())<=500:raise ValueError('กรอกผลตรวจตัวตนและการยืนยันช่องทางธนาคารอย่างน้อย 10 ตัวอักษร')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');_admin(conn,number,actor,('identity_pending','route_pending','identity_verified','quote_pending_route'))
        user,name=conn.execute('SELECT user_id,recipient FROM bank_flow WHERE number=?',(number,)).fetchone()
        from EXORA_identity import valid,record
        if not valid(conn,user,name):record(conn,user,name,actor,identity_note,method,valid_until,expected_document_id)
        price=conn.execute('SELECT quote FROM bank_flow WHERE number=?',(number,)).fetchone()[0]
        state='quoted' if price and json.loads(price)['quote_expires']>=time.time() else 'identity_verified'
        conn.execute("UPDATE bank_flow SET status=?,identity_note=?,route_note=?,feedback=NULL WHERE number=?",(state,'Account identity verified',route_note.strip(),number));audit(conn,number,actor,'route_and_identity_verified');conn.commit()
    except Exception:conn.rollback();raise
    finally:conn.close()

def identity_status(number,actor):
    row=get(number,actor);conn=db.getconnect()
    try:
        from EXORA_identity import valid
        return valid(conn,row['user_id'],row['recipient'])
    finally:conn.close()

def revoke_identity(number,actor):
    row=get(number,actor);conn=db.getconnect()
    try:
        from EXORA_identity import revoke
        revoke(conn,row['user_id'],actor);conn.commit()
    finally:conn.close()

# ตรวจซ้ำเฉพาะเมื่อข้อมูลเปลี่ยน/หมดอายุ/ถูกระงับ โดยไม่ย้อนสถานะเงินที่รับแล้ว
def renew_identity(number,actor,reference,method,valid_until,expected_document_id=None):
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');_admin(conn,number,actor,tuple(STATES))
        user,name=conn.execute('SELECT user_id,recipient FROM bank_flow WHERE number=?',(number,)).fetchone()
        from EXORA_identity import record
        record(conn,user,name,actor,reference,method,valid_until,expected_document_id)
        conn.execute("UPDATE bank_flow SET status='identity_verified' WHERE number=? AND status='identity_pending'",(number,));conn.commit()
    except Exception:conn.rollback();raise
    finally:conn.close()

# ออกราคาใหม่หลังผ่านการตรวจ โดยไม่รับยอดผลลัพธ์ที่ลูกค้าส่งมา
def quote(number,actor):
    row=get(number,actor)
    if row['user_id']!=actor:raise PermissionError('เฉพาะเจ้าของรายการ')
    if row['status'] not in ('identity_pending','identity_verified','route_pending','quoted','quote_pending_route'):raise ValueError('สถานะไม่ถูกต้อง')
    if not identity_status(number,actor):raise ValueError('กรุณายืนยันตัวตนใหม่ ข้อมูลเปลี่ยน หมดอายุ หรือถูกระงับ')
    from EXORA_profiles import shop,quote as calculate
    store=shop()
    if store.get('bank_receiving_currency','THB').upper()!=row['source']:raise ValueError('บัญชีร้านยังไม่รองรับสกุลเงินต้นทางนี้ ห้ามโอนชำระจนกว่าร้านยืนยันช่องทางรับเงิน')
    if not all(store.get(k) for k in ('bank_name','bank_account_name','bank_account_number')):raise ValueError('ร้านยังไม่ได้ตั้งบัญชีรับเงิน')
    price=calculate(row['source'],row['target'],row['amount'],actor_id=actor)
    state='quoted' if row['route_note'] else 'quote_pending_route'
    _change(number,actor,('identity_pending','identity_verified','route_pending','quoted','quote_pending_route'),state,owner=True,quote=json.dumps(price));return price

# รับข้อมูลผู้โอนจากฟอร์ม ตรวจและบันทึกพร้อม metadata ของ flow ใหม่
def submit_payment(number,actor,payment,source):
    row=get(number,actor)
    if row['user_id']!=actor or row['status']!='quoted':raise PermissionError('เฉพาะเจ้าของรายการที่รอชำระ')
    import EXORA_payments as payments
    price=json.loads(row['quote']);data={**payment,**price,'customer_name':row['recipient'],'payment_method':'bank'}
    from decimal import Decimal,InvalidOperation
    from EXORA_profiles import shop
    if shop().get('bank_receiving_currency','THB').upper()!=row['source']:raise ValueError('บัญชีร้านไม่รองรับสกุลเงินต้นทาง')
    try:matching=Decimal(str(payment.get('transfer_amount','')))==Decimal(str(price['from_amount']))
    except InvalidOperation:matching=False
    if not matching:raise ValueError('ยอดโอนต้องตรงกับยอดต้นทางของรายการ')
    if not str(data.get('transfer_reference','')).strip():raise ValueError('กรุณาระบุเลขอ้างอิงการชำระ')
    payments.submit(number,actor,data,source)

# ใช้ภายใน payments.submit เพื่อผูก flow กับรายการจริงโดย atomic
def submitted(conn,number,actor):
    row=conn.execute('SELECT user_id,status FROM bank_flow WHERE number=?',(number,)).fetchone()
    if row:
        if row!=(actor,'quoted'):raise ValueError('สถานะไม่ถูกต้อง')
        from EXORA_identity import valid
        name=conn.execute('SELECT recipient FROM bank_flow WHERE number=?',(number,)).fetchone()[0]
        if not valid(conn,actor,name):raise ValueError('กรุณายืนยันตัวตนใหม่ ข้อมูลเปลี่ยน หมดอายุ หรือถูกระงับ')
        conn.execute("UPDATE bank_flow SET status='payment_pending' WHERE number=?",(number,));audit(conn,number,actor,'payment_submitted')

# แอดมินบันทึกการตรวจเงินเข้าจริงและล็อกเริ่มงานจ่าย กันกดซ้ำ
def verify_payment(number,actor,reference):
    if not 3<=len(reference.strip())<=120:raise ValueError('ระบุเลขอ้างอิงเงินเข้าที่ตรวจจากธนาคาร')
    _change(number,actor,('payment_pending',),'payment_verified',payment_ref=reference.strip())

def start_payout(number,actor):_change(number,actor,('payment_verified',),'payout_processing')

# ปฏิเสธได้ก่อนรับชำระเท่านั้น ห้ามทำยอดเงินที่ร้านรับแล้วหายด้วยการยกเลิก
def reject(number,actor):_change(number,actor,('identity_pending','route_pending','identity_verified'),'rejected')

# ไม่สร้างเลขโอนเอง ต้องแนบภาพหลักฐานและเลขอ้างอิงที่แอดมินอ่านจากธนาคาร
def complete(number,actor,reference,source):
    row=get(number,actor)
    if row['status']!='payout_processing':raise ValueError('สถานะไม่ถูกต้อง')
    if not 3<=len(reference.strip())<=120:raise ValueError('ระบุเลขอ้างอิงการโอนจ่ายจริง')
    source=Path(source)
    if not source.is_file() or not 0<source.stat().st_size<=10*1024*1024:raise ValueError('ภาพต้องไม่เกิน 10 MB')
    with Image.open(source) as image:
        if image.format not in ('PNG','JPEG') or image.width*image.height>25000000:raise ValueError('ไฟล์ภาพไม่ถูกต้อง')
        image.verify()
    conn=db.getconnect();target=None
    try:
        conn.execute('BEGIN IMMEDIATE');_admin(conn,number,actor,('payout_processing',))
        from EXORA_identity import valid
        if not valid(conn,row['user_id'],row['recipient']):raise ValueError('กรุณายืนยันตัวตนใหม่ ข้อมูลเปลี่ยน หมดอายุ หรือถูกระงับ')
        folder=Path(db.BASE_DIR)/'EXORA_assets'/'payouts';folder.mkdir(parents=True,exist_ok=True)
        target=folder/(uuid.uuid4().hex+'.png')
        with Image.open(source) as image:image.convert('RGB').save(target,format='PNG')
        conn.execute("UPDATE bank_flow SET status='completed',payout_ref=?,payout_proof=? WHERE number=?",(reference.strip(),str(target.relative_to(db.BASE_DIR)),number))
        conn.execute("UPDATE transactions SET payment_status='approved',reviewed_by=?,reviewed_at=?,review_note=? WHERE transaction_no=? AND payment_status='pending'",(actor,datetime.now().isoformat(timespec='seconds'),'รับชำระและบันทึกการโอนจ่ายโดยเจ้าหน้าที่',number))
        audit(conn,number,actor,'completed',reference.strip());conn.commit()
    except Exception:
        conn.rollback()
        if target:target.unlink(missing_ok=True)
        raise
    finally:conn.close()

def _admin(conn,number,actor,allowed):
    access=role(conn,actor);row=conn.execute('SELECT user_id,status FROM bank_flow WHERE number=?',(number,)).fetchone()
    if not row:raise ValueError('ไม่พบรายการ')
    if access!='admin' or row[0]==actor:raise PermissionError('ให้แอดมินอีกบัญชีตรวจรายการนี้')
    if row[1] not in allowed:raise ValueError('สถานะไม่ถูกต้อง')

# การเปลี่ยนสถานะทั้งหมดต้องผ่านเจ้าของ/แอดมินและบันทึก audit
def _change(number,actor,allowed,state,owner=False,**fields):
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        if owner:
            role(conn,actor);row=conn.execute('SELECT user_id,status FROM bank_flow WHERE number=?',(number,)).fetchone()
            if not row or row[0]!=actor or row[1] not in allowed:raise PermissionError('เฉพาะเจ้าของรายการ')
        else:_admin(conn,number,actor,allowed)
        if state=='payout_processing':
            from EXORA_identity import valid
            user,name=conn.execute('SELECT user_id,recipient FROM bank_flow WHERE number=?',(number,)).fetchone()
            if not valid(conn,user,name):raise ValueError('กรุณายืนยันตัวตนใหม่ ข้อมูลเปลี่ยน หมดอายุ หรือถูกระงับ')
        if any(k not in ('identity_note','route_note','quote','payment_ref') for k in fields):raise ValueError('สถานะไม่ถูกต้อง')
        conn.execute('UPDATE bank_flow SET '+','.join(['status=?']+[k+'=?' for k in fields])+' WHERE number=?',(state,*fields.values(),number));audit(conn,number,actor,state);conn.commit()
    except Exception:conn.rollback();raise
    finally:conn.close()

# รับเฉพาะผลตรวจและเหตุผลจากชุดตัวเลือก บันทึกประวัติพร้อมเปลี่ยนสถานะ
REVIEW_REASONS=('ภาพเอกสารไม่ชัดเจน','เอกสารหมดอายุ','ข้อมูลเจ้าของบัญชีไม่ตรง','ข้อมูลบัญชีรับเงินไม่ครบ','ธนาคารไม่รองรับช่องทางนี้')
def review_choice(number,actor,decision,reason,checks,valid_until,expected_document_id):
    if decision not in ('ผ่าน','ขอข้อมูลเพิ่มเติม','ไม่ผ่าน') or reason not in REVIEW_REASONS:raise ValueError('เลือกผลตรวจและเหตุผลให้ถูกต้อง')
    if decision=='ผ่าน':
        verified=identity_status(number,actor)
        if checks.get('route') is not True:raise ValueError('กรุณายืนยันการตรวจช่องทางธนาคาร')
        if not verified and any(checks.get(k) is not True for k in ('document','holder')):raise ValueError('กรุณายืนยันการตรวจเอกสารและเจ้าของบัญชี')
        note='Document authenticity, expiry and account holder checked'
        route='Bank country, currency, beneficiary and net amount checked'
        row=get(number,actor)
        if row['status'] in ('identity_pending','route_pending','identity_verified','quote_pending_route'):
            return verify(number,actor,note,route,'document_review',valid_until,expected_document_id)
        return renew_identity(number,actor,note,'document_review',valid_until,expected_document_id)
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        _admin(conn,number,actor,('identity_pending','identity_verified','route_pending','quote_pending_route'))
        state='rejected' if decision=='ไม่ผ่าน' else conn.execute('SELECT status FROM bank_flow WHERE number=?',(number,)).fetchone()[0]
        conn.execute('UPDATE bank_flow SET status=?,feedback=? WHERE number=?',(state,decision+': '+reason,number))
        audit(conn,number,actor,'review_feedback',decision+': '+reason);conn.commit()
    except Exception:conn.rollback();raise
    finally:conn.close()

def timeline(number,actor):
    get(number,actor)
    conn=db.getconnect()
    try:return conn.execute('SELECT action,note,created_at FROM bank_flow_audit WHERE number=? ORDER BY id',(number,)).fetchall()
    finally:conn.close()
