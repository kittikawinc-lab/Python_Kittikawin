"""QR/bank transfer evidence with manual administrator review."""
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า datetime: datetime — จัดการวันที่ เวลา และเขตเวลา
# datetime: วันและเวลาของรายการและเอกสาร
from datetime import datetime
# คำอธิบาย import: นำเข้า math: math — คำนวณเส้นทางแอนิเมชัน และตรวจว่าตัวเลขเป็นค่าจำกัด
import math
# คำอธิบาย import: นำเข้า shutil: shutil — คัดลอกไฟล์หลักฐานและไฟล์ประกอบ
import shutil
# คำอธิบาย import: นำเข้า uuid: uuid — สร้างรหัสสุ่มสำหรับชื่อไฟล์ ลดการชนกันของชื่อ
import uuid
# คำอธิบาย import: นำเข้า Image: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
from PIL import Image
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db
# คำอธิบาย import: นำเข้า re: re — ตรวจรูปแบบข้อความด้วย regular expressions
import re

# คำอธิบาย def migrate: เพิ่มตารางหรือคอลัมน์ของโมดูลนี้ โดยรองรับฐานข้อมูลรุ่นเดิม
# รับค่า: conn
def migrate(conn):
    from EXORA_notifications import migrate as migrate_notifications
    migrate_notifications(conn)
    columns = {r[1] for r in conn.execute('PRAGMA table_info(transactions)')}
    additions = {'payment_status': "TEXT NOT NULL DEFAULT 'legacy'",
                 'slip_path': 'TEXT', 'reviewed_by': 'INTEGER',
                 'reviewed_at': 'TEXT', 'review_note': 'TEXT',
                 'payment_method': "TEXT NOT NULL DEFAULT 'legacy'",
                 'payer_bank':'TEXT','payer_name':'TEXT','payer_account':'TEXT',
                 'transfer_amount':'REAL','transfer_at':'TEXT','transfer_reference':'TEXT',
                 'recipient_bank':'TEXT','recipient_name':'TEXT','recipient_account':'TEXT','thb_value':'REAL'}
    for name, kind in additions.items():
        if name not in columns:
            conn.execute(f'ALTER TABLE transactions ADD COLUMN {name} {kind}')
    # คำอธิบาย import: นำเข้า migrate as migrate_profiles: EXORA_profiles — จัดการโปรไฟล์ ร้าน ผู้ใช้ และการคำนวณยอดแลกเงิน
    # migrate_profiles: ฟังก์ชันเตรียมตารางหรือคอลัมน์ของโมดูลที่อ้างอิง
    from EXORA_profiles import migrate as migrate_profiles
    migrate_profiles(conn)

# คำอธิบาย def _actor: ตรวจบัญชี active แล้วคืนสิทธิ์สำหรับการทำรายการ
# รับค่า: conn, user_id
def _actor(conn, user_id):
    row = conn.execute('SELECT role FROM users WHERE id=? AND status=?',
                       (user_id, 'active')).fetchone()
    if not row:
        raise PermissionError('บัญชีไม่พร้อมใช้งาน')
    return row[0]

# คำอธิบาย def _get: อ่านธุรกรรมและจำกัดการเข้าถึงตามเจ้าของหรือสิทธิ์ admin
# รับค่า: conn, number, actor_id
def _get(conn, number, actor_id):
    role = _actor(conn, actor_id)
    conn.row_factory = __import__('sqlite3').Row
    row = conn.execute('SELECT * FROM transactions WHERE transaction_no=?', (number,)).fetchone()
    if row is None:
        raise ValueError('ไม่พบรายการ')
    if role != 'admin' and row['user_id'] != actor_id:
        raise PermissionError('ไม่มีสิทธิ์ดูรายการนี้')
    return dict(row)

# คำอธิบาย def get_transaction: เปิดฐานข้อมูลเพื่ออ่านรายการที่ actor มีสิทธิ์ดู
# รับค่า: number, actor_id | เรียกใช้: db.getconnect
def get_transaction(number, actor_id):
    conn = db.getconnect()
    try:
        return _get(conn, number, actor_id)
    finally:
        conn.close()

