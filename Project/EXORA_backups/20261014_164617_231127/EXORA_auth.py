"""Email OTP password recovery. No OTP is stored or logged in plaintext."""
# คำอธิบาย import: นำเข้า hashlib: hashlib — คำนวณค่าแฮชสำหรับรหัสผ่าน OTP และลายนิ้วมือไฟล์ตามจุดใช้งาน
import hashlib
# คำอธิบาย import: นำเข้า hmac: hmac — เปรียบเทียบค่าแฮชด้วย compare_digest
import hmac
# คำอธิบาย import: นำเข้า os: os — อ่าน environment variables และทำงานร่วมกับระบบปฏิบัติการ
import os
# คำอธิบาย import: นำเข้า re: re — ตรวจรูปแบบข้อความด้วย regular expressions
import re
# คำอธิบาย import: นำเข้า secrets: secrets — สุ่ม OTP และข้อมูลลับสำหรับการยืนยัน
import secrets
# คำอธิบาย import: นำเข้า smtplib: smtplib — เชื่อมต่อ SMTP เพื่อส่งอีเมล
import smtplib
# คำอธิบาย import: นำเข้า ssl: ssl — สร้างบริบท TLS สำหรับการเชื่อมต่ออีเมล
import ssl
# คำอธิบาย import: นำเข้า time: time — จับเวลา เวลาหมดอายุ และรอบของแอนิเมชัน
import time
# คำอธิบาย import: นำเข้า EmailMessage: email.message — สร้างอีเมล ข้อความ HTML และไฟล์แนบด้วย EmailMessage
# EmailMessage: วัตถุสร้างเนื้อหา ผู้รับ และไฟล์แนบของอีเมล
from email.message import EmailMessage
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db
# คำอธิบาย import: นำเข้า EXORA_email_settings as email_settings: EXORA_email_settings — อ่าน Gmail App Password จาก environment variables และกำหนดผู้ส่ง
import EXORA_email_settings as email_settings

TTL=600
MAX_ATTEMPTS=5
GENERIC_MESSAGE='หากอีเมลนี้ลงทะเบียนและบัญชีพร้อมใช้งาน ระบบจะส่ง OTP ให้ กรุณาตรวจกล่องจดหมายและสแปม'

