"""Administrator-managed local news slides, independent of payment history."""
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า uuid: uuid — สร้างรหัสสุ่มสำหรับชื่อไฟล์ ลดการชนกันของชื่อ
import uuid
# คำอธิบาย import: นำเข้า Image, ImageOps: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
# ImageOps: ปรับทิศทางภาพและย่อภาพให้พอดีกรอบ
from PIL import Image, ImageOps
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db

# คำอธิบาย def migrate: เพิ่มตารางหรือคอลัมน์ของโมดูลนี้ โดยรองรับฐานข้อมูลรุ่นเดิม
# รับค่า: conn
def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS news_slides(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,image_path TEXT NOT NULL,position INTEGER NOT NULL,active INTEGER NOT NULL DEFAULT 1)''')

# คำอธิบาย def slides: อ่านข่าวตามลำดับ โดยเลือกแสดงหรือรวมข่าวที่ซ่อน
# รับค่า: include_hidden | เรียกใช้: db.getconnect
def slides(include_hidden=False):
    conn=db.getconnect()
    try:
        migrate(conn);conn.commit();conn.row_factory=__import__('sqlite3').Row
        return [dict(r) for r in conn.execute('SELECT * FROM news_slides '+('' if include_hidden else 'WHERE active=1 ')+'ORDER BY position,id')]
    finally:conn.close()

# คำอธิบาย def authorize: ตรวจว่า actor เป็น admin ที่ยัง active
# รับค่า: conn, actor
def authorize(conn,actor):
    row=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()
    if not row or row[0]!='admin':raise PermissionError('เฉพาะแอดมินจัดการข่าวได้')

# คำอธิบาย def image_path: ตรวจว่าพาธภาพอยู่ในโฟลเดอร์ภาพข่าวที่กำหนด
# รับค่า: relative
def image_path(relative):
    root=(Path(db.BASE_DIR)/'EXORA_assets'/'news').resolve()
    path=(Path(db.BASE_DIR)/relative).resolve()
    if path.parent!=root:raise ValueError('ตำแหน่งภาพข่าวไม่ถูกต้อง')
    return path

# คำอธิบาย def add: ตรวจภาพและหัวข้อ แล้วบันทึกข่าวพร้อมไฟล์ภาพในเครื่อง
# รับค่า: actor, title, source | เรียกใช้: db.getconnect
def add(actor,title,source):
    title=title.strip()
    if not title or len(title)>120:raise ValueError('ชื่อข่าวต้องมี 1–120 ตัวอักษร')
    conn=db.getconnect();target=None
    try:
        authorize(conn,actor);migrate(conn)
        source=Path(source)
        if not source.is_file() or not 0<source.stat().st_size<=10*1024*1024:raise ValueError('ภาพต้องไม่เกิน 10 MB')
        with Image.open(source) as original:
            if original.format not in ('JPEG','PNG') or original.width*original.height>25000000:raise ValueError('รองรับ JPG/PNG ไม่เกิน 25 ล้านพิกเซล')
            original.load();image=ImageOps.exif_transpose(original).convert('RGBA')
            image.thumbnail((2400,1600),Image.Resampling.LANCZOS)
            background=Image.new('RGB',image.size,'white');background.paste(image,mask=image.getchannel('A'))
        root=Path(db.BASE_DIR)/'EXORA_assets'/'news';root.mkdir(parents=True,exist_ok=True)
        target=root/(uuid.uuid4().hex+'.jpg');background.save(target,quality=94)
        position=conn.execute('SELECT COALESCE(MAX(position),0)+1 FROM news_slides').fetchone()[0]
        cursor=conn.execute('INSERT INTO news_slides(title,image_path,position) VALUES (?,?,?)',(title,target.relative_to(db.BASE_DIR).as_posix(),position));conn.commit();return cursor.lastrowid
    except Exception:
        conn.rollback()
        if target:target.unlink(missing_ok=True)
        raise
    finally:conn.close()

# คำอธิบาย def manage: เปลี่ยนลำดับ ซ่อน/แสดง หรือลบข่าวภายใน transaction
# รับค่า: actor, slide_id, action | เรียกใช้: db.getconnect
def manage(actor,slide_id,action):
    if action not in ('delete','toggle','up','down'):raise ValueError('คำสั่งไม่ถูกต้อง')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');authorize(conn,actor);migrate(conn)
        rows=conn.execute('SELECT id,position FROM news_slides ORDER BY position,id').fetchall()
        ids=[r[0] for r in rows]
        if slide_id not in ids:raise ValueError('ไม่พบข่าวนี้')
        if action=='delete':conn.execute('DELETE FROM news_slides WHERE id=?',(slide_id,))
        elif action=='toggle':conn.execute('UPDATE news_slides SET active=1-active WHERE id=?',(slide_id,))
        else:
            index=ids.index(slide_id);other=index+(-1 if action=='up' else 1)
            if 0<=other<len(ids):ids[index],ids[other]=ids[other],ids[index]
            conn.executemany('UPDATE news_slides SET position=? WHERE id=?',enumerate(ids))
        conn.commit()
    except Exception:conn.rollback();raise
    finally:conn.close()

class AutoPlayer:
    """One cancellable timer; leaving the page stops playback."""
    # คำอธิบาย def AutoPlayer.__init__: เตรียมค่าเริ่มต้น ทรัพยากร และองค์ประกอบของคลาส AutoPlayer
    # รับค่า: scheduler, count, render, interval
    def __init__(self,scheduler,count,render,interval=6000):
        self.scheduler=scheduler;self.count=count;self.render=render;self.interval=interval;self.index=0;self.timer=None;self.paused=False;self.closed=False
    # คำอธิบาย def AutoPlayer.start: เริ่มงานของตัวควบคุมและจัดการ timer เดิม
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def start(self):
        self.cancel()
        if not self.closed and not self.paused and self.count>1:self.timer=self.scheduler.after(self.interval,self.tick)
    # คำอธิบาย def AutoPlayer.cancel: ยกเลิก timer ที่ยังรอทำงาน เพื่อไม่ให้แอนิเมชันเก่าค้าง
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def cancel(self):
        if self.timer is not None:self.scheduler.after_cancel(self.timer);self.timer=None
    # คำอธิบาย def AutoPlayer.tick: เลื่อนข่าวเมื่อถึงเวลา หากไม่ได้หยุดหรือปิดตัวควบคุม
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def tick(self):
        self.timer=None
        if not self.closed and not self.paused:self.move(1)
    # คำอธิบาย def AutoPlayer.move: เปลี่ยนตำแหน่งสไลด์แบบวนรอบแล้วเริ่มจับเวลาใหม่
    # รับค่า: step
    def move(self,step):
        if self.closed or not self.count:return
        self.index=(self.index+step)%self.count;self.render(self.index);self.start()
    # คำอธิบาย def AutoPlayer.pause: ตั้งสถานะหยุด/เล่นและปรับ timer ให้สอดคล้อง
    # รับค่า: value
    def pause(self,value=True):self.paused=value;self.start()
    # คำอธิบาย def AutoPlayer.close: ปิดทรัพยากรหรือ timer ของวัตถุนี้และยุติการทำงาน
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def close(self):self.closed=True;self.cancel()
