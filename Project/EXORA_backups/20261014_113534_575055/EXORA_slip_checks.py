"""Exact file and decoded-image duplicate checks; no bank verification."""
import hashlib
from PIL import Image,ImageOps
import EXORA_database as db

def fingerprints(path):
    raw=hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as image:
        if image.width*image.height>25000000:raise ValueError('ภาพสลิปต้องไม่เกิน 25 ล้านพิกเซล')
        pixels=ImageOps.exif_transpose(image).convert('RGBA')
        visual=hashlib.sha256(str(pixels.size).encode()+pixels.tobytes()).hexdigest()
    return raw,visual

def check_and_record(conn,number,path):
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