# คำอธิบาย def migrate: เพิ่มตารางหรือคอลัมน์ของโมดูลนี้ โดยรองรับฐานข้อมูลรุ่นเดิม
# รับค่า: conn
def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS password_reset_otp (
        challenge_id TEXT PRIMARY KEY,user_id INTEGER NOT NULL,email TEXT NOT NULL,
        salt TEXT NOT NULL,code_hash TEXT NOT NULL,expires_at REAL NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,used INTEGER NOT NULL DEFAULT 0,created_at REAL NOT NULL)''')
    conn.execute('CREATE TABLE IF NOT EXISTS password_reset_requests(email_key TEXT NOT NULL,created_at REAL NOT NULL)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reset_requests ON password_reset_requests(email_key,created_at)')

# คำอธิบาย def digest: สร้างค่าแฮช OTP ด้วย PBKDF2 และ salt
# รับค่า: code, salt
def digest(code,salt):
    return hashlib.pbkdf2_hmac('sha256',code.encode('ascii'),bytes.fromhex(salt),120000).hex()

# คำอธิบาย def request_otp: ตรวจคำขอ สร้าง OTP กำหนดอายุและข้อจำกัด แล้วส่งไปยังอีเมล
# รับค่า: address | เรียกใช้: db.getconnect
def request_otp(address):
    address=address.strip().lower()
    if len(address)>254 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',address):
        raise ValueError('กรุณากรอกอีเมลที่ลงทะเบียนให้ถูกต้อง')
    sender=email_settings.SENDER
    password=email_settings.password()
    if not sender or not password:
        raise ValueError('ตั้ง EXORA_GMAIL_APP_PASSWORD ของ '+sender+' ก่อนส่ง OTP')
    stamp=time.time();challenge=secrets.token_urlsafe(32);email_key=hashlib.sha256(address.encode()).hexdigest()
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');migrate(conn)
        conn.execute('DELETE FROM password_reset_requests WHERE created_at<?',(stamp-3600,))
        conn.execute('DELETE FROM password_reset_otp WHERE expires_at<?',(stamp-86400,))
        requests=conn.execute('SELECT created_at FROM password_reset_requests WHERE email_key=? ORDER BY created_at DESC',(email_key,)).fetchall()
        if requests and (stamp-requests[0][0]<60 or len(requests)>=5):
            raise ValueError('ขอ OTP บ่อยเกินไป กรุณารออย่างน้อย 1 นาที (สูงสุด 5 ครั้งต่อชั่วโมง)')
        conn.execute('INSERT INTO password_reset_requests VALUES (?,?)',(email_key,stamp))
        user=conn.execute("SELECT id FROM users WHERE lower(email)=? AND status='active'",(address,)).fetchone()
        if user:
            code=f'{secrets.randbelow(1000000):06d}';salt=secrets.token_hex(16)
            conn.execute('UPDATE password_reset_otp SET used=1 WHERE user_id=?',(user[0],))
            conn.execute('INSERT INTO password_reset_otp(challenge_id,user_id,email,salt,code_hash,expires_at,created_at) VALUES (?,?,?,?,?,?,?)',
                         (challenge,user[0],address,salt,digest(code,salt),stamp+TTL,stamp))
        conn.commit()
    except Exception:
        conn.rollback();raise
    finally:conn.close()
    if user:
        message=EmailMessage();message['From']=sender;message['To']=address;message['Subject']='EXORA | OTP สำหรับตั้งรหัสผ่านใหม่'
        message.set_content(f'รหัส OTP ของคุณ: {code}\nใช้ได้ 10 นาที และใช้ได้ครั้งเดียว\nห้ามบอกรหัสนี้แก่ผู้อื่น\nหากคุณไม่ได้ขอตั้งรหัสผ่านใหม่ ให้ละเว้นอีเมลนี้')
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com',465,context=ssl.create_default_context(),timeout=20) as smtp:
                smtp.login(sender,password);smtp.send_message(message)
        except (OSError,smtplib.SMTPException):
            conn=db.getconnect()
            try:
                conn.execute('UPDATE password_reset_otp SET used=1 WHERE challenge_id=?',(challenge,));conn.commit()
            finally:conn.close()
            # Keep the same response for registered and unregistered addresses.
    return {'challenge_id':challenge,'message':GENERIC_MESSAGE}

# คำอธิบาย def reset_with_otp: ตรวจ OTP ที่ยังใช้ได้ แล้วบันทึกรหัสผ่านใหม่และปิดการใช้ OTP ซ้ำ
# รับค่า: challenge_id, code, new_password | เรียกใช้: db.getconnect, db.hashp
def reset_with_otp(challenge_id,code,new_password):
    if len(new_password)<8 or len(new_password)>256:
        raise ValueError('รหัสผ่านใหม่ต้องมี 8–256 ตัวอักษร')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');migrate(conn)
        conn.row_factory=__import__('sqlite3').Row
        row=conn.execute('SELECT * FROM password_reset_otp WHERE challenge_id=?',(challenge_id,)).fetchone()
        if not row or row['used'] or row['expires_at']<=time.time() or row['attempts']>=MAX_ATTEMPTS:
            raise ValueError('OTP ไม่ถูกต้อง หมดอายุ หรือใช้ไปแล้ว กรุณาขอรหัสใหม่')
        code=str(code).strip()
        valid=bool(re.fullmatch(r'[0-9]{6}',code)) and hmac.compare_digest(digest(code,row['salt']),row['code_hash'])
        if not valid:
            attempts=row['attempts']+1
            conn.execute('UPDATE password_reset_otp SET attempts=?,used=? WHERE challenge_id=?',(attempts,int(attempts>=MAX_ATTEMPTS),challenge_id));conn.commit()
            raise ValueError('OTP ไม่ถูกต้อง กรุณาตรวจสอบรหัส (ลองได้ไม่เกิน 5 ครั้ง)')
        user=conn.execute("SELECT id FROM users WHERE id=? AND lower(email)=? AND status='active'",(row['user_id'],row['email'])).fetchone()
        if not user:raise ValueError('OTP ไม่สามารถใช้กับบัญชีนี้ได้ กรุณาขอรหัสใหม่')
        conn.execute('UPDATE users SET password=? WHERE id=?',(db.hashp(new_password),row['user_id']))
        conn.execute('UPDATE password_reset_otp SET used=1 WHERE user_id=?',(row['user_id'],));conn.commit()
    except Exception:
        conn.rollback();raise
    finally:conn.close()
