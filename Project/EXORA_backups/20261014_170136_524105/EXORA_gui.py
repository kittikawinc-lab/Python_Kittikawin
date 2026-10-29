"""EXORA storefront: native Windows Tkinter UI, with no web server."""
# คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
import tkinter as tk
# คำอธิบาย import: นำเข้า ttk, messagebox, filedialog, colorchooser: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
# ttk: widget รูปแบบธีม เช่น ตาราง แท็บ และช่องเลือก
# messagebox: กล่องแจ้งผล ข้อผิดพลาด และคำถามยืนยัน
# filedialog: กล่องเลือกไฟล์และตำแหน่งบันทึก
# colorchooser: กล่องเลือกสีร้านหรือโปรไฟล์
from tkinter import ttk, messagebox, filedialog, colorchooser
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า datetime: datetime — จัดการวันที่ เวลา และเขตเวลา
# datetime: วันและเวลาของรายการและเอกสาร
from datetime import datetime,date,timedelta
# คำอธิบาย import: นำเข้า ThreadPoolExecutor: concurrent.futures — เรียกงานเบื้องหลังด้วย ThreadPoolExecutor เพื่อไม่ให้ UI ค้าง
# ThreadPoolExecutor: กลุ่มเธรดสำหรับงานออนไลน์และอีเมลเบื้องหลัง
from concurrent.futures import ThreadPoolExecutor
# คำอธิบาย import: นำเข้า queue: queue — ส่งผลลัพธ์จากเธรดงานกลับไปยังเธรดหน้าจอ
import queue
# คำอธิบาย import: นำเข้า os: os — อ่าน environment variables และทำงานร่วมกับระบบปฏิบัติการ
import os
# คำอธิบาย import: นำเข้า tempfile: tempfile — สร้างไฟล์หรือโฟลเดอร์ชั่วคราว
import tempfile
# คำอธิบาย import: นำเข้า uuid: uuid — สร้างรหัสสุ่มสำหรับชื่อไฟล์ ลดการชนกันของชื่อ
import uuid
# คำอธิบาย import: นำเข้า Image, ImageTk: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
# ImageTk: แปลงภาพ Pillow เป็น PhotoImage สำหรับ Tkinter
from PIL import Image, ImageTk
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db
# คำอธิบาย import: นำเข้า EXORA_profiles as profiles: EXORA_profiles — จัดการโปรไฟล์ ร้าน ผู้ใช้ และการคำนวณยอดแลกเงิน
import EXORA_profiles as profiles
# คำอธิบาย import: นำเข้า EXORA_payments as payments: EXORA_payments — รับหลักฐาน ตรวจสิทธิ์ และจัดการสถานะรายการชำระเงิน
import EXORA_payments as payments
# คำอธิบาย import: นำเข้า EXORA_receipts as receipts: EXORA_receipts — สร้าง PDF ใบเสร็จและส่งให้เจ้าของรายการ
import EXORA_receipts as receipts
# คำอธิบาย import: นำเข้า EXORA_brand as brand: EXORA_brand — วาดโลโก้และองค์ประกอบแบรนด์ EXORA
import EXORA_brand as brand
# คำอธิบาย import: นำเข้า EXORA_auth as auth: EXORA_auth — สร้าง ตรวจสอบ OTP และตั้งรหัสผ่านใหม่
import EXORA_auth as auth
# คำอธิบาย import: นำเข้า EXORA_email_settings as email_settings: EXORA_email_settings — อ่าน Gmail App Password จาก environment variables และกำหนดผู้ส่ง
import EXORA_email_settings as email_settings
# คำอธิบาย import: นำเข้า EXORA_layout as layout: EXORA_layout — กำหนดขนาด ฟอนต์ และการเปลี่ยนหน้าสำหรับจอ FHD
import EXORA_layout as layout
# คำอธิบาย import: นำเข้า EXORA_visuals as visuals: EXORA_visuals — สร้างภาพประกอบหน้าล็อกอินและภาพตัวอย่างการออกแบบ
import EXORA_visuals as visuals
# คำอธิบาย import: นำเข้า EXORA_effects as effects: EXORA_effects — เอฟเฟกต์ปุ่ม เฟดภาพ และการแสดงผล พร้อมยกเลิก timer
import EXORA_effects as effects
# คำอธิบาย import: นำเข้า EXORA_rates as online_rates: EXORA_rates — เชื่อมข้อมูลอัตราออนไลน์ เก็บราคาล่าสุด และกำหนดราคาอัตโนมัติ
import EXORA_rates as online_rates
# คำอธิบาย import: นำเข้า EXORA_news as news: EXORA_news — จัดเก็บและจัดการภาพข่าว รวมตัวควบคุมการเลื่อนสไลด์
import EXORA_news as news
# คำอธิบาย import: นำเข้า NewsSlideshow: EXORA_news_ui — สร้างสไลด์ข่าวบนหน้าร้านพร้อมเฟดภาพ
# NewsSlideshow: คลาสสร้างหน้าสไลด์ข่าวพร้อมปุ่มและเฟดภาพ
from EXORA_news_ui import NewsSlideshow
# คำอธิบาย import: นำเข้า MotionScene: EXORA_motion — วาดยานพาหนะและองค์ประกอบเคลื่อนไหวตามธีมเดินทาง
# MotionScene: คลาสวาดและอัปเดตฉากยานพาหนะเคลื่อนไหว
from EXORA_motion import MotionScene
# คำอธิบาย import: นำเข้า EXORA_contact as contact: EXORA_contact — ตรวจสอบและบันทึกข้อมูลติดต่อร้าน
import EXORA_contact as contact
# ธนาคารและสถิติแอดมิน
import EXORA_banks as banks
import EXORA_statistics as statistics
# คำอธิบาย import: นำเข้า webbrowser: webbrowser — เปิดลิงก์ภายนอกด้วยเบราว์เซอร์เมื่อผู้ใช้กด
import webbrowser
# คำอธิบาย import: นำเข้า font as ui_font: EXORA_layout — กำหนดขนาด ฟอนต์ และการเปลี่ยนหน้าสำหรับจอ FHD
# ui_font: ฟังก์ชันกำหนดรูปแบบฟอนต์ของหน้าจอ
from EXORA_layout import font as ui_font

BG='#f6f7f1'; WHITE='#ffffff'; INK='#173e33'; MUTED='#788478'; LINE='#dfe5d9'; LIME='#d8ef9a'
STATUS={'legacy':'ประวัติเดิม','pending':'รอตรวจสอบ','approved':'อนุมัติแล้ว','rejected':'ปฏิเสธ'}
SYMBOLS={'USD':'$','EUR':'€','GBP':'£','JPY':'¥','CNY':'¥','KRW':'₩','THB':'฿'}