# คำอธิบาย def submit: ตรวจหลักฐานและสลิปซ้ำ แล้วบันทึกรายการรอตรวจสอบแบบ atomic
# รับค่า: number, actor_id, data, source | เรียกใช้: db.getconnect
def submit(number,actor_id,data,source):
    payment=validate_payment(data);in_store=payment['payment_method']=='in_store'
    source=None if in_store else Path(source)
    if not in_store:
        if source.suffix.lower() not in {'.jpg','.jpeg','.png'} or not source.is_file() or not 0<source.stat().st_size<=10*1024*1024:raise ValueError('รองรับสลิป JPG/PNG ไม่เกิน 10 MB')
        with Image.open(source) as image:
            if image.format not in {'JPEG','PNG'}:raise ValueError('รูปแบบไฟล์ไม่ถูกต้อง')
            image.verify()
    for key in ('from_amount','to_amount','exchange_rate'):
        value=float(data[key])
        if not math.isfinite(value) or value<=0:raise ValueError('จำนวนเงินและอัตราไม่ถูกต้อง')
    if not 1<=len(str(data.get('customer_name','')).strip())<=80:raise ValueError('ชื่อลูกค้าต้องมี 1–80 ตัวอักษร')
    conn=db.getconnect();target=None
    try:
        conn.execute('BEGIN IMMEDIATE');_actor(conn,actor_id)
        from EXORA_security import consume_quote
        canonical=consume_quote(conn,actor_id,number,data)
        data={**data,**canonical}
        from EXORA_security import reserve_bank_reference
        reserve_bank_reference(conn,number,payment)
        phone=str(conn.execute('SELECT phone FROM users WHERE id=?',(actor_id,)).fetchone()[0] or '')
        if not re.fullmatch(r'[+\d ()-]{8,25}',phone) or not 8<=len(re.sub(r'\D','',phone))<=15:raise ValueError('กรุณาเพิ่มเบอร์โทรในโปรไฟล์ก่อนทำรายการ')
        if not in_store:
            directory=Path(db.BASE_DIR)/'EXORA_assets'/'slips';directory.mkdir(parents=True,exist_ok=True)
            target=directory/(uuid.uuid4().hex+source.suffix.lower());shutil.copyfile(source,target)
            with Image.open(target) as image:
                if image.format not in {'JPEG','PNG'} or image.width*image.height>25000000:raise ValueError('ภาพสลิปไม่ถูกต้องหรือใหญ่เกินกำหนด')
                image.verify()
            # ตรวจสลิปซ้ำภายใน transaction เดียวกันเพื่อป้องกันการส่งชนกัน
            from EXORA_slip_checks import check_and_record
            check_and_record(conn,number,target)
        conn.execute("""INSERT INTO transactions(transaction_no,user_id,transaction_type,from_currency,from_amount,to_currency,to_amount,exchange_rate,transaction_date,customer_name,customer_phone,payment_status,slip_path) VALUES (?,?,?,?,?,?,?,?,?,?,?,'pending',?)""",(number,actor_id,data['transaction_type'],data['from_currency'],data['from_amount'],data['to_currency'],data['to_amount'],data['exchange_rate'],datetime.now().isoformat(timespec='seconds'),data['customer_name'],phone,str(target.relative_to(db.BASE_DIR)) if target else None))
        value=data.get('thb_value')
        if data['from_currency']=='THB':value=data['from_amount']
        elif data['to_currency']=='THB':value=data['to_amount']
        if value is not None:
            value=float(value)
            if not math.isfinite(value) or value<=0:raise ValueError('มูลค่าเงินบาทไม่ถูกต้อง')
            conn.execute('UPDATE transactions SET thb_value=? WHERE transaction_no=?',(round(value,2),number))
        fields=list(payment);conn.execute('UPDATE transactions SET '+','.join(k+'=?' for k in fields)+' WHERE transaction_no=?',tuple(payment[k] for k in fields)+(number,))
        audit(conn,number,actor_id,'submitted');conn.commit()
    except Exception:
        conn.rollback()
        if target:target.unlink(missing_ok=True)
        raise
    finally:conn.close()

# คำอธิบาย def list_transactions: ค้นรายการตามสิทธิ์ โดยจำกัดเจ้าของในโหมดดูหน้าผู้ใช้
# รับค่า: actor_id, search, pending_only, own_only | เรียกใช้: db.getconnect
def list_transactions(actor_id, search='', pending_only=False, own_only=False):
    conn = db.getconnect()
    try:
        role = _actor(conn, actor_id)
        sql = '''SELECT t.transaction_no,u.username,t.transaction_type,t.from_currency,
            t.from_amount,t.to_currency,t.to_amount,t.exchange_rate,t.transaction_date,
            t.payment_status FROM transactions t LEFT JOIN users u ON u.id=t.user_id
            WHERE (t.transaction_no LIKE ? OR u.username LIKE ?)'''
        params = ['%' + search + '%'] * 2
        if role != 'admin' or own_only:
            sql += ' AND t.user_id=?'
            params.append(actor_id)
        if pending_only:
            if role != 'admin':
                raise PermissionError('เฉพาะ admin')
            sql += " AND t.payment_status='pending'"
        return conn.execute(sql + ' ORDER BY t.id DESC', params).fetchall()
    finally:
        conn.close()

