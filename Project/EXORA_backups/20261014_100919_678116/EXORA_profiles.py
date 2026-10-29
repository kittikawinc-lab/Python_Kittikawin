"""Native desktop profile, store preferences and accurate currency quotes."""
from pathlib import Path
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
import uuid
import sqlite3
import hmac
from PIL import Image, ImageOps
import EXORA_database as db

def migrate(conn):
    from EXORA_news import migrate as migrate_news
    migrate_news(conn)
    from EXORA_auth import migrate as migrate_auth
    migrate_auth(conn)
    users={r[1] for r in conn.execute('PRAGMA table_info(users)')}
    for name in ('display_name','phone','bio','avatar_path','accent'):
        if name not in users: conn.execute(f'ALTER TABLE users ADD COLUMN {name} TEXT')
    conn.execute('''CREATE TABLE IF NOT EXISTS payment_audit(id INTEGER PRIMARY KEY AUTOINCREMENT,transaction_no TEXT NOT NULL,actor_id INTEGER NOT NULL,action TEXT NOT NULL,note TEXT,created_at TEXT NOT NULL)''')
    conn.execute('CREATE TABLE IF NOT EXISTS shop_settings(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
    conn.execute('''CREATE TABLE IF NOT EXISTS email_log(id INTEGER PRIMARY KEY AUTOINCREMENT,transaction_no TEXT,actor_id INTEGER,recipient TEXT,status TEXT,created_at TEXT)''')
    conn.executemany('INSERT OR IGNORE INTO shop_settings(key,value) VALUES (?,?)',
        {'name':'EXORA','tagline':'A better exchange. A brighter journey.','phone':'','address':'','hours':'','accent':'#125b4a',
         'payment_note':'ตรวจสอบชื่อผู้รับและยอดเงินก่อนโอน แนบหลักฐานเพื่อให้เจ้าหน้าที่ตรวจสอบ',
         'bank_name':'','bank_account_name':'','bank_account_number':''}.items())
    conn.execute("UPDATE shop_settings SET value=? WHERE key='payment_note' AND value=?",
        ('ตรวจสอบชื่อผู้รับและยอดเงินก่อนโอน แนบหลักฐานเพื่อให้เจ้าหน้าที่ตรวจสอบ',
         'QR เป็นภาพตัวอย่าง ไม่สามารถใช้ชำระเงินจริงได้ กรุณาติดต่อร้านก่อนโอนเงิน'))

def quote(from_currency,to_currency,amount):
    try: amount=Decimal(str(amount))
    except InvalidOperation: raise ValueError('จำนวนเงินไม่ถูกต้อง')
    if not amount.is_finite() or not 0<amount<=Decimal('1000000000'): raise ValueError('จำนวนเงินต้องมากกว่า 0 และไม่เกิน 1,000,000,000')
    if from_currency==to_currency: raise ValueError('กรุณาเลือกสกุลเงินต่างกัน')
    source,target=db.getcur(from_currency),db.getcur(to_currency)
    if not source or not target: raise ValueError('ไม่พบสกุลเงิน')
    buy=Decimal('1') if from_currency=='THB' else Decimal(str(source[3]))
    sell=Decimal('1') if to_currency=='THB' else Decimal(str(target[4]))
    if not buy.is_finite() or not sell.is_finite() or buy<=0 or sell<=0: raise ValueError('ร้านยังไม่ได้ตั้งอัตราสำหรับสกุลเงินนี้')
    amount=amount.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    result=(amount*buy/sell).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    if amount<=0 or result<=0: raise ValueError('จำนวนเงินน้อยเกินไป')
    return {'from_currency':from_currency,'to_currency':to_currency,'from_amount':float(amount),'to_amount':float(result),'exchange_rate':float(buy/sell),'transaction_type':'SELL' if from_currency=='THB' else 'BUY'}

def get_profile(user_id):
    conn=db.getconnect()
    try:
        conn.row_factory=sqlite3.Row
        row=conn.execute("SELECT * FROM users WHERE id=? AND status='active'",(user_id,)).fetchone()
        if not row: raise ValueError('บัญชีไม่พร้อมใช้งาน')
        profile=dict(row); profile.pop('password',None); return profile
    finally: conn.close()

def save_profile(user_id,display_name,email,phone,bio,accent,avatar_source=None):
    if not display_name.strip() or len(display_name)>80 or len(bio)>400 or len(phone)>25: raise ValueError('กรุณาตรวจสอบชื่อ เบอร์โทร และข้อความแนะนำ')
    email=email.strip().lower()
    if email and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email): raise ValueError('อีเมลไม่ถูกต้อง')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',accent): raise ValueError('สีไม่ถูกต้อง')
    conn=db.getconnect(); target=None
    try:
        conn.execute('BEGIN IMMEDIATE')
        row=conn.execute("SELECT avatar_path FROM users WHERE id=? AND status='active'",(user_id,)).fetchone()
        if not row: raise ValueError('บัญชีไม่พร้อมใช้งาน')
        if email and conn.execute('SELECT 1 FROM users WHERE lower(email)=? AND id!=?',(email,user_id)).fetchone(): raise ValueError('อีเมลนี้ถูกใช้แล้ว')
        avatar=row[0]
        if avatar_source:
            source=Path(avatar_source)
            if not source.is_file() or not 0<source.stat().st_size<=10*1024*1024: raise ValueError('รูปต้องไม่เกิน 10 MB')
            with Image.open(source) as image:
                if image.format not in {'JPEG','PNG'} or image.width*image.height>25000000: raise ValueError('รองรับ JPG/PNG ไม่เกิน 25 ล้านพิกเซล')
                image.load(); image=ImageOps.exif_transpose(image).convert('RGB'); image.thumbnail((400,400))
                directory=Path(db.BASE_DIR)/'EXORA_assets'/'avatars'; directory.mkdir(parents=True,exist_ok=True)
                target=directory/(uuid.uuid4().hex+'.jpg'); image.save(target,quality=90); avatar=str(target.relative_to(db.BASE_DIR))
        conn.execute('UPDATE users SET display_name=?,email=?,phone=?,bio=?,accent=?,avatar_path=? WHERE id=?',
            (display_name.strip(),email or None,phone.strip(),bio.strip(),accent,avatar,user_id)); conn.commit()
    except Exception:
        conn.rollback()
        if target: target.unlink(missing_ok=True)
        raise
    finally: conn.close()

