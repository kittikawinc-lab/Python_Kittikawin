"""QR/bank transfer evidence with manual administrator review."""
from pathlib import Path
from datetime import datetime
import math
import shutil
import uuid
from PIL import Image
import EXORA_database as db
import re

def migrate(conn):
    columns = {r[1] for r in conn.execute('PRAGMA table_info(transactions)')}
    additions = {'payment_status': "TEXT NOT NULL DEFAULT 'legacy'",
                 'slip_path': 'TEXT', 'reviewed_by': 'INTEGER',
                 'reviewed_at': 'TEXT', 'review_note': 'TEXT',
                 'payment_method': "TEXT NOT NULL DEFAULT 'legacy'",
                 'payer_bank':'TEXT','payer_name':'TEXT','payer_account':'TEXT',
                 'transfer_amount':'REAL','transfer_at':'TEXT','transfer_reference':'TEXT',
                 'recipient_bank':'TEXT','recipient_name':'TEXT','recipient_account':'TEXT'}
    for name, kind in additions.items():
        if name not in columns:
            conn.execute(f'ALTER TABLE transactions ADD COLUMN {name} {kind}')
    from EXORA_profiles import migrate as migrate_profiles
    migrate_profiles(conn)

def _actor(conn, user_id):
    row = conn.execute('SELECT role FROM users WHERE id=? AND status=?',
                       (user_id, 'active')).fetchone()
    if not row:
        raise PermissionError('บัญชีไม่พร้อมใช้งาน')
    return row[0]

def _get(conn, number, actor_id):
    role = _actor(conn, actor_id)
    conn.row_factory = __import__('sqlite3').Row
    row = conn.execute('SELECT * FROM transactions WHERE transaction_no=?', (number,)).fetchone()
    if row is None:
        raise ValueError('ไม่พบรายการ')
    if role != 'admin' and row['user_id'] != actor_id:
        raise PermissionError('ไม่มีสิทธิ์ดูรายการนี้')
    return dict(row)

def get_transaction(number, actor_id):
    conn = db.getconnect()
    try:
        return _get(conn, number, actor_id)
    finally:
        conn.close()

def submit(number, actor_id, data, source):
    payment = validate_payment(data)
    source = Path(source)
    if source.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
        raise ValueError('รองรับสลิป JPG และ PNG เท่านั้น')
    if not source.is_file() or not 0 < source.stat().st_size <= 10 * 1024 * 1024:
        raise ValueError('ไฟล์สลิปต้องมีขนาดไม่เกิน 10 MB')
    with Image.open(source) as image:
        if image.format not in {'JPEG', 'PNG'}:
            raise ValueError('รูปแบบไฟล์ไม่ถูกต้อง')
        image.verify()
    for key in ('from_amount', 'to_amount', 'exchange_rate'):
        value = float(data[key])
        if not math.isfinite(value) or value <= 0:
            raise ValueError('จำนวนเงินและอัตราต้องมากกว่า 0 และเป็นตัวเลขที่ถูกต้อง')
    directory = Path(db.BASE_DIR) / 'EXORA_assets' / 'slips'
    if not str(data.get('customer_name','')).strip():
        raise ValueError('กรุณากรอกชื่อลูกค้า')
    if not re.fullmatch(r'[+\d ()-]{8,25}',str(data.get('customer_phone',''))):
        raise ValueError('เบอร์โทรไม่ถูกต้อง')
    conn = db.getconnect()
    target = None
    try:
        conn.execute('BEGIN IMMEDIATE')
        _actor(conn, actor_id)
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (uuid.uuid4().hex + source.suffix.lower())
        shutil.copyfile(source, target)
        conn.execute('''INSERT INTO transactions
            (transaction_no,user_id,transaction_type,from_currency,from_amount,
             to_currency,to_amount,exchange_rate,transaction_date,customer_name,
             customer_phone,payment_status,slip_path)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,'pending',?)''',
            (number, actor_id, data['transaction_type'], data['from_currency'],
             data['from_amount'], data['to_currency'], data['to_amount'],
             data['exchange_rate'], datetime.now().isoformat(timespec='seconds'),
             data['customer_name'], data['customer_phone'], str(target.relative_to(db.BASE_DIR))))
        fields=list(payment)
        conn.execute('UPDATE transactions SET '+','.join(key+'=?' for key in fields)+' WHERE transaction_no=?',
                     tuple(payment[key] for key in fields)+(number,))
        audit(conn,number,actor_id,'submitted')
        conn.commit()
    except Exception:
        conn.rollback()
        if target is not None:
            target.unlink(missing_ok=True)
        raise
    finally:
        conn.close()