# คำอธิบาย def review: ตรวจสิทธิ์ admin และเปลี่ยนรายการ pending เป็น approved/rejected
# รับค่า: number, actor_id, status, note | เรียกใช้: db.getconnect
def review(number, actor_id, status, note=''):
    if status not in {'approved', 'rejected'}:
        raise ValueError('สถานะไม่ถูกต้อง')
    if len(note)>500:raise ValueError('หมายเหตุต้องไม่เกิน 500 ตัวอักษร')
    if status == 'rejected' and not note.strip():
        raise ValueError('กรุณาระบุเหตุผลที่ปฏิเสธ')
    conn = db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        if _actor(conn, actor_id) != 'admin':
            raise PermissionError('เฉพาะ admin สามารถตรวจสอบสลิปได้')
        row = _get(conn, number, actor_id)
        if row['user_id']==actor_id:raise PermissionError('แอดมินไม่สามารถอนุมัติหรือปฏิเสธรายการของตัวเอง')
        if row['payment_status'] != 'pending':
            raise ValueError('รายการนี้ได้รับการตรวจสอบแล้ว')
        path = Path(db.BASE_DIR) / (row['slip_path'] or '')
        if row.get('payment_method')!='in_store' and (not row['slip_path'] or not path.is_file()):
            raise ValueError('ไม่พบไฟล์สลิป')
        conn.execute('''UPDATE transactions SET payment_status=?,reviewed_by=?,
            reviewed_at=?,review_note=? WHERE transaction_no=? AND payment_status='pending' ''',
            (status, actor_id, datetime.now().isoformat(timespec='seconds'), note.strip(), number))
        audit(conn,number,actor_id,status,note.strip())
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# คำอธิบาย def audit: บันทึกผู้กระทำ เหตุการณ์ และเวลาในการตรวจหลักฐาน
# รับค่า: conn, number, actor_id, action, note
def audit(conn, number, actor_id, action, note=''):
    cursor=conn.execute('INSERT INTO payment_audit(transaction_no,actor_id,action,note,created_at) VALUES (?,?,?,?,?)',
        (number,actor_id,action,note,datetime.now().isoformat(timespec='seconds')))
    if action in ('submitted','resubmitted'):
        from EXORA_notifications import enqueue
        enqueue(conn,cursor.lastrowid,number)

# คำอธิบาย def get_audit: อ่านประวัติการตรวจสอบของรายการที่ actor มีสิทธิ์เข้าถึง
# รับค่า: number, actor_id | เรียกใช้: db.getconnect
def get_audit(number, actor_id):
    conn=db.getconnect()
    try:
        _get(conn,number,actor_id)
        return [dict(r) for r in conn.execute('SELECT action,note,created_at FROM payment_audit WHERE transaction_no=? ORDER BY id',(number,))]
    finally: conn.close()

# คำอธิบาย def slip_path: ตรวจว่าพาธสลิปอยู่ในโฟลเดอร์หลักฐานและไฟล์ยังมีอยู่
# รับค่า: row
def slip_path(row):
    if not row.get('slip_path'): raise ValueError('รายการนี้ไม่มีสลิป')
    base=Path(db.BASE_DIR).resolve(); path=(base/row['slip_path']).resolve()
    if not path.is_relative_to(base/'EXORA_assets'/'slips') or not path.is_file():
        raise ValueError('ไม่พบไฟล์สลิป')
    return path

