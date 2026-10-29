"""Reusable staff-reviewed identity records; no automated eKYC or document image storage."""
import hashlib,json,re
from datetime import date,datetime,timedelta

# ไม่ยกข้อมูลหมายเหตุเก่ามาเป็นผลยืนยันตัวตนอัตโนมัติ
def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS verified_identities(user_id INTEGER PRIMARY KEY,legal_name TEXT NOT NULL,
        profile_fingerprint TEXT NOT NULL,method TEXT NOT NULL,reference TEXT NOT NULL,reviewed_by INTEGER NOT NULL,
        reviewed_at TEXT NOT NULL,valid_until TEXT NOT NULL,status TEXT NOT NULL)''')
    conn.execute('CREATE TABLE IF NOT EXISTS identity_audit(id INTEGER PRIMARY KEY,user_id INTEGER,actor INTEGER,action TEXT,created_at TEXT)')

def normalize(value):return re.sub(r'\s+',' ',str(value).strip()).casefold()

# สรุปแสดงเจ้าของบัญชี ไม่คืนเลขอ้างอิงหลักฐานหรือข้อมูลเอกสาร
def summary(user):
    import EXORA_database as db
    conn=db.getconnect()
    try:
        row=conn.execute('SELECT legal_name,reviewed_at,valid_until FROM verified_identities WHERE user_id=?',(user,)).fetchone()
        if not row:return None
        return {'valid':valid(conn,user,row[0]),'reviewed_at':row[1],'valid_until':row[2]}
    finally:conn.close()

# เปลี่ยนชื่อ อีเมล หรือเบอร์โทรแล้วต้องตรวจใหม่ ไม่แก้ผลเก่าเงียบ ๆ
def fingerprint(conn,user):
    row=conn.execute("SELECT display_name,email,phone FROM users WHERE id=? AND status='active'",(user,)).fetchone()
    if not row:return None
    return hashlib.sha256(json.dumps([normalize(v or '') for v in row],ensure_ascii=False).encode()).hexdigest()

# ชื่อผู้รับต้องตรงบุคคลที่ตรวจไว้ ผลยังไม่หมดอายุหรือถูกถอน
def valid(conn,user,name):
    row=conn.execute('SELECT legal_name,profile_fingerprint,valid_until,status FROM verified_identities WHERE user_id=?',(user,)).fetchone()
    return bool(row and row[3]=='verified' and row[2]>=date.today().isoformat() and normalize(row[0])==normalize(name) and row[1]==fingerprint(conn,user))

# บันทึกผลจากเจ้าหน้าที่ ต้องตรวจหลักฐานภายนอกจริง ไม่มีการอ้างว่าติดต่อทะเบียนราษฎร
def record(conn,user,name,actor,reference,method='document_video',valid_until=None):
    if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()!=('admin',) or user==actor:raise PermissionError('ให้แอดมินอีกบัญชีตรวจรายการนี้')
    if method not in ('document_video','provider_reference'):raise ValueError('วิธีตรวจตัวตนไม่ถูกต้อง')
    if not 10<=len(reference.strip())<=500:raise ValueError('กรอกวิธีตรวจและเลขอ้างอิงหลักฐานอย่างน้อย 10 ตัวอักษร')
    expires=valid_until or (date.today()+timedelta(days=365)).isoformat()
    if date.fromisoformat(expires)<date.today():raise ValueError('หลักฐานยืนยันตัวตนหมดอายุแล้ว')
    snapshot=fingerprint(conn,user)
    if snapshot is None:raise PermissionError('บัญชีไม่พร้อมใช้งาน')
    now=datetime.now().isoformat(timespec='seconds')
    conn.execute('INSERT OR REPLACE INTO verified_identities VALUES (?,?,?,?,?,?,?,?,?)',(user,name,snapshot,method,reference.strip(),actor,now,expires,'verified'))
    conn.execute('INSERT INTO identity_audit(user_id,actor,action,created_at) VALUES (?,?,?,?)',(user,actor,'verified',now))

# ถอนผลได้เมื่อพบความผิดปกติ ประวัติการตรวจยังอยู่ใน audit
def revoke(conn,user,actor):
    if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()!=('admin',):raise PermissionError('เฉพาะ admin')
    conn.execute("UPDATE verified_identities SET status='revoked' WHERE user_id=?",(user,))
    conn.execute('INSERT INTO identity_audit(user_id,actor,action,created_at) VALUES (?,?,?,?)',(user,actor,'revoked',datetime.now().isoformat(timespec='seconds')))