def list_transactions(actor_id, search='', pending_only=False):
    conn = db.getconnect()
    try:
        role = _actor(conn, actor_id)
        sql = '''SELECT t.transaction_no,u.username,t.transaction_type,t.from_currency,
            t.from_amount,t.to_currency,t.to_amount,t.exchange_rate,t.transaction_date,
            t.payment_status FROM transactions t LEFT JOIN users u ON u.id=t.user_id
            WHERE (t.transaction_no LIKE ? OR u.username LIKE ?)'''
        params = ['%' + search + '%'] * 2
        if role != 'admin':
            sql += ' AND t.user_id=?'
            params.append(actor_id)
        if pending_only:
            if role != 'admin':
                raise PermissionError('เฉพาะ admin')
            sql += " AND t.payment_status='pending'"
        return conn.execute(sql + ' ORDER BY t.id DESC', params).fetchall()
    finally:
        conn.close()

def review(number, actor_id, status, note=''):
    if status not in {'approved', 'rejected'}:
        raise ValueError('สถานะไม่ถูกต้อง')
    if status == 'rejected' and not note.strip():
        raise ValueError('กรุณาระบุเหตุผลที่ปฏิเสธ')
    conn = db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        if _actor(conn, actor_id) != 'admin':
            raise PermissionError('เฉพาะ admin สามารถตรวจสอบสลิปได้')
        row = _get(conn, number, actor_id)
        if row['payment_status'] != 'pending':
            raise ValueError('รายการนี้ได้รับการตรวจสอบแล้ว')
        path = Path(db.BASE_DIR) / (row['slip_path'] or '')
        if not row['slip_path'] or not path.is_file():
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

def audit(conn, number, actor_id, action, note=''):
    conn.execute('INSERT INTO payment_audit(transaction_no,actor_id,action,note,created_at) VALUES (?,?,?,?,?)',
        (number,actor_id,action,note,datetime.now().isoformat(timespec='seconds')))

def get_audit(number, actor_id):
    conn=db.getconnect()
    try:
        _get(conn,number,actor_id)
        return [dict(r) for r in conn.execute('SELECT action,note,created_at FROM payment_audit WHERE transaction_no=? ORDER BY id',(number,))]
    finally: conn.close()

def slip_path(row):
    if not row.get('slip_path'): raise ValueError('รายการนี้ไม่มีสลิป')
    base=Path(db.BASE_DIR).resolve(); path=(base/row['slip_path']).resolve()
    if not path.is_relative_to(base/'EXORA_assets'/'slips') or not path.is_file():
        raise ValueError('ไม่พบไฟล์สลิป')
    return path

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
        conn.execute("UPDATE transactions SET slip_path=?,payment_status='pending',reviewed_by=NULL,reviewed_at=NULL,review_note=NULL WHERE transaction_no=?",(str(target.relative_to(db.BASE_DIR)),number))
        audit(conn,number,actor_id,'resubmitted'); conn.commit()
    except Exception:
        conn.rollback()
        if target: target.unlink(missing_ok=True)
        raise
    finally: conn.close()

def validate_payment(data):
    method=data.get('payment_method','qr')
    if method not in {'qr','bank'}: raise ValueError('กรุณาเลือก QR หรือโอนบัญชีธนาคาร')
    result={'payment_method':method}
    if method=='qr': return result
    for key,label in [('payer_bank','ธนาคารผู้โอน'),('payer_name','ชื่อบัญชีผู้โอน'),('payer_account','เลขบัญชีผู้โอน'),('transfer_at','วันเวลาที่โอน')]:
        value=str(data.get(key,'')).strip()
        if not value or len(value)>120: raise ValueError('กรุณากรอก'+label)
        result[key]=value
    result['payer_account']=re.sub(r'[ -]','',result['payer_account'])
    if not re.fullmatch(r'\d{6,20}',result['payer_account']): raise ValueError('เลขบัญชีผู้โอนต้องมี 6–20 หลัก')
    try:
        datetime.strptime(result['transfer_at'],'%Y-%m-%d %H:%M')
    except ValueError: raise ValueError('วันเวลาโอนใช้รูปแบบ YYYY-MM-DD HH:MM')
    try: amount=float(data.get('transfer_amount',''))
    except (TypeError,ValueError): raise ValueError('กรุณากรอกจำนวนเงินที่โอนเป็นบาท')
    if not math.isfinite(amount) or not 0<amount<=1e9: raise ValueError('จำนวนเงินที่โอนต้องมากกว่า 0')
    result['transfer_amount']=round(amount,2)
    if result['transfer_amount']<=0: raise ValueError('จำนวนเงินที่โอนน้อยเกินไป')
    reference=str(data.get('transfer_reference','')).strip()
    if len(reference)>120: raise ValueError('เลขอ้างอิงยาวเกินไป')
    result['transfer_reference']=reference
    from EXORA_profiles import shop
    settings=shop()
    for key,shopkey in [('recipient_bank','bank_name'),('recipient_name','bank_account_name'),('recipient_account','bank_account_number')]:
        value=settings.get(shopkey,'').strip()
        if not value: raise ValueError('ให้ admin ตั้งค่าบัญชีธนาคารรับเงินของร้านก่อนใช้งานวิธีนี้')
        result[key]=value
    return result
