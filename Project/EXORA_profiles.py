"""Native desktop profile, store preferences and accurate currency quotes."""
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า Decimal, InvalidOperation, ROUND_HALF_UP: decimal — คำนวณและปัดเศษยอดเงินด้วย Decimal
# Decimal: ตัวเลขทศนิยมสำหรับคำนวณยอดเงิน
# InvalidOperation: ข้อผิดพลาดเมื่อแปลงหรือคำนวณ Decimal ไม่ได้
# ROUND_HALF_UP: วิธีปัดเศษครึ่งขึ้นสำหรับจำนวนเงิน
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
# คำอธิบาย import: นำเข้า re: re — ตรวจรูปแบบข้อความด้วย regular expressions
import re
# คำอธิบาย import: นำเข้า uuid: uuid — สร้างรหัสสุ่มสำหรับชื่อไฟล์ ลดการชนกันของชื่อ
import uuid
# คำอธิบาย import: นำเข้า sqlite3: sqlite3 — เชื่อมต่อ อ่าน และบันทึกฐานข้อมูล SQLite
import sqlite3
# คำอธิบาย import: นำเข้า hmac: hmac — เปรียบเทียบค่าแฮชด้วย compare_digest
import hmac
# คำอธิบาย import: นำเข้า Image, ImageOps: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
# ImageOps: ปรับทิศทางภาพและย่อภาพให้พอดีกรอบ
from PIL import Image, ImageOps
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db

# คำอธิบาย def migrate: เพิ่มตารางหรือคอลัมน์ของโมดูลนี้ โดยรองรับฐานข้อมูลรุ่นเดิม
# รับค่า: conn
def migrate(conn):
    from EXORA_saved_accounts import migrate as migrate_accounts
    migrate_accounts(conn)
    from EXORA_bank_flow import migrate as migrate_bank_flow
    migrate_bank_flow(conn)
    # เตรียมประวัติการเปลี่ยนอัตราและรายการโปรดของผู้ใช้
    from EXORA_currency_cards import migrate as migrate_cards
    migrate_cards(conn)
    # คำอธิบาย import: นำเข้า migrate as migrate_news: EXORA_news — จัดเก็บและจัดการภาพข่าว รวมตัวควบคุมการเลื่อนสไลด์
    # migrate_news: ฟังก์ชันเตรียมตารางหรือคอลัมน์ของโมดูลที่อ้างอิง
    from EXORA_news import migrate as migrate_news
    migrate_news(conn)
    # คำอธิบาย import: นำเข้า migrate as migrate_auth: EXORA_auth — สร้าง ตรวจสอบ OTP และตั้งรหัสผ่านใหม่
    # migrate_auth: ฟังก์ชันเตรียมตารางหรือคอลัมน์ของโมดูลที่อ้างอิง
    from EXORA_auth import migrate as migrate_auth
    migrate_auth(conn)
    users={r[1] for r in conn.execute('PRAGMA table_info(users)')}
    if 'language' not in users:conn.execute("ALTER TABLE users ADD COLUMN language TEXT NOT NULL DEFAULT 'th'")
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

# คำอธิบาย def quote: คำนวณแลกเงินผ่าน THB ด้วยราคาซื้อ–ขายและปัดยอดเป็นสองตำแหน่ง
# รับค่า: from_currency, to_currency, amount | เรียกใช้: db.getcur
def quote(from_currency,to_currency,amount,actor_id=None):
    from EXORA_security import issue_quote
    conn=db.getconnect()
    try:return issue_quote(conn,from_currency,to_currency,amount,actor_id)
    finally:conn.close()

# คำอธิบาย def get_profile: อ่านโปรไฟล์บัญชี active โดยไม่นำรหัสผ่านออกไป
# รับค่า: user_id | เรียกใช้: db.getconnect
def get_profile(user_id):
    conn=db.getconnect()
    try:
        conn.row_factory=sqlite3.Row
        row=conn.execute("SELECT * FROM users WHERE id=? AND status='active'",(user_id,)).fetchone()
        if not row: raise ValueError('บัญชีไม่พร้อมใช้งาน')
        profile=dict(row); profile.pop('password',None); return profile
    finally: conn.close()

# คำอธิบาย def save_profile: ตรวจข้อมูลและภาพโปรไฟล์ แล้วบันทึกการแก้ไข
# รับค่า: user_id, display_name, email, phone, bio, accent, avatar_source | เรียกใช้: db.getconnect
def save_profile(user_id,display_name,email,phone,bio,accent,avatar_source=None):
    if not display_name.strip() or len(display_name)>80 or len(bio)>400 or len(phone)>25: raise ValueError('กรุณาตรวจสอบชื่อ เบอร์โทร และข้อความแนะนำ')
    email=email.strip().lower()
    if phone and (not re.fullmatch(r'[+\d ()-]{8,25}',phone) or not 8<=len(re.sub(r'\D','',phone))<=15):raise ValueError('เบอร์โทรไม่ถูกต้อง')
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

