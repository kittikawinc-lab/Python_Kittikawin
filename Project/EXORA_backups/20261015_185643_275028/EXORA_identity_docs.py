"""Private ID image uploads, encrypted with Windows DPAPI for the local Windows user."""
import ctypes,io,uuid,sqlite3
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
from PIL import Image,ImageOps
import EXORA_database as db

class Blob(ctypes.Structure):
    _fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]

# Windows protects integrity and binds encryption to the current Windows account
def crypt(data,decrypt=False):
    buffer=ctypes.create_string_buffer(data);source=Blob(len(data),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)));output=Blob()
    api=ctypes.WinDLL('crypt32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.LocalFree.argtypes=[ctypes.c_void_p];kernel.LocalFree.restype=ctypes.c_void_p
    if decrypt:ok=api.CryptUnprotectData(ctypes.byref(source),None,None,None,None,1,ctypes.byref(output))
    else:ok=api.CryptProtectData(ctypes.byref(source),'EXORA identity',None,None,None,1,ctypes.byref(output))
    if not ok:raise OSError('Windows could not access encrypted identity image')
    try:return ctypes.string_at(output.data,output.size)
    finally:kernel.LocalFree(ctypes.cast(output.data,ctypes.c_void_p))

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS identity_documents(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,
        kind TEXT NOT NULL,path TEXT NOT NULL,uploaded_at TEXT NOT NULL,current INTEGER NOT NULL DEFAULT 1)''')

# Current image metadata only; image bytes are never stored in SQLite
def current(user):
    conn=db.getconnect()
    try:
        conn.row_factory=sqlite3.Row
        row=conn.execute('SELECT * FROM identity_documents WHERE user_id=? AND current=1 ORDER BY id DESC LIMIT 1',(user,)).fetchone()
        return dict(row) if row else None
    finally:conn.close()

# Only the account owner may upload; replacing evidence invalidates previous verification
def upload(actor,kind,source):
    if kind not in ('id_card','passport'):raise ValueError('ประเภทเอกสารไม่ถูกต้อง')
    source=Path(source)
    if not source.is_file() or not 0<source.stat().st_size<=10*1024*1024:raise ValueError('ภาพต้องไม่เกิน 10 MB')
    with Image.open(source) as original:
        if original.format not in ('JPEG','PNG') or original.width*original.height>25000000:raise ValueError('ไฟล์ภาพไม่ถูกต้อง')
        original.load();image=ImageOps.exif_transpose(original).convert('RGB');image.thumbnail((2400,2400))
        buffer=io.BytesIO();image.save(buffer,format='PNG');protected=crypt(buffer.getvalue())
    conn=db.getconnect();path=None
    try:
        conn.execute('BEGIN IMMEDIATE')
        if not conn.execute("SELECT 1 FROM users WHERE id=? AND status='active'",(actor,)).fetchone():raise PermissionError('บัญชีไม่พร้อมใช้งาน')
        folder=Path(db.BASE_DIR)/'EXORA_assets'/'identity_private';folder.mkdir(parents=True,exist_ok=True)
        path=folder/(uuid.uuid4().hex+'.dpapi');path.write_bytes(protected)
        conn.execute('UPDATE identity_documents SET current=0 WHERE user_id=?',(actor,))
        conn.execute('INSERT INTO identity_documents(user_id,kind,path,uploaded_at) VALUES (?,?,?,?)',(actor,kind,str(path.relative_to(db.BASE_DIR)),datetime.now().isoformat(timespec='seconds')))
        conn.execute("UPDATE verified_identities SET status='needs_review' WHERE user_id=?",(actor,));conn.commit()
    except Exception:
        conn.rollback()
        if path:path.unlink(missing_ok=True)
        raise
    finally:conn.close()

# Owners and active admins can decode in memory, with no plaintext temporary image
def image(actor,user):
    conn=db.getconnect()
    try:
        row=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()
        if not row or (actor!=user and row[0]!='admin'):raise PermissionError('ไม่มีสิทธิ์ดูเอกสารนี้')
    finally:conn.close()
    document=current(user)
    if not document:raise ValueError('ยังไม่ได้แนบเอกสารยืนยันตัวตน')
    root=(Path(db.BASE_DIR)/'EXORA_assets'/'identity_private').resolve();path=(Path(db.BASE_DIR)/document['path']).resolve()
    if path.parent!=root:raise ValueError('ตำแหน่งไฟล์ไม่ถูกต้อง')
    with Image.open(io.BytesIO(crypt(path.read_bytes(),True))) as picture:return picture.copy()