class Application:
    # คำอธิบาย def Application.__init__: เตรียมค่าเริ่มต้น ทรัพยากร และองค์ประกอบของคลาส Application
    # รับค่า: root
    def __init__(self,root):
        self.root=root; self.current_user=None; self.images=[]; self.green='#125b4a';self.user_preview=False
        self.motion_enabled=tk.BooleanVar(master=root,value=True)
        icon=Path(db.BASE_DIR)/'EXORA_assets'/'brand'/'EXORA_icon.png'
        if icon.is_file():
            with Image.open(icon) as image:self.app_icon=ImageTk.PhotoImage(image.copy(),master=root)
            root.iconphoto(True,self.app_icon)
        self.root.title('EXORA | Currency Exchange')
        self.root.bind('<F11>',lambda event:self.root.attributes('-fullscreen',not bool(self.root.attributes('-fullscreen'))))
        self.root.bind('<Escape>',lambda event:self.root.attributes('-fullscreen',False))
        width=min(1760,root.winfo_screenwidth()-60);height=min(980,root.winfo_screenheight()-100)
        self.root.geometry(f'{max(960,width)}x{max(650,height)}'); self.root.minsize(1024,650); self.root.configure(bg=BG)
        if os.name=='nt':self.root.state('zoomed')
        # คำอธิบาย import: นำเข้า tkinter.font as tkfont: tkinter.font — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
        import tkinter.font as tkfont
        for name in ('TkDefaultFont','TkTextFont','TkMenuFont','TkHeadingFont'):
            tkfont.nametofont(name).configure(family='Tahoma',size=-14)
        self.pool=ThreadPoolExecutor(max_workers=2); self.jobs=queue.Queue(); self.closed=False
        self.pending_jobs=0;self.busy_indicator=None
        self.rate_busy=False;self.rate_timer=None;self.rate_views=[];self.rate_results=queue.Queue();self.rate_cards=[]
        self.rate_message='กำลังตรวจสอบราคาออนไลน์…'
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.after(100,self.poll_jobs)
        self.configure_styles(); self.login_page()
        self.root.after(5000,self.check_session)
        self.rate_timer=self.root.after(500,self.refresh_rates)

    # คำอธิบาย def Application.check_session: ตรวจว่าบัญชียัง active และให้ออกจากระบบหากถูกปิดหรือแบน
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: db.getconnect
    def check_session(self):
        if self.closed:return
        if self.current_user:
            conn=db.getconnect()
            try:row=conn.execute('SELECT status FROM users WHERE id=?',(self.current_user['id'],)).fetchone()
            finally:conn.close()
            if not row or row[0]!='active':
                self.login_page();messagebox.showinfo('EXORA','บัญชีนี้ไม่พร้อมใช้งาน กรุณาติดต่อร้าน',parent=self.root)
        self.root.after(5000,self.check_session)

    # คำอธิบาย def Application.refresh_rates: ส่งงานดึงอัตราออนไลน์ไปทำเบื้องหลัง และป้องกันคำขอซ้อนกัน
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def refresh_rates(self):
        if self.closed or self.rate_busy:return
        if self.rate_timer:
            self.root.after_cancel(self.rate_timer);self.rate_timer=None
        self.rate_busy=True
        # คำอธิบาย def Application.refresh_rates.work: ทำงานเบื้องหลังและส่งผลกลับ
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: online_rates.refresh
        def work():
            try:result=online_rates.refresh()
            except Exception:result={'ok':False,'message':'ดึงข้อมูลไม่สำเร็จ · ใช้ราคาที่บันทึกไว้'}
            self.rate_results.put(result)
        self.pool.submit(work)

    # คำอธิบาย def Application.rates_ready: รับผลดึงอัตรา ปรับข้อความหน้าจอ และตั้งรอบตรวจครั้งถัดไป
    # รับค่า: result | เรียกใช้: online_rates.snapshot, online_rates.interval_ms
    def rates_ready(self,result):
        self.rate_busy=False;self.rate_message=result['message']
        if not result.get('ok'):
            cached=online_rates.snapshot()
            if cached:self.rate_message+=' · ข้อมูลเดิม '+min(v.get('time') or v['date'] for v in cached.values())+' ('+', '.join(sorted({v.get('source') or 'Frankfurter' for v in cached.values()}))+')'
        self.update_rate_views()
        if not self.closed:self.rate_timer=self.root.after(online_rates.interval_ms(),self.refresh_rates)

    # คำอธิบาย def Application.update_rate_views: รีเฟรชตารางราคาและการ์ดที่ยังแสดงอยู่
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: online_rates.snapshot, db.getcurs, db.getcur
    def update_rate_views(self):
        market=online_rates.snapshot();alive=[]
        for tree,status in self.rate_views:
            if not tree.winfo_exists():continue
            selected=[tree.item(i,'values')[0] for i in tree.selection()]
            tree.delete(*tree.get_children())
            for row in db.getcurs():
                if row[1]=='THB':continue
                reference=market.get(row[1]);mid=f"{reference['mid']:,.4f}" if reference else '—'
                tree.insert('','end',iid=row[1],values=(row[1],row[2],f'{row[3]:,.4f}' if row[3]>0 else 'รอตั้งราคา',f'{row[4]:,.4f}' if row[4]>0 else 'รอตั้งราคา',mid))
            tree.selection_set([code for code in selected if tree.exists(code)])
            status.configure(text=self.visible_rate_message());alive.append((tree,status))
        self.rate_views=alive
        cards=[]
        for widget,code in self.rate_cards:
            if widget.winfo_exists():
                row=db.getcur(code);widget.configure(text=f'{row[4]:,.4f}' if row and row[4]>0 else '—');cards.append((widget,code))
        self.rate_cards=cards

    # คำอธิบาย def Application.close: ปิดทรัพยากรหรือ timer ของวัตถุนี้และยุติการทำงาน
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def close(self):
        if self.rate_timer:self.root.after_cancel(self.rate_timer)
        self.closed=True; self.pool.shutdown(wait=False,cancel_futures=True); self.root.destroy()

    # คำอธิบาย def Application.poll_jobs: รับผลจากคิวงานและเรียก callback บนเธรดหน้าจอ
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def poll_jobs(self):
        if self.closed:return
        while not self.rate_results.empty():self.safe(lambda:self.rates_ready(self.rate_results.get()))
        while not self.jobs.empty():
            callback,result,error=self.jobs.get()
            self.pending_jobs=max(0,self.pending_jobs-1)
            if not self.pending_jobs and self.busy_indicator and self.busy_indicator.frame.winfo_exists():self.busy_indicator.hide()
            if error: messagebox.showerror('EXORA',str(error),parent=self.root)
            else: self.safe(lambda:callback(result))
        self.root.after(100,self.poll_jobs)

    # คำอธิบาย def Application.background: ส่งงานไปยัง thread pool พร้อมแสดงสถานะกำลังทำงาน
    # รับค่า: job, callback
    def background(self,job,callback):
        self.pending_jobs+=1
        if not self.busy_indicator or not self.busy_indicator.frame.winfo_exists():self.busy_indicator=effects.BusyIndicator(self.root)
        self.busy_indicator.show('กำลังเตรียมข้อมูลให้คุณ…',self.motion_enabled.get())
        # คำอธิบาย def Application.background.work: ทำงานเบื้องหลังและส่งผลกลับ
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def work():
            try:self.jobs.put((callback,job(),None))
            except Exception as error:self.jobs.put((callback,None,error))
        self.pool.submit(work)

    # คำอธิบาย def Application.safe: เรียกฟังก์ชันและแสดงข้อผิดพลาดเป็นกล่องข้อความ
    # รับค่า: fn
    def safe(self,fn):
        try:
            return fn()
        except Exception as error:messagebox.showerror('EXORA',str(error),parent=self.root)

    # จำกัดคำสั่งที่ผู้ใช้กดระหว่างตั้งรหัส admin ใหม่ ไม่ขัดขวาง callback ภายในระบบ
    def user_action(self,fn):
        if self.current_user and self.current_user.get('password_change_required') and getattr(fn,'__name__','') not in ('profile_page','login_page','password','close'):
            messagebox.showinfo('EXORA','กรุณาเปลี่ยนรหัสผ่าน admin เริ่มต้นก่อน',parent=self.root);return
        return self.safe(fn)

    # คำอธิบาย def Application.is_admin_view: ตรวจว่าเป็นหน้าฝั่ง admin จริง และไม่ได้อยู่ในโหมดดูผู้ใช้
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def is_admin_view(self):
        if not self.current_user or self.user_preview:return False
        try:return profiles.get_profile(self.current_user['id'])['role']=='admin'
        except ValueError:return False

    # คำอธิบาย def Application.toggle_user_view: สลับหน้าตัวอย่างผู้ใช้กับหน้า admin โดยไม่เปลี่ยนสิทธิ์ในฐานข้อมูล
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.get_profile
    def toggle_user_view(self):
        if profiles.get_profile(self.current_user['id'])['role']!='admin':raise PermissionError('เฉพาะ admin')
        self.user_preview=not self.user_preview;self.shell();self.home()

    # คำอธิบาย def Application.ensure_not_preview: ป้องกันการบันทึกข้อมูลในโหมดดูตัวอย่างผู้ใช้
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def ensure_not_preview(self):
        if self.user_preview:raise ValueError('นี่คือโหมดดูหน้าผู้ใช้ กลับฝั่งแอดมินเพื่อบันทึกข้อมูล')

    # คำอธิบาย def Application.visible_rate_message: เลือกข้อความสถานะราคาที่เหมาะกับสิทธิ์ของผู้ดู
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: online_rates.snapshot
    def visible_rate_message(self):
        if self.is_admin_view():return self.rate_message
        cached=online_rates.snapshot()
        stamp=min((v.get('time') or v['date'] for v in cached.values()),default='')
        return ('ยังอัปเดตไม่ได้ · ใช้ราคาล่าสุดที่บันทึกไว้' if 'ไม่สำเร็จ' in self.rate_message or 'ออฟไลน์' in self.rate_message or 'เก่าเกิน' in self.rate_message else 'ข้อมูลอ้างอิง')+(' · '+stamp if stamp else ' · กำลังตรวจสอบ')

    # คำอธิบาย def Application.configure_styles: ตั้งสี ฟอนต์ และรูปแบบของ ttk widgets
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def configure_styles(self):
        style=ttk.Style(self.root); style.theme_use('clam')
        style.configure('Treeview',background=WHITE,foreground=INK,fieldbackground=WHITE,rowheight=37,font=ui_font(10),borderwidth=0)
        style.configure('Treeview.Heading',background='#eef3e8',foreground=MUTED,font=ui_font(9),padding=(10,12),relief='flat')
        style.map('Treeview',background=[('selected','#dfedcf')],foreground=[('selected',INK)])
        style.configure('TCombobox',padding=8,fieldbackground=WHITE,foreground=INK)
        style.configure('TEntry',padding=9,fieldbackground=WHITE,foreground=INK)
        style.configure('TNotebook',background=BG,borderwidth=0)
        style.configure('Travel.TNotebook',background='#d8ef9a',borderwidth=2)
        style.configure('TNotebook.Tab',padding=(17,12),font=ui_font(10))
        style.map('TNotebook.Tab',background=[('selected',self.green)],foreground=[('selected',WHITE)])
        style.map('TEntry',bordercolor=[('focus',self.green)],fieldbackground=[('focus','#f7faf1')])
        style.map('TCombobox',bordercolor=[('focus',self.green)])

    # คำอธิบาย def Application.label: สร้างข้อความบนหน้าจอด้วยรูปแบบมาตรฐานของ EXORA
    # รับค่า: parent, text, size, color, bg, bold, **kwargs
    def label(self,parent,text,size=11,color=INK,bg=None,bold=False,**kwargs):
        return tk.Label(parent,text=text,font=ui_font(size,bold),fg=color,bg=bg or parent.cget('bg'),**kwargs)

    # คำอธิบาย def Application.button: สร้างปุ่ม ผูกคำสั่ง และเพิ่มเอฟเฟกต์ตอบสนอง
    # รับค่า: parent, text, command, kind, **kwargs
    def button(self,parent,text,command,kind='primary',**kwargs):
        colors={'primary':(self.green,WHITE),'light':(LIME,INK),'secondary':('#eaf0e2',INK),'danger':('#ab4b3c',WHITE),'plain':(parent.cget('bg'),self.green)}
        bg,fg=colors[kind]
        button=tk.Button(parent,text=text,command=lambda:self.user_action(command),bg=bg,fg=fg,font=ui_font(10,True),relief='flat',borderwidth=0,padx=18,pady=11,cursor='hand2',activebackground=bg,activeforeground=fg,**kwargs)
        effects.button_feedback(button,bg,lambda:self.motion_enabled.get());return button

    # คำอธิบาย def Application.card: สร้างกรอบการ์ดและเอฟเฟกต์ขอบ
    # รับค่า: parent, **kwargs
    def card(self,parent,**kwargs):
        card=tk.Frame(parent,bg=WHITE,highlightthickness=1,highlightbackground=LINE,**kwargs)
        effects.card_feedback(card,lambda:self.motion_enabled.get());return card

    # คำอธิบาย def Application.field: สร้างป้ายกำกับ ช่องกรอก และตัวแปรเก็บค่า
    # รับค่า: parent, label, value, secret
    def field(self,parent,label,value='',secret=False):
        self.label(parent,label,10,MUTED).pack(anchor='w',pady=(12,6))
        var=tk.StringVar(value=value or '')
        entry=ttk.Entry(parent,textvariable=var,font=ui_font(11),show='●' if secret else '')
        entry.pack(fill='x'); return var,entry

    # คำอธิบาย def Application.clear_root: ล้างหน้าจอเดิมและยกเลิกเอฟเฟกต์ก่อนสร้างหน้าใหม่
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def clear_root(self):
        if hasattr(self,'transition'):self.transition.cancel()
        if self.busy_indicator and self.busy_indicator.frame.winfo_exists():self.busy_indicator.destroy()
        self.busy_indicator=None
        for widget in self.root.winfo_children():widget.destroy()
        self.images=[]

    # คำอธิบาย def Application.login_page: สร้างหน้าล็อกอิน ภาพประกอบ และทางเข้าสมัคร/ลืมรหัสผ่าน
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.shop
    def login_page(self):
        self.clear_root(); self.current_user=None;self.user_preview=False; self.shop=profiles.shop(); self.green=self.shop.get('accent') or '#125b4a'
        stage=tk.Frame(self.root,bg=WHITE,highlightbackground=LINE,highlightthickness=1)
        stage.place(relx=.5,rely=.5,anchor='center',width=1640,height=860);stage.grid_propagate(False)
        stage.columnconfigure(0,weight=55,uniform='login');stage.columnconfigure(1,weight=45,uniform='login');stage.rowconfigure(0,weight=1)
        left=tk.Canvas(stage,bg=self.green,highlightthickness=0);left.grid(row=0,column=0,sticky='nsew')
        right=tk.Frame(stage,bg=WHITE);right.grid(row=0,column=1,sticky='nsew')
        hero={'timer':None,'size':None}
        # คำอธิบาย def Application.login_page.redraw: วาดภาพใหม่เมื่อขนาดพื้นที่เปลี่ยน
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def redraw():
            hero['timer']=None
            if not left.winfo_exists():return
            size=(max(1,left.winfo_width()),max(1,left.winfo_height()))
            if hero['size']==size:return
            hero['size']=size;photo=ImageTk.PhotoImage(visuals.hero(*size));left.delete('travel-image');left.create_image(0,0,image=photo,anchor='nw',tags='travel-image');left.photo=photo
        # คำอธิบาย def Application.login_page.resized: รับเหตุการณ์เปลี่ยนขนาดและเลื่อนการวาดใหม่เพื่อลดงานซ้ำ
        # รับค่า: event
        def resized(event):
            if event.widget is self.root:
                width,height=visuals.login_size(event.width,event.height);stage.place_configure(width=width,height=height)
            if hero['timer']:
                try:left.after_cancel(hero['timer'])
                except tk.TclError:pass
            hero['timer']=left.after(40,redraw)
        # คำอธิบาย def Application.login_page.destroy: หยุด timer หรือคืนทรัพยากรเมื่อ widget ถูกทำลาย
        # รับค่า: event
        def destroy(event):
            if event.widget is left and hero['timer']:
                try:left.after_cancel(hero['timer'])
                except tk.TclError:pass
        left.bind('<Configure>',resized);left.bind('<Destroy>',destroy,add='+');self.root.bind('<Configure>',resized)
        MotionScene(left,lambda:self.motion_enabled.get(),login=True)
        inner=tk.Frame(right,bg=WHITE);inner.place(relx=.5,rely=.5,anchor='center',width=460)
        right.bind('<Configure>',lambda e:inner.place_configure(width=min(460,max(300,e.width-90))))
        self.label(inner,'ยินดีต้อนรับกลับ',25,bold=True).pack(anchor='w',pady=(12,8))
        username,entry=self.field(inner,'ชื่อผู้ใช้ หรืออีเมล');password,pwd=self.field(inner,'รหัสผ่าน',secret=True)
        # คำอธิบาย def Application.login_page.login: ตรวจชื่อผู้ใช้หรืออีเมล รหัสผ่าน และสถานะบัญชี
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: db.login
        def login():
            user=db.login(username.get(),password.get())
            if not user:raise ValueError('ข้อมูลเข้าสู่ระบบไม่ถูกต้อง หรือบัญชีถูกจำกัดชั่วคราว กรุณาตรวจสอบหรือลองภายหลัง')
            self.current_user=user;self.shell()
            if user.get('password_change_required'):
                self.profile_page();messagebox.showinfo('EXORA','กรุณาเปลี่ยนรหัสผ่าน admin เริ่มต้นก่อนจัดการร้านหรือทำรายการ',parent=self.root)
            else:self.home()
        self.button(inner,'เข้าสู่ระบบ  ↗',login).pack(fill='x',pady=(25,10))
        self.button(inner,'ยังไม่มีบัญชี?  สมัครสมาชิก',self.signup,'plain').pack(fill='x')
        self.button(inner,'ลืมรหัสผ่าน?  รับ OTP ทางอีเมล',self.forgot_password,'plain').pack(fill='x')
        tk.Checkbutton(inner,text='เอฟเฟกต์',variable=self.motion_enabled,bg=WHITE,fg=MUTED,activebackground=WHITE,font=ui_font(9),highlightthickness=0).pack(anchor='w',pady=(12,0))
        entry.bind('<Return>',lambda e:pwd.focus_set());pwd.bind('<Return>',lambda e:self.safe(login));entry.focus_set()

    # คำอธิบาย def Application.dialog: สร้างหน้าต่างย่อย จัดขนาดให้อยู่ในจอ และเพิ่มส่วนตกแต่ง
    # รับค่า: title, width, height
    def dialog(self,title,width=650,height=680):
        self.root.update_idletasks()
        width,height,x,y=layout.dialog_geometry(self.root.winfo_screenwidth(),self.root.winfo_screenheight(),self.root.winfo_rootx(),self.root.winfo_rooty(),self.root.winfo_width(),self.root.winfo_height(),width,height)
        dialog=tk.Toplevel(self.root);dialog.title(title);dialog.geometry(f'{width}x{height}+{x}+{y}');dialog.configure(bg=BG)
        dialog.transient(self.root);dialog.grab_set();dialog.minsize(min(width,520),min(height,450));effects.dialog_reveal(dialog,lambda:self.motion_enabled.get())
        footer=tk.Canvas(dialog,height=24,bg=BG,highlightthickness=0);footer.pack(side='bottom',fill='x');MotionScene(footer,lambda:self.motion_enabled.get());return dialog

    # คำอธิบาย def Application.signup: สร้างแบบฟอร์มสมัครสมาชิกและตรวจรหัสผ่านยืนยัน
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def signup(self):
        win=self.dialog('EXORA | สร้างบัญชี',560,710);inner=self.scroll_dialog(win)
        self.label(inner,'เริ่มต้นการเดินทางของคุณ',21,bold=True).pack(anchor='w')
        username,_=self.field(inner,'ชื่อผู้ใช้');email,_=self.field(inner,'อีเมล');phone,_=self.field(inner,'เบอร์โทร');password,_=self.field(inner,'รหัสผ่านอย่างน้อย 8 ตัว',secret=True)
        confirm,_=self.field(inner,'ยืนยันรหัสผ่าน',secret=True)
        # คำอธิบาย def Application.signup.save: ตรวจและบันทึกข้อมูลจากฟอร์ม
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: db.register_user
        def save():
            if password.get()!=confirm.get():raise ValueError('รหัสผ่านไม่ตรงกัน')
            ok,message=db.register_user(username.get(),email.get(),password.get(),phone.get())
            if not ok:raise ValueError(message)
            win.destroy();messagebox.showinfo('EXORA',message,parent=self.root)
        self.button(inner,'สร้างบัญชี',save).pack(fill='x',pady=25)

    # คำอธิบาย def Application.forgot_password: สร้างหน้าขอ OTP และตั้งรหัสผ่านใหม่
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def forgot_password(self):
        win=self.dialog('EXORA | ยืนยัน OTP และตั้งรหัสผ่านใหม่',600,720)
        body=self.scroll_dialog(win)
        self.label(body,'กลับเข้าสู่การเดินทางของคุณ',21,bold=True).pack(anchor='w')
        self.label(body,'ส่งรหัสยืนยันไปยังอีเมลที่ลงทะเบียนไว้\nOTP 6 หลัก ใช้ได้ 10 นาที และใช้ได้ครั้งเดียว',10,MUTED,justify='left').pack(anchor='w',pady=12)
        address,email_entry=self.field(body,'อีเมลที่ลงทะเบียน')
        state={'challenge':None,'sending':False,'email':None}
        notice=self.label(body,'',10,MUTED,wraplength=500,justify='left')
        # คำอธิบาย def Application.forgot_password.send: เริ่มส่งอีเมลและแสดงสถานะ
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def send():
            if state['sending']:return
            requested_email=address.get().strip()
            state['sending']=True;send_button.configure(state='disabled',text='กำลังส่ง OTP…')
            # คำอธิบาย def Application.forgot_password.send.completed: แสดงผลหลังงานเบื้องหลังเสร็จ
            # รับค่า: result
            def completed(result):
                state['sending']=False
                if not win.winfo_exists():return
                send_button.configure(state='normal',text='ส่ง / ขอ OTP ใหม่')
                if 'error' in result:notice.configure(text=result['error'],fg='#ab4b3c');return
                state['challenge']=result['challenge_id'];state['email']=requested_email
                notice.configure(text=result['message'],fg=self.green)
                otp_entry.focus_set()
            # คำอธิบาย def Application.forgot_password.send.request: ขอข้อมูลหรือ OTP และจัดผลตอบกลับ
            # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: auth.request_otp
            def request():
                try:return auth.request_otp(requested_email)
                except Exception as error:return {'error':str(error)}
            self.background(request,completed)
        send_button=self.button(body,'ส่ง OTP ไปยังอีเมล',send);send_button.pack(fill='x',pady=15)
        notice.pack(anchor='w',pady=(0,10))
        code,otp_entry=self.field(body,'OTP 6 หลัก')
        new,_=self.field(body,'รหัสผ่านใหม่อย่างน้อย 8 ตัว',secret=True)
        confirm,_=self.field(body,'ยืนยันรหัสผ่านใหม่',secret=True)
        # คำอธิบาย def Application.forgot_password.reset: ตรวจฟอร์มและตั้งรหัสผ่านใหม่
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: auth.reset_with_otp
        def reset():
            if not state['challenge']:raise ValueError('กรุณาขอ OTP ก่อน')
            if address.get().strip()!=state['email']:raise ValueError('อีเมลเปลี่ยนแล้ว กรุณาขอ OTP สำหรับอีเมลนี้ใหม่')
            if new.get()!=confirm.get():raise ValueError('รหัสผ่านใหม่ไม่ตรงกัน')
            auth.reset_with_otp(state['challenge'],code.get(),new.get())
            win.destroy();messagebox.showinfo('EXORA','ตั้งรหัสผ่านใหม่แล้ว กรุณาเข้าสู่ระบบด้วยรหัสใหม่',parent=self.root)
        self.button(body,'ยืนยัน OTP และตั้งรหัสผ่านใหม่',reset).pack(fill='x',pady=25)

    # คำอธิบาย def Application.shell: สร้างเมนูตามสิทธิ์และพื้นที่แสดงหน้าต่างหลัก
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.shop, profiles.get_profile
    def shell(self):
        self.root.unbind('<Configure>')
        self.clear_root();self.shop=profiles.shop();self.green=self.shop['accent'];self.configure_styles()
        self.profile_data=profiles.get_profile(self.current_user['id']);self.current_user['role']=self.profile_data['role']
        sidebar=tk.Frame(self.root,bg=self.green,width=layout.SIDEBAR_WIDTH);sidebar.pack(side='left',fill='y');sidebar.pack_propagate(False)
        menu_canvas=tk.Canvas(sidebar,bg=self.green,highlightthickness=0)
        menu_scroll=ttk.Scrollbar(sidebar,orient='vertical',command=menu_canvas.yview);menu_scroll.pack(side='right',fill='y');menu_canvas.pack(fill='both',expand=True);menu_canvas.configure(yscrollcommand=menu_scroll.set)
        side=tk.Frame(menu_canvas,bg=self.green);menu_item=menu_canvas.create_window((0,0),window=side,anchor='nw',width=layout.SIDEBAR_WIDTH-16)
        side.bind('<Configure>',lambda event:menu_canvas.configure(scrollregion=menu_canvas.bbox('all')))
        menu_canvas.bind('<Configure>',lambda event:menu_canvas.itemconfigure(menu_item,width=event.width))
        brand.header(side,self.shop['name'],dark=True,color=self.green,width=220).pack(anchor='w',padx=15,pady=(25,4))
        nav=[('⌂  หน้าร้าน',self.home),('⇄  แลกเปลี่ยนเงิน',self.exchange_page),('≡  ประวัติรายการ',self.history_page),('◉  โปรไฟล์ของฉัน',self.profile_page),('☎  ติดต่อร้าน',self.contact_page)]
        if self.is_admin_view():nav.extend([('✓  ตรวจสอบรายการ',self.review_page),('▤  สถิติรายการ',self.statistics_page),('▦  จัดการร้าน',self.admin_page)])
        self.nav_buttons={}
        for text,fn in nav:
            button=tk.Button(side,text=text,command=lambda action=fn:self.user_action(action),bg=self.green,fg=WHITE,activebackground='#24725f',activeforeground=WHITE,anchor='w',font=ui_font(11),relief='flat',padx=24,pady=15,cursor='hand2')
            button.pack(fill='x',padx=10,pady=3);self.nav_buttons[fn.__name__]=button
            effects.button_feedback(button,self.green,lambda:self.motion_enabled.get())
            button.bind('<Leave>',lambda e:e.widget.configure(bg='#24725f' if getattr(e.widget,'selected',False) else self.green),add='+')
        bottom=tk.Frame(side,bg=self.green);bottom.pack(side='bottom',fill='x',padx=22,pady=25)
        ornament=tk.Canvas(bottom,height=42,bg=self.green,highlightthickness=0);ornament.pack(fill='x',pady=(0,8));MotionScene(ornament,lambda:self.motion_enabled.get(),theme='car')
        self.label(bottom,self.profile_data['display_name'] or self.current_user['username'],12,WHITE,bg=self.green,bold=True,wraplength=170,justify='left').pack(anchor='w')
        if self.current_user['role']=='admin':
            self.button(bottom,'กลับฝั่งแอดมิน' if self.user_preview else 'ดูหน้าผู้ใช้',self.toggle_user_view,'light').pack(fill='x',pady=(10,8))
            if self.user_preview:self.label(bottom,'โหมดดูตัวอย่าง · บัญชีของคุณ',8,LIME,bg=self.green,wraplength=190).pack(anchor='w',pady=(0,8))
        tk.Checkbutton(bottom,text='เอฟเฟกต์',variable=self.motion_enabled,bg=self.green,fg=WHITE,selectcolor=self.green,activebackground=self.green,activeforeground=WHITE,font=ui_font(8),highlightthickness=0).pack(anchor='w',pady=(0,12))
        self.button(bottom,'ออกจากระบบ',self.login_page,'light').pack(fill='x')
        host=tk.Frame(self.root,bg=BG);host.pack(side='right',fill='both',expand=True)
        self.canvas=tk.Canvas(host,bg=BG,highlightthickness=0);scroll=ttk.Scrollbar(host,orient='vertical',command=self.canvas.yview)
        scroll.pack(side='right',fill='y');self.canvas.pack(side='left',fill='both',expand=True);self.canvas.configure(yscrollcommand=scroll.set)
        self.main_frame=tk.Frame(self.canvas,bg=BG);self.window_id=self.canvas.create_window((0,0),window=self.main_frame,anchor='nw')
        # คำอธิบาย def Application.shell.resize: จัดขนาดหรือตำแหน่งองค์ประกอบให้พอดีกับพื้นที่ปัจจุบัน
        # รับค่า: event
        def resize(event=None):
            width=self.canvas.winfo_width();content=width
            self.canvas.itemconfigure(self.window_id,width=content)
            if not getattr(self,'transition',None) or self.transition.timer is None:self.canvas.coords(self.window_id,max(0,(width-content)/2),0)
            self.canvas.configure(scrollregion=(0,0,width,max(self.canvas.winfo_height(),self.main_frame.winfo_reqheight())))
        self.main_frame.bind('<Configure>',resize);self.canvas.bind('<Configure>',resize)
        self.transition=layout.PageTransition(self.canvas,self.window_id,lambda:self.motion_enabled.get())
        self.root.bind('<MouseWheel>',self.wheel)
        def menu_wheel(event):menu_canvas.yview_scroll(int(-event.delta/120),'units');return 'break'
        stack=[sidebar]
        while stack:
            widget=stack.pop();widget.bind('<MouseWheel>',menu_wheel);stack.extend(widget.winfo_children())

    # คำอธิบาย def Application.wheel: เลื่อนเนื้อหาหน้าหลักด้วยล้อเมาส์เมื่อไม่ใช่ widget ที่มีการเลื่อนของตัวเอง
    # รับค่า: event
    def wheel(self,event):
        if not hasattr(self,'canvas') or not self.canvas.winfo_exists():return
        if isinstance(event.widget,(ttk.Treeview,tk.Text,ttk.Combobox)):return
        if event.widget.winfo_toplevel()!=self.root:return
        self.canvas.yview_scroll(int(-event.delta/120),'units')

    # คำอธิบาย def Application.page: ล้างเนื้อหา ตั้งหัวข้อ เลือกเมนู และเริ่มเอฟเฟกต์เปลี่ยนหน้า
    # รับค่า: title, subtitle | เรียกใช้: profiles.get_profile
    def page(self,title,subtitle):
        if hasattr(self,'transition'):self.transition.cancel()
        self.profile_data=profiles.get_profile(self.current_user['id'])
        self.current_user['role']=self.profile_data['role']
        for w in self.main_frame.winfo_children():w.destroy()
        self.images=[];self.canvas.yview_moveto(0)
        if self.is_admin_view():self.label(self.main_frame,subtitle.upper(),9,MUTED).pack(anchor='w',padx=32,pady=(20,9))
        self.label(self.main_frame,'หน้าร้าน' if title=='เตรียมพร้อมสำหรับทุกการเดินทาง' else title,26,bold=True).pack(anchor='w',padx=30,pady=(20,10))
        route=tk.Canvas(self.main_frame,height=42,bg=BG,highlightthickness=0);route.pack(fill='x',padx=32,pady=(0,10))
        theme={'แลกเปลี่ยนเงิน':'boat','ประวัติรายการ':'train','โปรไฟล์ของฉัน':'car','จัดการร้าน':'car','ตรวจสอบสลิป':'train'}.get(title,'plane')
        MotionScene(route,lambda:self.motion_enabled.get(),theme=theme)
        body=tk.Frame(self.main_frame,bg=BG);body.pack(fill='both',expand=True,padx=30,pady=(0,25))
        active={'เตรียมพร้อมสำหรับทุกการเดินทาง':'home','แลกเปลี่ยนเงิน':'exchange_page','ประวัติรายการ':'history_page','ตรวจสอบสลิป':'review_page','โปรไฟล์ของฉัน':'profile_page','จัดการร้าน':'admin_page','ติดต่อร้าน':'contact_page','สถิติรายการ':'statistics_page','ตรวจสอบรายการ':'review_page'}.get(title)
        for key,button in getattr(self,'nav_buttons',{}).items():button.selected=(key==active);button.configure(bg='#24725f' if button.selected else self.green,fg=LIME if button.selected else WHITE)
        self.transition.start();effects.page_reveal(self.canvas,lambda:self.motion_enabled.get());return body

    # คำอธิบาย def Application.draw_notes: วาดภาพประกอบธนบัตรบน Canvas
    # รับค่า: canvas, dark
    def draw_notes(self,canvas,dark=False):
        canvas.create_oval(80,0,340,260,outline='#7c9c76',width=1)
        canvas.create_polygon(28,30,295,10,310,138,43,158,fill='#174f40',outline='#83aa7c',width=2)
        canvas.create_text(70,57,text='EXORA / EVERY JOURNEY',anchor='w',fill=LIME,font=ui_font(8))
        canvas.create_text(69,107,text='$ 100 USD',anchor='w',fill=LIME,font=('Georgia',24))
        canvas.create_polygon(83,116,344,140,333,250,72,226,fill='#cce3ac',outline='#92af77',width=2)
        canvas.create_text(120,166,text='EXCHANGE · EXPLORE',anchor='w',fill=INK,font=ui_font(8))
        canvas.create_text(115,204,text='€ 100 EUR',anchor='w',fill=INK,font=('Georgia',23))

    # คำอธิบาย def Application.home: จัดหน้าร้าน ตารางราคา ข่าว และเครื่องคำนวณ
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: db.getcur
    def home(self):
        outer=self.page('เตรียมพร้อมสำหรับทุกการเดินทาง','EXORA / YOUR LOCAL EXCHANGE')
        body=tk.Frame(outer,bg=BG);body.grid(row=0,column=0,sticky='nsew',padx=(0,20))
        right=tk.Frame(outer,bg=BG);right.grid(row=0,column=1,sticky='nsew')
        hero=NewsSlideshow(right,lambda:self.motion_enabled.get());hero.pack(fill='x',pady=(0,16))
        converter=self.card(right);converter.pack(fill='x');self.converter(converter)
        self.responsive_columns(outer,body,right)
        strip=tk.Frame(body,bg=BG);strip.pack(fill='x',pady=(0,20))
        for code in ('USD','EUR','JPY','GBP'):
            rate=db.getcur(code);card=self.card(strip);card.pack(side='left',fill='both',expand=True,padx=(0,9))
            self.label(card,f'{SYMBOLS.get(code,"¤")}  {code} / THB',11).pack(anchor='w',padx=16,pady=(15,8))
            value=self.label(card,f'{rate[4]:,.4f}' if rate and rate[4]>0 else '—',21,bold=True);value.pack(anchor='w',padx=16);self.rate_cards.append((value,code))
            self.label(card,'ราคาขาย / 1 หน่วย',9,MUTED).pack(anchor='w',padx=16,pady=(7,15))
        rates=self.card(body);rates.pack(fill='both',expand=True);self.rate_board(rates,height=5)

    # คำอธิบาย def Application.responsive_columns: ปรับสองคอลัมน์เป็นแนวตั้งเมื่อพื้นที่จอแคบ
    # รับค่า: parent, left, right
    def responsive_columns(self,parent,left,right):
        parent.columnconfigure(0,weight=3);parent.columnconfigure(1,weight=1)
        mode={'wide':None}
        # คำอธิบาย def Application.responsive_columns.resize: จัดขนาดหรือตำแหน่งองค์ประกอบให้พอดีกับพื้นที่ปัจจุบัน
        # รับค่า: event
        def resize(event):
            wide=event.width>=1040
            if mode['wide']==wide:return
            mode['wide']=wide
            left.grid_configure(row=0,column=0,sticky='nsew',padx=(0,20) if wide else 0)
            right.grid_configure(row=0 if wide else 1,column=1 if wide else 0,sticky='nsew',padx=0,pady=0 if wide else (18,0))
            parent.columnconfigure(1,weight=1 if wide else 0)
        parent.bind('<Configure>',resize,add='+')

    # คำอธิบาย def Application.table: สร้างตารางพร้อมหัวคอลัมน์และเอฟเฟกต์แถว
    # รับค่า: parent, columns, headings, height, widths
    def table(self,parent,columns,headings,height=10,widths=None):
        host=tk.Frame(parent,bg=WHITE);host.pack(fill='both',expand=True,padx=15,pady=15)
        tree=ttk.Treeview(host,columns=columns,show='headings',height=height,selectmode='browse')
        sy=ttk.Scrollbar(host,orient='vertical',command=tree.yview);sx=ttk.Scrollbar(host,orient='horizontal',command=tree.xview)
        tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);sy.pack(side='right',fill='y');sx.pack(side='bottom',fill='x');tree.pack(fill='both',expand=True)
        for index,(column,heading) in enumerate(zip(columns,headings)):
            tree.heading(column,text=heading);tree.column(column,width=widths[index] if widths else 105,minwidth=70,anchor='w',stretch=True)
        for status,color in [('pending','#a97812'),('approved','#337342'),('rejected','#ab4b3c'),('legacy',MUTED)]:tree.tag_configure(status,foreground=color)
        tree.tag_configure('hover',background='#f2f7e9')
        hover={'row':None}
        # คำอธิบาย def Application.table.highlight: ปรับแถวตารางที่ตัวชี้เมาส์อยู่ โดยรักษาสถานะรายการ
        # รับค่า: event
        def highlight(event):
            row=tree.identify_row(event.y) if event.type!=tk.EventType.Leave else ''
            if row==hover['row']:return
            previous=hover['row']
            if previous and tree.exists(previous):tree.item(previous,tags=tuple(t for t in tree.item(previous,'tags') if t!='hover'))
            if row and tree.exists(row):tree.item(row,tags=tuple(tree.item(row,'tags'))+('hover',))
            hover['row']=row
        tree.bind('<Motion>',highlight,add='+');tree.bind('<Leave>',highlight,add='+')
        return tree

    # คำอธิบาย def Application.rate_board: แสดงราคาซื้อ–ขายและข้อมูลอ้างอิงออนไลน์
    # รับค่า: parent, height | เรียกใช้: online_rates.source_label, online_rates.live_enabled
    def rate_board(self,parent,height=9):
        self.label(parent,'อัตราแลกเปลี่ยนของร้าน',16,bold=True).pack(anchor='w',padx=22,pady=(23,0))
        tree=self.table(parent,('code','name','buy','sell','market'),('สกุลเงิน','ชื่อ','รับซื้อ','ขาย','อ้างอิงออนไลน์'),height,[65,140,85,85,100])
        status=self.label(parent,self.visible_rate_message(),9,MUTED,wraplength=600,justify='left');status.pack(anchor='w',padx=22,pady=(0,8))
        self.label(parent,'THB ต่อ 1 หน่วย · '+(online_rates.source_label() if self.is_admin_view() else ('Twelve Data' if online_rates.live_enabled() else 'Frankfurter · อัตราอ้างอิงรายวัน')),9,MUTED,wraplength=600,justify='left').pack(anchor='w',padx=22,pady=(0,8))
        if self.is_admin_view():self.button(parent,'ตรวจสอบราคาออนไลน์ ↻',self.refresh_rates,'secondary').pack(anchor='w',padx=22,pady=(0,12))
        self.rate_views.append((tree,status));self.update_rate_views();return tree

    # คำอธิบาย def Application.converter: สร้างแบบฟอร์มคำนวณยอดและปุ่มเริ่มทำรายการ
    # รับค่า: parent | เรียกใช้: db.getcurs
    def converter(self,parent):
        inner=tk.Frame(parent,bg=WHITE);inner.pack(fill='both',expand=True,padx=22,pady=22)
        self.label(inner,'คำนวณเงิน',17,bold=True).pack(anchor='w',pady=(0,7))
        codes=[r[1] for r in db.getcurs()];amount,_=self.field(inner,'จำนวนเงินที่ต้องการแลก','1000')
        self.label(inner,'จากสกุลเงิน',10,MUTED).pack(anchor='w',pady=(14,6))
        source=tk.StringVar(value='THB');ttk.Combobox(inner,textvariable=source,values=codes,state='readonly',font=ui_font(11)).pack(fill='x')
        self.label(inner,'เป็นสกุลเงิน',10,MUTED).pack(anchor='w',pady=(14,6))
        target=tk.StringVar(value='USD' if 'USD' in codes else codes[0]);ttk.Combobox(inner,textvariable=target,values=codes,state='readonly',font=ui_font(11)).pack(fill='x')
        result=self.label(inner,'เลือกสกุลเงิน แล้วคำนวณยอด',12,MUTED,justify='left',wraplength=320);result.pack(anchor='w',pady=18)
        holder={'quote':None}
        # คำอธิบาย def Application.converter.calculate: อ่านค่าฟอร์ม คำนวณยอด และแสดงผล
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.quote
        def calculate():
            q=profiles.quote(source.get(),target.get(),amount.get(),actor_id=self.current_user['id']);holder['quote']=q
            result.configure(fg=self.green)
            effects.number_reveal(result,q['to_amount'],lambda value:f"ได้รับ {value:,.2f} {q['to_currency']}\n1 {q['from_currency']} = {q['exchange_rate']:.6f} {q['to_currency']}",lambda:self.motion_enabled.get())
        # คำอธิบาย def Application.converter.start: คำนวณยอดใหม่และเปิดหน้าชำระเงินด้วยข้อมูลยอดนั้น
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def start():calculate();self.payment_dialog(dict(holder['quote']))
        # คำอธิบาย def Application.converter.changed: ยกเลิกผลหรือเอฟเฟกต์เดิมหลังข้อมูลที่ผู้ใช้เลือกเปลี่ยน
        # รับค่า: *args
        def changed(*args):effects.cancel(result,'number');holder['quote']=None;result.configure(text='คำนวณยอดใหม่หลังเปลี่ยนข้อมูล',fg=MUTED)
        for var in (source,target,amount):var.trace_add('write',changed)
        self.button(inner,'คำนวณยอด',calculate,'secondary').pack(fill='x',pady=(0,8))
        self.button(inner,'ทำรายการและแนบสลิป  ↗',start).pack(fill='x')

    # คำอธิบาย def Application.exchange_page: จัดหน้าแลกเปลี่ยนเงินให้แสดงเครื่องคำนวณกับตารางราคา
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def exchange_page(self):
        body=self.page('แลกเปลี่ยนเงิน','START YOUR JOURNEY');body.columnconfigure(0,weight=2);body.columnconfigure(1,weight=3)
        card=self.card(body);card.grid(row=0,column=0,sticky='nsew',padx=(0,20));self.converter(card)
        rates=self.card(body);rates.grid(row=0,column=1,sticky='nsew');self.rate_board(rates)
        self.responsive_columns(body,card,rates)

    # คำอธิบาย def Application.scroll_dialog: สร้างพื้นที่เลื่อนสำหรับแบบฟอร์มที่ยาว
    # รับค่า: win
    def scroll_dialog(self,win):
        canvas=tk.Canvas(win,bg=BG,highlightthickness=0)
        scrollbar=ttk.Scrollbar(win,orient='vertical',command=canvas.yview)
        scrollbar.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        body=tk.Frame(canvas,bg=BG);window=canvas.create_window((0,0),window=body,anchor='nw')
        body.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window,width=e.width))
        win.bind('<MouseWheel>',lambda e:canvas.yview_scroll(int(-e.delta/120),'units'))
        inner=tk.Frame(body,bg=BG);inner.pack(fill='both',expand=True,padx=26,pady=23)
        return inner

    # คำอธิบาย def Application.payment_dialog: แสดงยอด QR บัญชีร้าน ข้อมูลโอน และช่องแนบสลิป
    # รับค่า: data | เรียกใช้: profiles.shop
    def payment_dialog(self,data):
        profile=profiles.get_profile(self.current_user['id'])
        if not profile.get('phone'):raise ValueError('กรุณาเพิ่มเบอร์โทรในโปรไฟล์ก่อนทำรายการ')
        win=self.dialog('EXORA | วิธีชำระและส่งมอบเงิน',920,850);body=self.scroll_dialog(win)
        self.label(body,'ชำระและส่งมอบเงิน',23,bold=True).pack(anchor='w')
        self.label(body,f"{data['from_amount']:,.2f} {data['from_currency']} → {data['to_amount']:,.2f} {data['to_currency']}",18,self.green,bold=True).pack(anchor='w',pady=15)
        if data.get('quote_expires'):self.label(body,'ราคานี้ใช้ได้ถึง '+datetime.fromtimestamp(data['quote_expires']).strftime('%H:%M'),10,MUTED).pack(anchor='w',pady=(0,10))
        settings=profiles.shop();foreign=data['from_currency']!='THB'
        name,_=self.field(body,'ชื่อลูกค้า',profile['display_name'] or profile['username'])
        if foreign:
            self.label(body,'นำเงินต่างประเทศตามยอดข้างต้นมาส่งมอบที่ร้าน\nเจ้าหน้าที่ตรวจสอบเงินและอัตราก่อนอนุมัติ ไม่ต้องโอนบาทซ้ำ',12,self.green,justify='left',wraplength=760).pack(anchor='w',pady=20)
            if settings.get('address'):self.label(body,settings['address'],11,MUTED,wraplength=760).pack(anchor='w')
            # จองรายการส่งมอบเงินต่างประเทศจริงที่ร้าน ไม่สร้างหลักฐานการโอนจำลอง
            def reserve():
                self.ensure_not_preview();number='EX'+datetime.now().strftime('%y%m%d')+'-'+uuid.uuid4().hex[:10].upper()
                payments.submit(number,self.current_user['id'],{**data,'customer_name':name.get(),'customer_phone':profile['phone'],'payment_method':'in_store'},None)
                win.destroy();self.history_page();messagebox.showinfo('EXORA','บันทึกรายการรอตรวจสอบการส่งมอบเงินที่ร้านแล้ว',parent=self.root)
            self.button(body,'บันทึกรายการส่งมอบเงินที่ร้าน',reserve).pack(fill='x',pady=24);return
        tabs=ttk.Notebook(body);tabs.pack(fill='x',pady=15);layout.tab_feedback(tabs,lambda:self.motion_enabled.get())
        qr=tk.Frame(tabs,bg=WHITE);bank=tk.Frame(tabs,bg=WHITE);card=tk.Frame(tabs,bg=WHITE)
        tabs.add(qr,text='QR พร้อมเพย์');tabs.add(bank,text='โอนธนาคาร');tabs.add(card,text='บัตรเครดิต / เดบิต')
        qr_path=Path(db.BASE_DIR)/'EXORA_assets/payments/store_qr.png'
        if qr_path.is_file():
            with Image.open(qr_path) as image:image=image.copy();image.thumbnail((240,310));photo=ImageTk.PhotoImage(image)
            picture=tk.Label(qr,image=photo,bg=WHITE);picture.image=photo;picture.pack(pady=15)
            self.button(qr,'เปิด QR ขนาดเต็ม',lambda:os.startfile(str(qr_path)),'plain').pack()
        else:self.label(qr,'ไม่พบ QR กรุณาติดต่อร้าน',11,MUTED).pack(pady=25)
        self.label(qr,f"ชำระ {data['from_amount']:,.2f} THB และตรวจชื่อผู้รับก่อนโอน",11,self.green).pack(pady=12)
        inner=tk.Frame(bank,bg=WHITE);inner.pack(fill='both',expand=True,padx=22,pady=18)
        receiver=self.card(inner);receiver.pack(fill='x',pady=(0,15))
        recipient='ร้านยังไม่ได้ตั้งบัญชีรับเงิน'
        if all(settings.get(k) for k in ('bank_name','bank_account_name','bank_account_number')):recipient=f"{settings['bank_name']} · {settings['bank_account_name']}\n{settings['bank_account_number']}"
        code,label,color=banks.lookup(settings.get('bank_name',''))
        tk.Label(receiver,text=code,bg=color,fg=WHITE,font=ui_font(11,True),padx=12,pady=12).pack(side='left',padx=12,pady=12)
        self.label(receiver,recipient,12,self.green,bold=True,justify='left',wraplength=620).pack(side='left',padx=10,pady=12)
        self.label(inner,'ธนาคารที่ใช้โอน',10,MUTED).pack(anchor='w',pady=(0,6));values={'payer_bank':banks.selector(inner)}
        grid=tk.Frame(inner,bg=WHITE);grid.pack(fill='x');grid.columnconfigure(0,weight=1);grid.columnconfigure(1,weight=1)
        specs=[('payer_name','ชื่อบัญชีผู้โอน',profile['display_name'] or profile['username']),('payer_account','เลขบัญชีผู้โอน',''),('transfer_amount','ยอดโอน (THB)',str(data['from_amount'])),('transfer_at','วันเวลาโอน (YYYY-MM-DD HH:MM)',datetime.now().strftime('%Y-%m-%d %H:%M')),('transfer_reference','เลขอ้างอิง (ถ้ามี)','')]
        for index,(key,title,value) in enumerate(specs):
            cell=tk.Frame(grid,bg=WHITE);cell.grid(row=index//2,column=index%2,sticky='ew',padx=8);values[key],_=self.field(cell,title,value)
        card_inner=tk.Frame(card,bg=WHITE);card_inner.pack(fill='both',expand=True,padx=25,pady=30)
        tk.Label(card_inner,text='▣  CREDIT / DEBIT',bg=self.green,fg=WHITE,font=ui_font(20,True),padx=30,pady=35).pack(fill='x')
        self.label(card_inner,'ยังไม่เปิดบริการ',17,bold=True).pack(anchor='w',pady=18)
        self.label(card_inner,'ร้านยังไม่ได้เชื่อมผู้ให้บริการรับบัตร\nเมื่อเปิดบริการ จะชำระยอด THB บนหน้าผู้ให้บริการ\nEXORA ไม่เก็บเลขบัตร วันหมดอายุ หรือ CVV',11,MUTED,justify='left',wraplength=750).pack(anchor='w')
        self.button(card_inner,'ชำระด้วยบัตร',lambda:None,state='disabled').pack(anchor='w',pady=20)
        evidence=tk.Frame(body,bg=BG);evidence.pack(fill='x');selected=tk.StringVar(value='ยังไม่ได้แนบสลิป')
        self.label(evidence,'แนบสลิป JPG / PNG ไม่เกิน 10 MB',10,MUTED).pack(anchor='w')
        self.label(evidence,'',10,MUTED,textvariable=selected,wraplength=760).pack(anchor='w',pady=8)
        # คำอธิบาย def choose: เลือกไฟล์ภาพสลิปสำหรับหลักฐานชำระเงินจริง
        def choose():
            file=filedialog.askopenfilename(parent=win,filetypes=[('ภาพสลิป','*.jpg *.jpeg *.png')])
            if file:selected.set(file)
        self.button(evidence,'เลือกหลักฐาน',choose,'secondary').pack(anchor='w')
        # คำอธิบาย def submit: ตรวจช่องทางและหลักฐาน แล้วส่งรายการโดยใช้เบอร์โทรจากบัญชี
        def submit():
            self.ensure_not_preview();index=tabs.index(tabs.select())
            if index==2:raise ValueError('ช่องทางบัตรยังไม่เปิดบริการ')
            if not Path(selected.get()).is_file():raise ValueError('กรุณาแนบสลิป')
            if index==0 and not qr_path.is_file():raise ValueError('ยังไม่มี QR ร้าน')
            payload={**data,'customer_name':name.get().strip(),'customer_phone':profile['phone'],'payment_method':'qr' if index==0 else 'bank'}
            if index==1:
                if values['payer_bank'].get()=='เลือกธนาคาร':raise ValueError('กรุณาเลือกธนาคารผู้โอน')
                payload.update({k:v.get().strip() for k,v in values.items()})
            number='EX'+datetime.now().strftime('%y%m%d')+'-'+uuid.uuid4().hex[:10].upper()
            payments.submit(number,self.current_user['id'],payload,selected.get());win.destroy();self.history_page()
            messagebox.showinfo('EXORA','บันทึกรายการรอตรวจสอบแล้ว',parent=self.root)
        submit_button=self.button(evidence,'ส่งหลักฐานให้เจ้าหน้าที่ตรวจสอบ',submit);submit_button.pack(fill='x',pady=20)
        # คำอธิบาย def switched: ซ่อนการแนบหลักฐานเมื่อเลือกช่องทางบัตรที่ยังไม่เปิดบริการ
        def switched(event):
            if tabs.index(tabs.select())==2:evidence.pack_forget()
            else:evidence.pack(fill='x')
        tabs.bind('<<NotebookTabChanged>>',switched,add='+')

    # คำอธิบาย def Application.history_page: เปิดหน้าประวัติรายการ
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def history_page(self):self.show_history(False)
    # คำอธิบาย def Application.review_page: เปิดหน้ารายการที่รอแอดมินตรวจสลิป
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def review_page(self):self.show_history(True)
    # คำอธิบาย def Application.show_history: สร้างหน้าค้นหา ตารางสถานะ และปุ่มรายละเอียดรายการ
    # รับค่า: pending
    def show_history(self,pending):
        if pending and not self.is_admin_view():raise PermissionError('เฉพาะ admin')
        body=self.page('ตรวจสอบรายการ' if pending else 'ประวัติรายการ','PAYMENT REVIEW' if pending else 'YOUR EXCHANGE JOURNAL')
        self.pending_only=pending;toolbar=tk.Frame(body,bg=BG);toolbar.pack(fill='x',pady=(0,16))
        self.search=tk.StringVar();ttk.Entry(toolbar,textvariable=self.search,width=28,font=ui_font(11)).pack(side='left',padx=(0,12))
        self.status_filter=tk.StringVar(value='ทุกสถานะ')
        ttk.Combobox(toolbar,textvariable=self.status_filter,values=['ทุกสถานะ']+list(STATUS.values()),state='readonly',width=16).pack(side='left',padx=(0,12))
        self.button(toolbar,'ค้นหา / รีเฟรช',self.load_history,'secondary').pack(side='left')
        card=self.card(body);card.pack(fill='both',expand=True)
        cols=('no','user','type','from','amount','to','result','rate','date','status')
        self.history_tree=self.table(card,cols,('เลขรายการ','ผู้ใช้','ประเภท','จาก','จำนวน','เป็น','ได้รับ','อัตรา','วันที่','สถานะ'),12,[190,100,70,70,100,70,100,100,155,110])
        self.history_tree.bind('<Double-1>',lambda e:self.safe(self.selected_detail))
        self.count_label=self.label(body,'',10,MUTED);self.count_label.pack(anchor='w',pady=12)
        self.button(body,'ดูรายละเอียด / สลิป / PDF',self.selected_detail).pack(anchor='w')
        self.load_history()

    # คำอธิบาย def Application.load_history: อ่านรายการตามสิทธิ์และตัวกรอง แล้วแสดงในตาราง
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: payments.list_transactions
    def load_history(self):
        rows=payments.list_transactions(self.current_user['id'],self.search.get(),self.pending_only,own_only=self.user_preview)
        for item in self.history_tree.get_children():self.history_tree.delete(item)
        count=0
        for row in rows:
            status=row[9]
            if self.status_filter.get()!='ทุกสถานะ' and STATUS.get(status)!=self.status_filter.get():continue
            display=list(row);display[4]=f'{row[4]:,.2f}';display[6]=f'{row[6]:,.2f}';display[7]=f'{row[7]:.6f}';display[9]=STATUS.get(status,status)
            self.history_tree.insert('','end',values=display,tags=(status,));count+=1
        self.count_label.configure(text=f'{count} รายการ')

    # คำอธิบาย def Application.selected_detail: อ่านเลขรายการที่เลือกและเปิดรายละเอียด
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def selected_detail(self):
        selection=self.history_tree.selection()
        if not selection:raise ValueError('กรุณาเลือกรายการ')
        self.detail(self.history_tree.item(selection[0],'values')[0])

    # คำอธิบาย def Application.detail: แสดงข้อมูลรายการ สลิป ผลตรวจสอบ และตัวเลือก PDF/อีเมลตามสิทธิ์
    # รับค่า: number | เรียกใช้: payments.get_transaction, payments.slip_path, payments.get_audit
    def detail(self,number):
        row=payments.get_transaction(number,self.current_user['id'])
        if self.user_preview and row['user_id']!=self.current_user['id']:raise PermissionError('โหมดดูหน้าผู้ใช้แสดงเฉพาะรายการของบัญชีคุณ')
        win=self.dialog(f'EXORA | {number}',900,790)
        body=self.scroll_dialog(win)
        self.label(body,number,23,bold=True).pack(anchor='w');self.label(body,STATUS.get(row['payment_status'],row['payment_status']),11,self.green,bold=True).pack(anchor='w',pady=(8,16))
        split=tk.Frame(body,bg=BG);split.pack(fill='both',expand=True);split.columnconfigure(0,weight=1);split.columnconfigure(1,weight=1)
        left=tk.Frame(split,bg=BG);left.grid(row=0,column=0,sticky='nsew',padx=(0,20));right=tk.Frame(split,bg=BG);right.grid(row=0,column=1,sticky='nsew')
        fields=[('ลูกค้า',row['customer_name']),('เบอร์โทร',row['customer_phone']),('แลกจาก',f"{row['from_amount']:,.2f} {row['from_currency']}"),('ได้รับ',f"{row['to_amount']:,.2f} {row['to_currency']}"),('อัตรา',f"{row['exchange_rate']:.6f}"),('วันที่',row['transaction_date']),('ตรวจสอบเมื่อ',row['reviewed_at']),('หมายเหตุ',row['review_note'])]
        fields.insert(2,('วิธีชำระเงิน',{'qr':'QR พร้อมเพย์','bank':'โอนบัญชีธนาคาร','in_store':'ส่งมอบเงินต่างประเทศที่ร้าน','card':'บัตรเครดิต/เดบิต','legacy':'ข้อมูลเดิม'}.get(row.get('payment_method'),'ข้อมูลเดิม')))
        if row.get('payment_method')=='bank':
            fields.extend([('ธนาคาร / ชื่อผู้โอน',f"{row['payer_bank']} / {row['payer_name']}"),('เลขบัญชีผู้โอน',row['payer_account']),
                           ('จำนวนเงินโอน',f"{row['transfer_amount']:,.2f} THB"),('โอนเมื่อ / อ้างอิง',f"{row['transfer_at']} / {row['transfer_reference'] or '—'}"),
                           ('บัญชีร้านที่รับเงิน',f"{row['recipient_bank']} / {row['recipient_name']} / {row['recipient_account']}")])
        for title,value in fields:
            self.label(left,title,9,MUTED).pack(anchor='w',pady=(8,2));self.label(left,value or '—',11,wraplength=350,justify='left').pack(anchor='w')
        self.label(right,'หลักฐานการชำระเงิน',12,bold=True).pack(anchor='w',pady=(0,14))
        if row['slip_path']:
            try:
                with Image.open(payments.slip_path(row)) as image:
                    image=image.copy();image.thumbnail((370,360));photo=ImageTk.PhotoImage(image)
                label=tk.Label(right,image=photo,bg=WHITE);label.image=photo;label.pack()
                self.button(right,'เปิดสลิปขนาดเต็ม',lambda:os.startfile(str(payments.slip_path(row))),'plain').pack(anchor='w')
            except Exception as error:self.label(right,str(error),10,'#ab4b3c',wraplength=370).pack(anchor='w')
        else:self.label(right,'ส่งมอบเงินที่หน้าร้าน' if row.get('payment_method')=='in_store' else 'รายการนี้ไม่มีภาพสลิป',11,MUTED).pack(anchor='w')
        audit=payments.get_audit(number,self.current_user['id']);audit_text='\n'.join(f"{a['created_at']} · {STATUS.get(a['action'],{'submitted':'แนบสลิป','resubmitted':'แนบสลิปใหม่'}.get(a['action'],a['action']))}" for a in audit[-4:])
        self.label(right,audit_text or 'ประวัติจากระบบเดิม',9,MUTED,wraplength=370,justify='left').pack(anchor='w',pady=15)
        actions=tk.Frame(body,bg=BG);actions.pack(fill='x',pady=(20,8))
        self.button(actions,'บันทึก PDF',lambda:self.export_pdf(number),'secondary').pack(side='left',padx=(0,9))
        # คำอธิบาย def Application.detail.reload: โหลดตารางและรายละเอียดใหม่หลังสถานะรายการเปลี่ยน
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def reload():win.destroy();self.load_history();self.detail(number)
        if row['payment_status']=='pending' and self.is_admin_view():
            # คำอธิบาย def Application.detail.review: ตรวจสิทธิ์ admin และเปลี่ยนรายการ pending เป็น approved/rejected
            # รับค่า: status | เรียกใช้: payments.review, receipts.ensure_receipt
            def review(status):
                if status=='approved':
                    if not messagebox.askyesno('อนุมัติรายการ','ตรวจสอบยอดและการรับชำระหรือส่งมอบเงินจริงกับร้านแล้วใช่หรือไม่?\nการอนุมัตินี้ไม่ได้เชื่อมต่อธนาคาร',parent=win):return
                    note='ตรวจสอบการส่งมอบเงินต่างประเทศที่ร้านแล้ว' if row.get('payment_method')=='in_store' else 'ตรวจสอบสลิปโดยเจ้าหน้าที่'
                else:
                    # คำอธิบาย import: นำเข้า simpledialog: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
                    from tkinter import simpledialog
                    note=simpledialog.askstring('ปฏิเสธรายการ','ระบุเหตุผลที่ปฏิเสธ',parent=win)
                    if note is None:return
                actor=self.current_user['id']
                payments.review(number,actor,status,note);reload()
                if status=='approved':
                    # คำอธิบาย def Application.detail.review.completed: แสดงผลหลังงานเบื้องหลังเสร็จ
                    # รับค่า: result
                    def completed(result):
                        messagebox.showinfo('EXORA','สร้างใบเสร็จธีม EXORA แล้ว กดส่งใบเสร็จในรายละเอียดเพื่อส่งให้ผู้ทำรายการ',parent=self.root)
                    self.background(lambda:receipts.ensure_receipt(number,actor),completed)
            self.button(actions,'✓ อนุมัติ',lambda:review('approved')).pack(side='left',padx=(0,9))
            self.button(actions,'ปฏิเสธ',lambda:review('rejected'),'danger').pack(side='left')
        if row['payment_status']=='rejected' and row['user_id']==self.current_user['id'] and row.get('payment_method')!='in_store':
            # คำอธิบาย def Application.detail.resubmit: เลือกหลักฐานใหม่สำหรับรายการที่ถูกปฏิเสธ
            # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: payments.replace_slip
            def resubmit():
                self.ensure_not_preview()
                source=filedialog.askopenfilename(parent=win,title='แนบสลิปใหม่',filetypes=[('รูปภาพ','*.jpg *.jpeg *.png')])
                if source:payments.replace_slip(number,self.current_user['id'],source);reload()
            self.button(actions,'แนบสลิปใหม่',resubmit).pack(side='left')
        if row['payment_status']=='approved':
            delivery=receipts.delivery_status(number,self.current_user['id'])
            if delivery:self.label(body,'ใบเสร็จอัตโนมัติ: '+{'sent':'ส่งแล้ว','sending':'กำลังส่ง','failed':'ส่งไม่สำเร็จ'}.get(delivery['status'],delivery['status'])+' · '+delivery['recipient'],10,MUTED,wraplength=700).pack(anchor='w',pady=8)
            if self.is_admin_view():self.label(body,'ผู้ส่ง: '+email_settings.SENDER,10,MUTED).pack(anchor='w',pady=8)
            conn=db.getconnect()
            try:owner=conn.execute('SELECT email FROM users WHERE id=?',(row['user_id'],)).fetchone()
            finally:conn.close()
            self.label(body,'ส่งไปที่: '+((owner[0] or 'ยังไม่มีอีเมลในโปรไฟล์') if owner else 'ไม่พบบัญชีผู้ทำรายการ'),11,self.green,wraplength=700).pack(anchor='w',pady=8)
            mail_status=self.label(body,'',10,MUTED,wraplength=700,justify='left');mail_status.pack(anchor='w',pady=8)
            mail_state={'sending':False}
            # คำอธิบาย def Application.detail.send: เริ่มส่งอีเมลและแสดงสถานะ
            # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
            def send():
                self.ensure_not_preview()
                if mail_state['sending']:return
                recipient=(owner[0] or '').strip() if owner else ''
                if not recipient:raise ValueError('ให้ผู้ทำรายการเพิ่มอีเมลในโปรไฟล์ก่อนส่งใบเสร็จ')
                if not email_settings.configured():
                    raise ValueError('ระบบอีเมลยังไม่พร้อม กรุณาติดต่อร้าน' if not self.is_admin_view() else 'ตั้ง EXORA_GMAIL_APP_PASSWORD ของ '+email_settings.SENDER+' ก่อนส่งใบเสร็จ')
                actor=self.current_user['id']
                mail_state['sending']=True;mail_button.configure(state='disabled',text='กำลังส่งใบเสร็จ…');mail_status.configure(text='กำลังสร้าง PDF และส่งอีเมล')
                # คำอธิบาย def Application.detail.send.work: ทำงานเบื้องหลังและส่งผลกลับ
                # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: receipts.send_to_user
                def work():
                    try:
                        result=receipts.send_to_user(number,actor)
                        return {'ok':result['status']=='sent','message':result['message'],'error':result['message']}
                    except Exception as error:return {'error':str(error)}
                # คำอธิบาย def Application.detail.send.completed: แสดงผลหลังงานเบื้องหลังเสร็จ
                # รับค่า: result
                def completed(result):
                    mail_state['sending']=False
                    if not win.winfo_exists():return
                    mail_button.configure(state='normal',text='ส่งใบเสร็จทางอีเมล  ↗')
                    mail_status.configure(text=(result.get('message') or 'ส่งใบเสร็จพร้อม PDF ไปยัง '+recipient) if result.get('ok') else ('ส่งไม่สำเร็จ: '+result['error']),fg=self.green if result.get('ok') else '#ab4b3c')
                self.background(work,completed)
            mail_button=self.button(body,'ส่งใบเสร็จทางอีเมล  ↗',send);mail_button.pack(anchor='w',pady=10)

    # คำอธิบาย def Application.export_pdf: จัดเตรียมและบันทึก PDF รายการไปยังตำแหน่งที่ระบุ
    # รับค่า: number | เรียกใช้: payments.get_transaction, receipts.ensure_receipt, receipts.export_pdf
    def export_pdf(self,number):
        path=filedialog.asksaveasfilename(parent=self.root,title='บันทึก PDF',defaultextension='.pdf',initialfile=number+'.pdf',filetypes=[('PDF','*.pdf')])
        if path:
            row=payments.get_transaction(number,self.current_user['id'])
            if row['payment_status']=='approved':
                # คำอธิบาย import: นำเข้า shutil: shutil — คัดลอกไฟล์หลักฐานและไฟล์ประกอบ
                import shutil
                saved=receipts.ensure_receipt(number,self.current_user['id'])
                if saved.resolve()!=Path(path).resolve():shutil.copy2(saved,path)
            else:receipts.export_pdf(number,self.current_user['id'],path)
            messagebox.showinfo('EXORA','บันทึก PDF แล้ว',parent=self.root)

    # คำอธิบาย def Application.profile_page: สร้างหน้าแก้ข้อมูล รูปโปรไฟล์ สี และรหัสผ่าน
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.get_profile
    def profile_page(self):
        body=self.page('โปรไฟล์ของฉัน','MAKE IT YOURS');profile=profiles.get_profile(self.current_user['id'])
        summary=self.card(body);summary.pack(fill='x',pady=(0,20));strip=tk.Frame(summary,bg=WHITE);strip.pack(fill='x',padx=22,pady=20)
        avatar=profile.get('avatar_path')
        if avatar:
            path=(Path(db.BASE_DIR)/avatar).resolve()
            if path.is_relative_to(Path(db.BASE_DIR).resolve()/'EXORA_assets'/'avatars') and path.is_file():
                with Image.open(path) as im:im=im.copy();im.thumbnail((85,85));photo=ImageTk.PhotoImage(im)
                self.images.append(photo);tk.Label(strip,image=photo,bg=WHITE).pack(side='left',padx=(0,20))
        self.label(strip,profile['display_name'] or profile['username'],22,profile.get('accent') or self.green,bold=True).pack(anchor='w')
        self.label(strip,f"@{profile['username']}",10,MUTED).pack(anchor='w',pady=8)
        grid=tk.Frame(body,bg=BG);grid.pack(fill='x');grid.columnconfigure(0,weight=1);grid.columnconfigure(1,weight=1)
        card=self.card(grid);card.grid(row=0,column=0,sticky='nsew',padx=(0,20));inner=tk.Frame(card,bg=WHITE);inner.pack(fill='both',expand=True,padx=25,pady=24)
        self.label(inner,'ข้อมูลส่วนตัว',17,bold=True).pack(anchor='w')
        values={}
        for key,label in [('display_name','ชื่อที่แสดง'),('email','อีเมล'),('phone','เบอร์โทร')]:values[key],_=self.field(inner,label,profile.get(key) or (profile['username'] if key=='display_name' else ''))
        accent=tk.StringVar(value=profile.get('accent') or self.green);avatar_file={'path':None}
        # คำอธิบาย def Application.profile_page.color: เลือกสีจากกล่องเลือกสี
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def color():
            chosen=colorchooser.askcolor(accent.get(),parent=self.root)[1]
            if chosen:accent.set(chosen)
        # คำอธิบาย def Application.profile_page.choose: เลือกไฟล์จากกล่องเลือกไฟล์
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def choose():
            file=filedialog.askopenfilename(parent=self.root,title='รูปโปรไฟล์',filetypes=[('รูปภาพ','*.jpg *.jpeg *.png')])
            if file:avatar_file['path']=file;avatar_status.configure(text=Path(file).name)
        row=tk.Frame(inner,bg=WHITE);row.pack(fill='x',pady=18)
        self.button(row,'เลือกสี',color,'secondary').pack(side='left',padx=(0,10));self.button(row,'เลือกรูปโปรไฟล์',choose,'secondary').pack(side='left')
        avatar_status=self.label(inner,'',9,MUTED);avatar_status.pack(anchor='w')
        # คำอธิบาย def Application.profile_page.save: ตรวจและบันทึกข้อมูลจากฟอร์ม
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.save_profile
        def save():
            self.ensure_not_preview()
            profiles.save_profile(self.current_user['id'],**{key:value.get() for key,value in values.items()},bio=profile.get('bio') or '',accent=accent.get(),avatar_source=avatar_file['path'])
            self.shell();self.profile_page();messagebox.showinfo('EXORA','บันทึกโปรไฟล์แล้ว',parent=self.root)
        self.button(inner,'บันทึกโปรไฟล์  ↗',save).pack(fill='x',pady=(15,0))
        card=self.card(grid);card.grid(row=0,column=1,sticky='nsew');inner=tk.Frame(card,bg=WHITE);inner.pack(fill='both',expand=True,padx=25,pady=24)
        self.label(inner,'เปลี่ยนรหัสผ่าน',17,bold=True).pack(anchor='w');old,_=self.field(inner,'รหัสผ่านปัจจุบัน',secret=True);new,_=self.field(inner,'รหัสผ่านใหม่อย่างน้อย 8 ตัว',secret=True);confirm,_=self.field(inner,'ยืนยันรหัสผ่านใหม่',secret=True)
        # คำอธิบาย def Application.profile_page.password: ตรวจและเปลี่ยนรหัสผ่านจากฟอร์ม
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.change_password
        def password():
            if new.get()!=confirm.get():raise ValueError('รหัสผ่านใหม่ไม่ตรงกัน')
            self.ensure_not_preview();profiles.change_password(self.current_user['id'],old.get(),new.get());self.current_user['password_change_required']=False;old.set('');new.set('');confirm.set('');messagebox.showinfo('EXORA','เปลี่ยนรหัสผ่านแล้ว',parent=self.root)
        self.button(inner,'เปลี่ยนรหัสผ่าน',password,'secondary').pack(fill='x',pady=22)

    # คำอธิบาย def Application.contact_page: แสดงเฉพาะข้อมูลติดต่อร้านที่กรอกไว้และปุ่มเปิดลิงก์
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.shop
    def contact_page(self):
        body=self.page('ติดต่อร้าน','CONTACT');settings=profiles.shop()
        card=self.card(body);card.pack(fill='x',pady=8)
        inner=tk.Frame(card,bg=WHITE);inner.pack(fill='x',padx=28,pady=24)
        self.label(inner,settings.get('name') or 'EXORA',24,bold=True).pack(anchor='w',pady=(0,18))
        published=False
        for key,title in contact.FIELDS:
            value=settings.get(key,'').strip()
            if not value:continue
            published=True;self.label(inner,title,10,MUTED).pack(anchor='w',pady=(12,4))
            self.label(inner,value,12,wraplength=850,justify='left').pack(anchor='w')
            if key in contact.LINKS:self.button(inner,'เปิดแผนที่' if key=='contact_map' else 'เปิดลิงก์',lambda url=value:webbrowser.open(url),'secondary').pack(anchor='w',pady=8)
        if not published:self.label(inner,'ร้านยังไม่ได้เพิ่มข้อมูลติดต่อ',12,MUTED).pack(anchor='w')

    # คำอธิบาย def Application.contact_admin: สร้างแบบฟอร์มให้ admin บันทึกข้อมูลติดต่อร้าน
    # รับค่า: parent | เรียกใช้: profiles.shop
    def contact_admin(self,parent):
        form=self.scroll_dialog(parent);settings=profiles.shop();values={}
        self.label(form,'ข้อมูลติดต่อร้าน',20,bold=True).pack(anchor='w',pady=(12,8))
        for key,title in contact.FIELDS:values[key],_=self.field(form,title+(' (https://...)' if key in contact.LINKS else ''),settings.get(key,''))
        # คำอธิบาย def Application.contact_admin.save: ตรวจและบันทึกข้อมูลจากฟอร์ม
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: contact.save
        def save():
            self.ensure_not_preview();contact.save(self.current_user['id'],{key:value.get() for key,value in values.items()})
            messagebox.showinfo('EXORA','บันทึกข้อมูลติดต่อร้านแล้ว',parent=self.root)
        self.button(form,'บันทึกข้อมูลติดต่อ',save).pack(anchor='w',pady=22)
        canvas=form.master.master
        # คำอธิบาย def Application.contact_admin.scroll: เลื่อนแบบฟอร์มติดต่อร้านและหยุด event ไม่ให้ไปเลื่อนหน้าหลัก
        # รับค่า: event
        def scroll(event):canvas.yview_scroll(int(-event.delta/120),'units');return 'break'
        pending=[parent]
        while pending:
            widget=pending.pop();widget.bind('<MouseWheel>',scroll);pending.extend(widget.winfo_children())

    # คำอธิบาย def Application.admin_page: สร้างแท็บจัดการร้าน ราคา ผู้ใช้ ข่าว และข้อมูลติดต่อ
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.shop, profiles.list_users
    def admin_page(self):
        if not self.is_admin_view():raise PermissionError('เฉพาะ admin')
        body=self.page('จัดการร้าน','EXORA MANAGEMENT')
        tabs=ttk.Notebook(body);tabs.pack(fill='both',expand=True);layout.tab_feedback(tabs,lambda:self.motion_enabled.get())
        store=tk.Frame(tabs,bg=WHITE);rates=tk.Frame(tabs,bg=WHITE);users=tk.Frame(tabs,bg=WHITE)
        tabs.add(store,text='หน้าร้าน');tabs.add(rates,text='อัตราแลกเปลี่ยน');tabs.add(users,text='ผู้ใช้งาน')
        news_tab=tk.Frame(tabs,bg=WHITE);tabs.add(news_tab,text='ข่าวหน้าแรก');self.news_admin(news_tab)
        contact_tab=tk.Frame(tabs,bg=WHITE);tabs.add(contact_tab,text='ติดต่อร้าน');self.contact_admin(contact_tab)
        form=tk.Frame(store,bg=WHITE);form.pack(fill='x',padx=28,pady=25);values={}
        fields=tk.Frame(form,bg=WHITE);fields.pack(fill='x');fields.columnconfigure(0,weight=1);fields.columnconfigure(1,weight=1)
        for index,(key,label) in enumerate([('name','ชื่อร้าน'),('tagline','ข้อความแนะนำ'),('phone','เบอร์โทรร้าน'),('address','ที่อยู่'),('hours','เวลาเปิดบริการ'),('payment_note','คำแนะนำก่อนแนบสลิป'),('bank_name','บัญชีธนาคารรับเงิน: ชื่อธนาคาร'),('bank_account_name','ชื่อบัญชีรับเงินของร้าน'),('bank_account_number','เลขบัญชีรับเงินของร้าน')]):
            cell=tk.Frame(fields,bg=WHITE);cell.grid(row=index//2,column=index%2,sticky='ew',padx=(0,20) if index%2==0 else 0)
            values[key],_=self.field(cell,label,self.shop.get(key))
        accent=tk.StringVar(value=self.green)
        # คำอธิบาย def Application.admin_page.color: เลือกสีจากกล่องเลือกสี
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def color():
            value=colorchooser.askcolor(accent.get(),parent=self.root)[1]
            if value:accent.set(value)
        self.button(form,'เลือกสีร้าน',color,'secondary').pack(anchor='w',pady=15)
        # คำอธิบาย def Application.admin_page.save: ตรวจและบันทึกข้อมูลจากฟอร์ม
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.save_shop
        def save():
            profiles.save_shop(self.current_user['id'],{**{k:v.get() for k,v in values.items()},'accent':accent.get()});self.shell();self.admin_page();messagebox.showinfo('EXORA','บันทึกหน้าร้านแล้ว',parent=self.root)
        self.button(form,'บันทึกหน้าร้าน  ↗',save).pack(anchor='w',pady=8)
        self.label(form,'ผู้ส่ง: '+email_settings.SENDER+' · '+('พร้อมส่ง OTP / ใบเสร็จ' if email_settings.configured() else 'ยังไม่ได้ตั้ง Gmail App Password'),10,MUTED).pack(anchor='w',pady=15)
        tree=self.rate_board(rates,height=9)
        config=profiles.shop();auto=tk.BooleanVar(value=config.get('online_pricing')=='1')
        controls=tk.Frame(rates,bg=WHITE);controls.pack(fill='x',padx=22,pady=8)
        tk.Checkbutton(controls,text='ใช้ราคาออนไลน์คำนวณราคาซื้อ–ขายอัตโนมัติ',variable=auto,bg=WHITE,font=ui_font(10)).pack(side='left')
        self.label(controls,'ส่วนต่าง %',10,MUTED).pack(side='left',padx=10)
        spread=tk.StringVar(value=config.get('online_spread','2'));ttk.Entry(controls,textvariable=spread,width=6).pack(side='left')
        # คำอธิบาย def Application.admin_page.save_online: ยืนยันและบันทึกโหมดกำหนดราคาจากข้อมูลออนไลน์
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: online_rates.settings
        def save_online():
            if auto.get() and not messagebox.askyesno('EXORA','ราคาซื้อ–ขายของร้านจะเปลี่ยนตามข้อมูลออนไลน์และส่วนต่างที่กำหนด\nยืนยันเปิดใช้ราคาซื้อ–ขายอัตโนมัติ?',parent=self.root):return
            online_rates.settings(self.current_user['id'],auto.get(),spread.get());self.refresh_rates()
        self.button(controls,'บันทึก',save_online,'secondary').pack(side='left',padx=12)
        # คำอธิบาย def Application.admin_page.rate_form: เปิดฟอร์มเพิ่มหรือแก้ราคาสกุลเงิน
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.shop().get, profiles.shop, db.getcur
        def rate_form():
            if profiles.shop().get('online_pricing')=='1':raise ValueError('กรุณาปิดราคาซื้อ–ขายอัตโนมัติก่อนแก้ไขราคาเอง')
            selection=tree.selection();code=tree.item(selection[0],'values')[0] if selection else '';existing=db.getcur(code) if code else None
            win=self.dialog('EXORA | อัตราแลกเปลี่ยน',510,520);inner=tk.Frame(win,bg=BG);inner.pack(fill='both',expand=True,padx=28,pady=25)
            cv,ce=self.field(inner,'รหัสสกุลเงิน 3 ตัว',code);nv,_=self.field(inner,'ชื่อสกุลเงิน',existing[2] if existing else '');bv,_=self.field(inner,'ราคาที่ร้านรับซื้อ (THB ต่อ 1 หน่วย)',existing[3] if existing else '');sv,_=self.field(inner,'ราคาที่ร้านขาย (THB ต่อ 1 หน่วย)',existing[4] if existing else '')
            if code:ce.configure(state='readonly')
            # คำอธิบาย def Application.admin_page.rate_form.update: บันทึกการเปลี่ยนแปลงและโหลดหน้าจอใหม่
            # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.set_rate
            def update():profiles.set_rate(self.current_user['id'],cv.get(),nv.get(),bv.get(),sv.get());win.destroy();self.admin_page()
            self.button(inner,'บันทึกอัตรา',update).pack(fill='x',pady=25)
        self.button(rates,'แก้ไขที่เลือก / เพิ่มสกุลเงิน',rate_form).pack(anchor='w',padx=22,pady=(0,24))
        utree=self.table(users,('id','username','email','role','status'),('ID','ชื่อผู้ใช้','อีเมล','สิทธิ์','สถานะ'),10,[60,160,220,100,100])
        for user in profiles.list_users(self.current_user['id']):utree.insert('','end',values=[v or '' for v in user])
        # คำอธิบาย def Application.admin_page.user_form: เปิดฟอร์มแก้สิทธิ์และสถานะบัญชีที่เลือก
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def user_form():
            selection=utree.selection()
            if not selection:raise ValueError('กรุณาเลือกบัญชี')
            uid,username,email,role,status=utree.item(selection[0],'values');win=self.dialog('EXORA | สิทธิ์ผู้ใช้งาน',500,420);inner=tk.Frame(win,bg=BG);inner.pack(fill='both',expand=True,padx=28,pady=25)
            self.label(inner,username,20,bold=True).pack(anchor='w');rv=tk.StringVar(value=role);sv=tk.StringVar(value=status)
            self.label(inner,'สิทธิ์',10,MUTED).pack(anchor='w',pady=(22,8));ttk.Combobox(inner,textvariable=rv,values=['user','staff','admin'],state='readonly').pack(fill='x')
            self.label(inner,'สถานะ',10,MUTED).pack(anchor='w',pady=(22,8));ttk.Combobox(inner,textvariable=sv,values=['active','inactive','banned'],state='readonly').pack(fill='x')
            # คำอธิบาย def Application.admin_page.user_form.update: บันทึกการเปลี่ยนแปลงและโหลดหน้าจอใหม่
            # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: profiles.update_user
            def update():profiles.update_user(self.current_user['id'],int(uid),rv.get(),sv.get());win.destroy();self.admin_page()
            self.button(inner,'บันทึกสิทธิ์',update).pack(fill='x',pady=28)
        self.button(users,'จัดการสิทธิ์ที่เลือก',user_form).pack(anchor='w',padx=22,pady=(0,25))
        actions=tk.Frame(users,bg=WHITE);actions.pack(fill='x',padx=22,pady=8)
        # คำอธิบาย def Application.admin_page.manage_account: ดำเนินการแบน ปลดแบน หรือลบบัญชีที่แอดมินเลือก
        # รับค่า: action | เรียกใช้: profiles.delete_user, profiles.update_user
        def manage_account(action):
            selected=utree.selection()
            if not selected:raise ValueError('กรุณาเลือกบัญชี')
            uid,username,email,role,status=utree.item(selected[0],'values');uid=int(uid)
            if action=='delete':
                if not messagebox.askyesno('ลบผู้ใช้',f'ลบบัญชี {username}?\nบัญชีจะเข้าใช้งานไม่ได้ โดยเก็บประวัติรายการไว้',parent=self.root):return
                profiles.delete_user(self.current_user['id'],uid)
            else:profiles.update_user(self.current_user['id'],uid,role,'banned' if action=='ban' else 'active')
            self.admin_page()
        for text,action in [('แบนผู้ใช้','ban'),('ปลดแบน / เปิดใช้งาน','restore'),('ลบผู้ใช้','delete')]:
            self.button(actions,text,lambda action=action:manage_account(action),'danger' if action!='restore' else 'secondary').pack(side='left',padx=(0,8))

    # คำอธิบาย def Application.news_admin: สร้างรายการข่าวและคำสั่งเพิ่ม ลำดับ แสดง/ซ่อน และลบ
    # รับค่า: parent
    def news_admin(self,parent):
        self.label(parent,'ข่าวการเงินโลก · สไลด์หน้าแรก',20,bold=True).pack(anchor='w',padx=22,pady=(20,8))
        self.label(parent,'เพิ่มภาพข่าว JPG / PNG ไม่เกิน 10 MB',10,MUTED).pack(anchor='w',padx=22,pady=(0,10))
        tree=self.table(parent,('id','title','status'),('ID','หัวข้อข่าว','การแสดงผล'),9,[60,520,120])
        # คำอธิบาย def Application.news_admin.load: อ่านข้อมูลข่าวแล้วเติมตารางใหม่
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: news.slides
        def load():
            tree.delete(*tree.get_children())
            for item in news.slides(True):tree.insert('','end',iid=str(item['id']),values=(item['id'],item['title'],'แสดง' if item['active'] else 'ซ่อน'))
        # คำอธิบาย def Application.news_admin.selected: อ่าน ID ข่าวที่เลือก และแจ้งหากยังไม่เลือก
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def selected():
            selection=tree.selection()
            if not selection:raise ValueError('กรุณาเลือกข่าว')
            return int(selection[0])
        # คำอธิบาย def Application.news_admin.action: ดำเนินคำสั่งจัดการข่าวที่เลือกแล้วปรับตาราง
        # รับค่า: kind | เรียกใช้: news.manage
        def action(kind):
            ident=selected()
            if kind=='delete' and not messagebox.askyesno('EXORA','ลบข่าวนี้ออกจากสไลด์?',parent=self.root):return
            news.manage(self.current_user['id'],ident,kind);load()
            if tree.exists(str(ident)):tree.selection_set(str(ident))
        # คำอธิบาย def Application.news_admin.add: เปิดฟอร์มให้ admin เลือกภาพและเพิ่มข่าวเข้าสไลด์
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def add():
            win=self.dialog('EXORA | เพิ่มภาพข่าว',580,430);inner=tk.Frame(win,bg=BG);inner.pack(fill='both',expand=True,padx=25,pady=22)
            title,_=self.field(inner,'หัวข้อข่าว (ไม่เกิน 120 ตัวอักษร)')
            source={'path':None};filename=self.label(inner,'ยังไม่ได้เลือกภาพ',10,MUTED,wraplength=480);filename.pack(anchor='w',pady=16)
            # คำอธิบาย def Application.news_admin.add.choose: เลือกไฟล์จากกล่องเลือกไฟล์
            # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
            def choose():
                path=filedialog.askopenfilename(parent=win,title='เลือกภาพข่าว',filetypes=[('ภาพข่าว JPG / PNG','*.jpg *.jpeg *.png')])
                if path:source['path']=path;filename.configure(text=Path(path).name)
            self.button(inner,'เลือกภาพข่าว',choose,'secondary').pack(anchor='w')
            # คำอธิบาย def Application.news_admin.add.save: ตรวจและบันทึกข้อมูลจากฟอร์ม
            # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน | เรียกใช้: news.add
            def save():
                if not source['path']:raise ValueError('กรุณาเลือกภาพข่าว')
                news.add(self.current_user['id'],title.get(),source['path']);win.destroy();load()
            self.button(inner,'เพิ่มเข้าสไลด์',save).pack(fill='x',pady=22)
        controls=tk.Frame(parent,bg=WHITE);controls.pack(fill='x',padx=22,pady=12)
        self.button(controls,'เพิ่มภาพข่าว  +',add).pack(side='left',padx=(0,8))
        for caption,kind in [('ขึ้น ↑','up'),('ลง ↓','down'),('แสดง / ซ่อน','toggle'),('ลบข่าว','delete')]:
            self.button(controls,caption,lambda kind=kind:action(kind),'danger' if kind=='delete' else 'secondary').pack(side='left',padx=4)
        self.label(parent,'ลำดับในตารางคือลำดับสไลด์ · ข่าวที่ซ่อนจะไม่แสดง · กลับหน้าแรกเพื่อดูข่าวที่บันทึก',10,MUTED,wraplength=850).pack(anchor='w',padx=22,pady=10)
        load()

    # หน้าสถิติสำหรับ admin อ่านประวัติจริง ไม่เปลี่ยนราคาหรือสถานะย้อนหลัง
    def statistics_page(self):
        if not self.is_admin_view():raise PermissionError('เฉพาะ admin')
        body=self.page('สถิติรายการ','TRANSACTION STATISTICS')
        controls=tk.Frame(body,bg=BG);controls.pack(fill='x',pady=8)
        start=tk.StringVar(value=(date.today()-timedelta(days=29)).isoformat());end=tk.StringVar(value=date.today().isoformat());state=tk.StringVar(value='อนุมัติแล้ว')
        for title,var in [('เริ่ม YYYY-MM-DD',start),('สิ้นสุด YYYY-MM-DD',end)]:
            self.label(controls,title,10,MUTED).pack(side='left',padx=5);ttk.Entry(controls,textvariable=var,width=12).pack(side='left',padx=5)
        names={'อนุมัติแล้ว':'approved','ทุกสถานะ':'all','รอตรวจสอบ':'pending','ปฏิเสธ':'rejected','ประวัติเดิม':'legacy'}
        ttk.Combobox(controls,textvariable=state,values=list(names),state='readonly',width=14).pack(side='left',padx=8)
        summary=self.label(body,'',16,bold=True,wraplength=1250,justify='left');summary.pack(anchor='w',pady=15)
        chart=tk.Canvas(body,height=175,bg=WHITE,highlightthickness=0);chart.pack(fill='x',pady=(0,12))
        tabs=ttk.Notebook(body);tabs.pack(fill='both',expand=True);layout.tab_feedback(tabs,lambda:self.motion_enabled.get())
        people=tk.Frame(tabs,bg=WHITE);money=tk.Frame(tabs,bg=WHITE);days=tk.Frame(tabs,bg=WHITE)
        tabs.add(people,text='ผู้ทำรายการบ่อยที่สุด');tabs.add(money,text='สกุลเงินยอดนิยม');tabs.add(days,text='สรุปรายวัน')
        users=self.table(people,('rank','user','count','thb'),('อันดับ','ผู้ใช้','จำนวนรายการ','มูลค่า THB'),10,[70,330,150,230])
        currencies=self.table(money,('code','count','received','paid','thb'),('สกุลเงิน','จำนวนรายการ','ร้านรับ (หน่วย)','ร้านจ่าย (หน่วย)','มูลค่าเทียบ THB'),10,[100,140,220,220,230])
        daily=self.table(days,('day','count','thb','unknown'),('วันที่ทำรายการ','จำนวนรายการ','มูลค่า THB','รายการไม่ทราบมูลค่า THB'),10,[180,160,230,240])
        note=self.label(body,'',10,MUTED,wraplength=1250,justify='left');note.pack(anchor='w',pady=12)
        cached={'data':None}
        # วาดจำนวนรายการ 14 วันล่าสุดภายในช่วงที่เลือก
        def draw(event=None):
            chart.delete('all');data=cached['data']
            if not data:return
            rows=list(reversed(data['daily'][:14]));width=max(200,chart.winfo_width())
            chart.create_text(15,16,text='จำนวนรายการต่อวัน · '+state.get(),anchor='w',fill=self.green,font=ui_font(10,True))
            if not rows:return
            maximum=max(1,max(row['count'] for row in rows));cell=(width-40)/len(rows)
            for index,row in enumerate(rows):
                x=25+index*cell;height=95*row['count']/maximum
                chart.create_rectangle(x,135-height,x+max(2,cell-12),135,fill=self.green,outline='')
                chart.create_text(x+max(2,cell-12)/2,125-height,text=str(row['count']),fill=INK,font=ui_font(9))
                chart.create_text(x+max(2,cell-12)/2,151,text=row['day'][5:],fill=MUTED,font=ui_font(8))
        # โหลดข้อมูลตามช่วงวันและสถานะ แล้วแสดงสามตารางพร้อมยอดสรุป
        def load():
            data=statistics.report(self.current_user['id'],start.get().strip(),end.get().strip(),names[state.get()]);cached['data']=data
            summary.configure(text=f"{data['count']:,} รายการ · มูลค่าธุรกรรม {data['thb']:,.2f} THB")
            for tree in (users,currencies,daily):tree.delete(*tree.get_children())
            for index,row in enumerate(data['users'],1):users.insert('','end',values=(index,row['name'],row['count'],f"{row['thb']:,.2f}"))
            for row in data['currencies']:currencies.insert('','end',values=(row['code'],row['count'],f"{row['received']:,.2f}",f"{row['paid']:,.2f}",f"{row['thb']:,.2f}"))
            for row in data['daily']:daily.insert('','end',values=(row['day'],row['count'],f"{row['thb']:,.2f}",row['unknown']))
            statuses=' · '.join(f"{STATUS.get(key,key)} {value}" for key,value in data['states'].items())
            note.configure(text='จำนวนรายการในช่วงวัน: '+(statuses or 'ไม่มีรายการ')+f"\nยอดเป็นมูลค่าธุรกรรม ไม่ใช่กำไร · ไม่รวม {data['unknown']} รายการที่ไม่ทราบมูลค่า THB · สกุลเงินจัดอันดับตามมูลค่า THB ที่เกี่ยวข้อง")
            draw()
        self.button(controls,'ดูสถิติ / รีเฟรช',load,'secondary').pack(side='left',padx=8)
        chart.bind('<Configure>',draw);load()
