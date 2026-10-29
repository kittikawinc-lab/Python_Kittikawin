"""Store contact details share existing shop_settings, independent of Gmail sender."""
# คำอธิบาย import: นำเข้า re: re — ตรวจรูปแบบข้อความด้วย regular expressions
import re
# คำอธิบาย import: นำเข้า urlparse: urllib.parse — แยกส่วน URL หรือเข้ารหัสพารามิเตอร์คำขอ
# urlparse: แยก URL เพื่อตรวจ scheme และ hostname
from urllib.parse import urlparse
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db

FIELDS=[('phone','เบอร์โทร'),('contact_email','อีเมลติดต่อ'),('address','ที่อยู่'),('hours','เวลาเปิดบริการ'),('contact_line','LINE ID'),('contact_facebook','Facebook'),('contact_website','เว็บไซต์'),('contact_map','ลิงก์แผนที่'),('contact_note','ข้อมูลเพิ่มเติม')]
LINKS={'contact_facebook','contact_website','contact_map'}

# คำอธิบาย def save: ตรวจสิทธิ์ admin รูปแบบอีเมลและลิงก์ แล้วบันทึกข้อมูลติดต่อร้าน
# รับค่า: actor, values | เรียกใช้: db.getconnect
def save(actor,values):
    cleaned={key:str(values.get(key,'')).strip() for key,_ in FIELDS}
    if any(len(value)>500 for value in cleaned.values()):raise ValueError('ข้อมูลแต่ละช่องต้องไม่เกิน 500 ตัวอักษร')
    if cleaned['contact_email'] and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',cleaned['contact_email']):raise ValueError('อีเมลติดต่อไม่ถูกต้อง')
    for key in LINKS:
        value=cleaned[key]
        if value:
            parsed=urlparse(value)
            if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or any(c.isspace() for c in value):raise ValueError('ลิงก์ต้องเป็น http:// หรือ https:// ที่ถูกต้อง')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()!=('admin',):raise PermissionError('เฉพาะ admin')
        conn.executemany('INSERT OR REPLACE INTO shop_settings(key,value) VALUES (?,?)',cleaned.items());conn.commit()
    finally:conn.close()