# คำอธิบาย def replace_slip: ตรวจสิทธิ์เจ้าของและสลิปซ้ำ แล้วแทนหลักฐานของรายการ rejected
# รับค่า: number, actor_id, source | เรียกใช้: db.getconnect
def replace_slip(number, actor_id, source):
    source=Path(source)
    if source.suffix.lower() not in {'.jpg','.jpeg','.png'} or not source.is_file() or not 0<source.stat().st_size<=10*1024*1024:
        raise ValueError('รองรับ JPG/PNG ไม่เกิน 10 MB')
    with Image.open(source) as image:
        if image.format not in {'JPEG','PNG'}: raise ValueError('ไฟล์ภาพไม่ถูกต้อง')
        image.verify()
    conn=db.getconnect(); target=None
    try:
        conn.execute('BEGIN IMMEDIATE'); row=_get(conn,number,actor_id)
        if row['user_id']!=actor_id: raise PermissionError('เฉพาะเจ้าของรายการ')
        if row['payment_status']!='rejected': raise ValueError('แนบใหม่ได้เฉพาะรายการปฏิเสธ')
        directory=Path(db.BASE_DIR)/'EXORA_assets'/'slips'; directory.mkdir(parents=True,exist_ok=True)
        target=directory/(uuid.uuid4().hex+source.suffix.lower()); shutil.copyfile(source,target)
        with Image.open(target) as image:
            if image.format not in {'JPEG','PNG'} or image.width*image.height>25000000:raise ValueError('ภาพสลิปไม่ถูกต้องหรือใหญ่เกินกำหนด')
            image.verify()
        # คำอธิบาย import: นำเข้า check_and_record: EXORA_slip_checks — ตรวจไฟล์และภาพสลิปที่ซ้ำกับรายการอื่น
        # check_and_record: ฟังก์ชันตรวจสลิปซ้ำกับรายการอื่นและบันทึกแฮช
        from EXORA_slip_checks import check_and_record
        check_and_record(conn,number,target)
        conn.execute("UPDATE transactions SET slip_path=?,payment_status='pending',reviewed_by=NULL,reviewed_at=NULL,review_note=NULL WHERE transaction_no=?",(str(target.relative_to(db.BASE_DIR)),number))
        audit(conn,number,actor_id,'resubmitted'); conn.commit()
    except Exception:
        conn.rollback()
        if target: target.unlink(missing_ok=True)
        raise
    finally: conn.close()

# คำอธิบาย def validate_payment: ตรวจข้อมูล QR/ธนาคารและจัดรูปแบบข้อมูลชำระเงินก่อนบันทึก
# รับค่า: data
def validate_payment(data):
    method=data.get('payment_method','qr')
    if method=='card':raise ValueError('ช่องทางบัตรยังไม่เปิดบริการ ต้องตั้งผู้ให้บริการก่อน')
    if method=='in_store':
        if data.get('from_currency')=='THB':raise ValueError('ช่องทางนี้สำหรับส่งมอบเงินต่างประเทศที่ร้าน')
        return {'payment_method':'in_store'}
    if method not in {'qr','bank'}:raise ValueError('กรุณาเลือกวิธีชำระเงินที่เปิดบริการ')
    result={'payment_method':method}
    if method=='qr': return result
    for key,label in [('payer_bank','ธนาคารผู้โอน'),('payer_name','ชื่อบัญชีผู้โอน'),('payer_account','เลขบัญชีผู้โอน'),('transfer_at','วันเวลาที่โอน')]:
        value=str(data.get(key,'')).strip()
        if not value or len(value)>120: raise ValueError('กรุณากรอก'+label)
        result[key]=value
    result['payer_account']=re.sub(r'[ -]','',result['payer_account'])
    if not re.fullmatch(r'[0-9]{6,20}',result['payer_account']): raise ValueError('เลขบัญชีผู้โอนต้องมี 6–20 หลัก')
    try:
        datetime.strptime(result['transfer_at'],'%Y-%m-%d %H:%M')
    except ValueError: raise ValueError('วันเวลาโอนใช้รูปแบบ YYYY-MM-DD HH:MM')
    try: amount=float(data.get('transfer_amount',''))
    except (TypeError,ValueError): raise ValueError('กรุณากรอกจำนวนเงินที่โอนเป็นบาท')
    if not math.isfinite(amount) or not 0<amount<=1e9: raise ValueError('จำนวนเงินที่โอนต้องมากกว่า 0')
    result['transfer_amount']=round(amount,2)
    if result['transfer_amount']<=0: raise ValueError('จำนวนเงินที่โอนน้อยเกินไป')
    if data.get('from_currency')=='THB' and abs(result['transfer_amount']-float(data['from_amount']))>.01:raise ValueError('ยอดโอนต้องตรงกับยอด THB ของรายการ')
    reference=str(data.get('transfer_reference','')).strip()
    if len(reference)>120: raise ValueError('เลขอ้างอิงยาวเกินไป')
    result['transfer_reference']=reference
    # คำอธิบาย import: นำเข้า shop: EXORA_profiles — จัดการโปรไฟล์ ร้าน ผู้ใช้ และการคำนวณยอดแลกเงิน
    from EXORA_profiles import shop
    settings=shop()
    for key,shopkey in [('recipient_bank','bank_name'),('recipient_name','bank_account_name'),('recipient_account','bank_account_number')]:
        value=settings.get(shopkey,'').strip()
        if not value: raise ValueError('ให้ admin ตั้งค่าบัญชีธนาคารรับเงินของร้านก่อนใช้งานวิธีนี้')
        result[key]=value
    return result