def change_password(user_id,current,new):
    if len(new)<8: raise ValueError('รหัสผ่านใหม่อย่างน้อย 8 ตัว')
    conn=db.getconnect()
    try:
        row=conn.execute('SELECT password FROM users WHERE id=?',(user_id,)).fetchone()
        if not row or not hmac.compare_digest(row[0],db.hashp(current)): raise ValueError('รหัสผ่านปัจจุบันไม่ถูกต้อง')
        conn.execute('UPDATE users SET password=? WHERE id=?',(db.hashp(new),user_id)); conn.commit()
    finally: conn.close()

def shop():
    conn=db.getconnect()
    try: return dict(conn.execute('SELECT key,value FROM shop_settings').fetchall())
    finally: conn.close()

def save_shop(actor_id,values):
    conn=db.getconnect()
    try:
        actor=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor_id,)).fetchone()
        if not actor or actor[0]!='admin': raise PermissionError('เฉพาะ admin')
        if not values.get('name','').strip(): raise ValueError('กรุณาระบุชื่อร้าน')
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',values.get('accent','')): raise ValueError('สีไม่ถูกต้อง')
        bank_values=[str(values.get(key,'')).strip() for key in ('bank_name','bank_account_name','bank_account_number')]
        if any(bank_values) and not all(bank_values): raise ValueError('กรอกธนาคาร ชื่อบัญชี และเลขบัญชีร้านให้ครบ หรือเว้นว่างทั้งสามช่อง')
        if bank_values[2] and not re.fullmatch(r'[\d -]{6,30}',bank_values[2]): raise ValueError('เลขบัญชีร้านไม่ถูกต้อง')
        for key in ('name','tagline','phone','address','hours','accent','payment_note','bank_name','bank_account_name','bank_account_number'):
            if key not in values: continue
            value=values[key].strip()
            if len(value)>500: raise ValueError('ข้อความยาวเกินไป')
            conn.execute('INSERT OR REPLACE INTO shop_settings(key,value) VALUES (?,?)',(key,value))
        conn.commit()
    finally: conn.close()

def set_rate(actor_id,code,name,buy,sell):
    conn=db.getconnect()
    try:
        actor=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor_id,)).fetchone()
        if not actor or actor[0]!='admin': raise PermissionError('เฉพาะ admin')
        code=code.strip().upper()
        if not re.fullmatch(r'[A-Z]{3}',code) or not name.strip(): raise ValueError('กรุณาตรวจสอบชื่อและรหัสสกุลเงิน')
        buy,sell=Decimal(str(buy)),Decimal(str(sell))
        if not buy.is_finite() or not sell.is_finite() or buy<=0 or sell<buy: raise ValueError('อัตราต้องมากกว่า 0 และราคาขายไม่น้อยกว่ารับซื้อ')
        if code=='THB': buy=sell=Decimal('1')
        conn.execute('''INSERT INTO currencies(currency_code,currency_name,buy_rate,sell_rate,updated_at) VALUES (?,?,?,?,datetime('now','localtime')) ON CONFLICT(currency_code) DO UPDATE SET currency_name=excluded.currency_name,buy_rate=excluded.buy_rate,sell_rate=excluded.sell_rate,updated_at=excluded.updated_at''',(code,name.strip(),float(buy),float(sell))); conn.commit()
    finally: conn.close()

def list_users(actor_id):
    conn=db.getconnect()
    try:
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor_id,)).fetchone()!=('admin',): raise PermissionError('เฉพาะ admin')
        return conn.execute('SELECT id,username,email,role,status FROM users ORDER BY id').fetchall()
    finally: conn.close()

def update_user(actor_id,user_id,role,status):
    if role not in {'user','staff','admin'} or status not in {'active','inactive'}: raise ValueError('สิทธิ์หรือสถานะไม่ถูกต้อง')
    if actor_id==user_id and (role!='admin' or status!='active'): raise ValueError('ไม่สามารถปิดสิทธิ์ admin ของตัวเอง')
    conn=db.getconnect()
    try:
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor_id,)).fetchone()!=('admin',): raise PermissionError('เฉพาะ admin')
        conn.execute('UPDATE users SET role=?,status=? WHERE id=?',(role,status,user_id)); conn.commit()
    finally: conn.close()
