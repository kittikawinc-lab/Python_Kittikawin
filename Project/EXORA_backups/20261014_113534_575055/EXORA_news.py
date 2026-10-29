"""Administrator-managed local news slides, independent of payment history."""
from pathlib import Path
import uuid
from PIL import Image, ImageOps
import EXORA_database as db

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS news_slides(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,image_path TEXT NOT NULL,position INTEGER NOT NULL,active INTEGER NOT NULL DEFAULT 1)''')

def slides(include_hidden=False):
    conn=db.getconnect()
    try:
        migrate(conn);conn.commit();conn.row_factory=__import__('sqlite3').Row
        return [dict(r) for r in conn.execute('SELECT * FROM news_slides '+('' if include_hidden else 'WHERE active=1 ')+'ORDER BY position,id')]
    finally:conn.close()

def authorize(conn,actor):
    row=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()
    if not row or row[0]!='admin':raise PermissionError('เฉพาะแอดมินจัดการข่าวได้')

def image_path(relative):
    root=(Path(db.BASE_DIR)/'EXORA_assets'/'news').resolve()
    path=(Path(db.BASE_DIR)/relative).resolve()
    if path.parent!=root:raise ValueError('ตำแหน่งภาพข่าวไม่ถูกต้อง')
    return path

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
    def __init__(self,scheduler,count,render,interval=6000):
        self.scheduler=scheduler;self.count=count;self.render=render;self.interval=interval;self.index=0;self.timer=None;self.paused=False;self.closed=False
    def start(self):
        self.cancel()
        if not self.closed and not self.paused and self.count>1:self.timer=self.scheduler.after(self.interval,self.tick)
    def cancel(self):
        if self.timer is not None:self.scheduler.after_cancel(self.timer);self.timer=None
    def tick(self):
        self.timer=None
        if not self.closed and not self.paused:self.move(1)
    def move(self,step):
        if self.closed or not self.count:return
        self.index=(self.index+step)%self.count;self.render(self.index);self.start()
    def pause(self,value=True):self.paused=value;self.start()
    def close(self):self.closed=True;self.cancel()
