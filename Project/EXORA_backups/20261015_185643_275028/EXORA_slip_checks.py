"""Exact file and decoded-image duplicate checks; no bank verification."""
# คำอธิบาย import: นำเข้า hashlib: hashlib — คำนวณค่าแฮชสำหรับรหัสผ่าน OTP และลายนิ้วมือไฟล์ตามจุดใช้งาน
import hashlib
# คำอธิบาย import: นำเข้า Image, ImageOps: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
# ImageOps: ปรับทิศทางภาพและย่อภาพให้พอดีกรอบ
from PIL import Image,ImageOps
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db

# คำอธิบาย def fingerprints: คำนวณ SHA-256 ของไฟล์และพิกเซลภาพที่ปรับทิศทางแล้ว
# รับค่า: path
def fingerprints(path):
    raw=hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as image:
        if image.width*image.height>25000000:raise ValueError('ภาพสลิปต้องไม่เกิน 25 ล้านพิกเซล')
        pixels=ImageOps.exif_transpose(image).convert('RGBA')
        visual=hashlib.sha256(str(pixels.size).encode()+pixels.tobytes()).hexdigest()
    return raw,visual

# คำอธิบาย def check_and_record: ตรวจลายนิ้วมือสลิปกับรายการอื่นและบันทึกข้อมูลตรวจซ้ำ
# รับค่า: conn, number, path
def check_and_record(conn,number,path):
    # คำอธิบาย import: นำเข้า slip_path: EXORA_payments — รับหลักฐาน ตรวจสิทธิ์ และจัดการสถานะรายการชำระเงิน
    from EXORA_payments import slip_path
    conn.execute('CREATE TABLE IF NOT EXISTS slip_fingerprints(transaction_no TEXT NOT NULL,raw_hash TEXT NOT NULL,image_hash TEXT NOT NULL,PRIMARY KEY(transaction_no,raw_hash))')
    conn.execute('CREATE INDEX IF NOT EXISTS slip_raw_index ON slip_fingerprints(raw_hash)')
    conn.execute('CREATE INDEX IF NOT EXISTS slip_image_index ON slip_fingerprints(image_hash)')
    # Index original evidence too, without modifying historical transactions.
    for old_number,relative in conn.execute('SELECT transaction_no,slip_path FROM transactions WHERE slip_path IS NOT NULL').fetchall():
        if conn.execute('SELECT 1 FROM slip_fingerprints WHERE transaction_no=?',(old_number,)).fetchone():continue
        try:raw,visual=fingerprints(slip_path({'slip_path':relative}))
        except (OSError,ValueError):continue
        conn.execute('INSERT OR IGNORE INTO slip_fingerprints VALUES (?,?,?)',(old_number,raw,visual))
    raw,visual=fingerprints(path)
    if conn.execute('SELECT 1 FROM slip_fingerprints WHERE transaction_no<>? AND (raw_hash=? OR image_hash=?)',(number,raw,visual)).fetchone():
        raise ValueError('ภาพสลิปนี้ถูกใช้ในรายการอื่นแล้ว กรุณาตรวจสอบหลักฐาน')
    conn.execute('INSERT OR IGNORE INTO slip_fingerprints VALUES (?,?,?)',(number,raw,visual))