# คำอธิบาย def change_password: ตรวจรหัสผ่านปัจจุบันและบันทึกรหัสผ่านใหม่
# รับค่า: user_id, current, new | เรียกใช้: db.getconnect, db.hashp
# บันทึกภาษาของบัญชีตัวเองโดยไม่เปลี่ยนข้อมูลโปรไฟล์หรือสิทธิ์
def save_language(user_id,language):
    if language not in ('th','en','zh'):raise ValueError('ภาษาไม่ถูกต้อง')
    conn=db.getconnect()
    try:
        if conn.execute("UPDATE users SET language=? WHERE id=? AND status='active'",(language,user_id)).rowcount!=1:raise PermissionError('บัญชีไม่พร้อมใช้งาน')
        conn.commit()
    finally:conn.close()

# ตรวจรหัสผ่านเดิมและบันทึกรหัสผ่านใหม่แบบเข้ารหัส
def change_password(user_id,current,new):
    from EXORA_security import validate_new_password
    validate_new_password(new)
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        row=conn.execute("SELECT password,role FROM users WHERE id=? AND status='active'",(user_id,)).fetchone()
        from EXORA_security import password_matches
        if not row or not password_matches(current,row[0]):raise ValueError('รหัสผ่านปัจจุบันไม่ถูกต้อง')
        if row[1]=='admin' and new=='admin123':raise ValueError('กรุณาใช้รหัสผ่านใหม่ที่ไม่ใช่รหัสเริ่มต้น')
        conn.execute('UPDATE users SET password=? WHERE id=?',(db.hashp(new),user_id))
        from EXORA_security import clear_login_limit
        clear_login_limit(conn,user_id);conn.commit()
    finally: conn.close()

# คำอธิบาย def shop: อ่านการตั้งค่าร้านเป็นพจนานุกรม
# รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: db.getconnect
def shop():
    conn=db.getconnect()
    try: return dict(conn.execute('SELECT key,value FROM shop_settings').fetchall())
    finally: conn.close()

# คำอธิบาย def save_shop: ตรวจสิทธิ์และความถูกต้อง แล้วบันทึกการตั้งค่าร้าน
# รับค่า: actor_id, values | เรียกใช้: db.getconnect
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
        currency=values.get('bank_receiving_currency','THB').strip().upper()
        if not conn.execute('SELECT 1 FROM currencies WHERE currency_code=?',(currency,)).fetchone():raise ValueError('ไม่พบสกุลเงิน')
        for key in ('name','tagline','phone','address','hours','accent','payment_note','bank_name','bank_account_name','bank_account_number','bank_receiving_currency'):
            if key not in values: continue
            value=values[key].strip().upper() if key=='bank_receiving_currency' else values[key].strip()
            if len(value)>500: raise ValueError('ข้อความยาวเกินไป')
            conn.execute('INSERT OR REPLACE INTO shop_settings(key,value) VALUES (?,?)',(key,value))
        conn.commit()
    finally: conn.close()

# คำอธิบาย def set_rate: ตรวจสิทธิ์และราคาซื้อ–ขายก่อนเพิ่มหรือแก้สกุลเงิน
# รับค่า: actor_id, code, name, buy, sell | เรียกใช้: db.getconnect
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

# คำอธิบาย def list_users: คืนรายชื่อบัญชีให้ admin ที่ยัง active
# รับค่า: actor_id | เรียกใช้: db.getconnect
def list_users(actor_id):
    conn=db.getconnect()
    try:
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor_id,)).fetchone()!=('admin',): raise PermissionError('เฉพาะ admin')
        return conn.execute('SELECT id,username,email,role,status FROM users ORDER BY id').fetchall()
    finally: conn.close()

# คำอธิบาย def update_user: ปรับสิทธิ์และสถานะบัญชี โดยห้ามปิดสิทธิ์ admin ของตัวเอง
# รับค่า: actor_id, user_id, role, status | เรียกใช้: db.getconnect
def update_user(actor_id,user_id,role,status):
    if role not in {'user','staff','admin'} or status not in {'active','inactive','banned'}: raise ValueError('สิทธิ์หรือสถานะไม่ถูกต้อง')
    if actor_id==user_id and (role!='admin' or status!='active'): raise ValueError('ไม่สามารถปิดสิทธิ์ admin ของตัวเอง')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor_id,)).fetchone()!=('admin',): raise PermissionError('เฉพาะ admin')
        target=conn.execute('SELECT role,status FROM users WHERE id=?',(user_id,)).fetchone()
        if not target or target[1]=='deleted':raise ValueError('ไม่พบบัญชีที่จัดการได้')
        conn.execute('UPDATE users SET role=?,status=? WHERE id=?',(role,status,user_id)); conn.commit()
    finally: conn.close()

# คำอธิบาย def delete_user: เปลี่ยนบัญชีเป็น deleted เพื่อปิดการใช้งานและรักษาประวัติ
# รับค่า: actor_id, user_id | เรียกใช้: db.getconnect
def delete_user(actor_id,user_id):
    if actor_id==user_id:raise ValueError('ไม่สามารถลบบัญชีตัวเอง')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor_id,)).fetchone()!=('admin',):raise PermissionError('เฉพาะ admin')
        row=conn.execute('SELECT status FROM users WHERE id=?',(user_id,)).fetchone()
        if not row or row[0]=='deleted':raise ValueError('ไม่พบบัญชีที่จัดการได้')
        conn.execute("UPDATE users SET status='deleted' WHERE id=?",(user_id,));conn.commit()
    finally:conn.close()
