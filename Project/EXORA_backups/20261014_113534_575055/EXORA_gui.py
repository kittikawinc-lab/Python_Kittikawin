"""EXORA storefront: native Windows Tkinter UI, with no web server."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import queue
import os
import tempfile
import uuid
from PIL import Image, ImageTk
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_payments as payments
import EXORA_receipts as receipts
import EXORA_brand as brand
import EXORA_auth as auth
import EXORA_email_settings as email_settings
import EXORA_layout as layout
import EXORA_visuals as visuals
import EXORA_effects as effects
import EXORA_rates as online_rates
import EXORA_news as news
from EXORA_news_ui import NewsSlideshow
from EXORA_motion import MotionScene
from EXORA_layout import font as ui_font

BG='#f6f7f1'; WHITE='#ffffff'; INK='#173e33'; MUTED='#788478'; LINE='#dfe5d9'; LIME='#d8ef9a'
STATUS={'legacy':'ประวัติเดิม','pending':'รอตรวจสอบ','approved':'อนุมัติแล้ว','rejected':'ปฏิเสธ'}
SYMBOLS={'USD':'$','EUR':'€','GBP':'£','JPY':'¥','CNY':'¥','KRW':'₩','THB':'฿'}

class Application:
    def __init__(self,root):
        self.root=root; self.current_user=None; self.images=[]; self.green='#125b4a';self.user_preview=False
        self.motion_enabled=tk.BooleanVar(master=root,value=True)
        icon=Path(db.BASE_DIR)/'EXORA_assets'/'brand'/'EXORA_icon.png'
        if icon.is_file():
            with Image.open(icon) as image:self.app_icon=ImageTk.PhotoImage(image.copy(),master=root)
            root.iconphoto(True,self.app_icon)
        self.root.title('EXORA | Currency Exchange')
        width=min(1760,root.winfo_screenwidth()-60);height=min(980,root.winfo_screenheight()-100)
        self.root.geometry(f'{max(960,width)}x{max(650,height)}'); self.root.minsize(1024,650); self.root.configure(bg=BG)
        if os.name=='nt':self.root.state('zoomed')
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

    def check_session(self):
        if self.closed:return
        if self.current_user:
            conn=db.getconnect()
            try:row=conn.execute('SELECT status FROM users WHERE id=?',(self.current_user['id'],)).fetchone()
            finally:conn.close()
            if not row or row[0]!='active':
                self.login_page();messagebox.showinfo('EXORA','บัญชีนี้ไม่พร้อมใช้งาน กรุณาติดต่อร้าน',parent=self.root)
        self.root.after(5000,self.check_session)

    def refresh_rates(self):
        if self.closed or self.rate_busy:return
        if self.rate_timer:
            self.root.after_cancel(self.rate_timer);self.rate_timer=None
        self.rate_busy=True
        def work():
            try:result=online_rates.refresh()
            except Exception:result={'ok':False,'message':'ดึงข้อมูลไม่สำเร็จ · ใช้ราคาที่บันทึกไว้'}
            self.rate_results.put(result)
        self.pool.submit(work)

    def rates_ready(self,result):
        self.rate_busy=False;self.rate_message=result['message']
        if not result.get('ok'):
            cached=online_rates.snapshot()
            if cached:self.rate_message+=' · ข้อมูลเดิม '+min(v.get('time') or v['date'] for v in cached.values())+' ('+', '.join(sorted({v.get('source') or 'Frankfurter' for v in cached.values()}))+')'
        self.update_rate_views()
        if not self.closed:self.rate_timer=self.root.after(online_rates.interval_ms(),self.refresh_rates)

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

    def close(self):
        if self.rate_timer:self.root.after_cancel(self.rate_timer)
        self.closed=True; self.pool.shutdown(wait=False,cancel_futures=True); self.root.destroy()

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

    def background(self,job,callback):
        self.pending_jobs+=1
        if not self.busy_indicator or not self.busy_indicator.frame.winfo_exists():self.busy_indicator=effects.BusyIndicator(self.root)
        self.busy_indicator.show('กำลังเตรียมข้อมูลให้คุณ…',self.motion_enabled.get())
        def work():
            try:self.jobs.put((callback,job(),None))
            except Exception as error:self.jobs.put((callback,None,error))
        self.pool.submit(work)

    def safe(self,fn):
        try:return fn()
        except Exception as error:messagebox.showerror('EXORA',str(error),parent=self.root)

    def is_admin_view(self):return bool(self.current_user and self.current_user['role']=='admin' and not self.user_preview)

    def toggle_user_view(self):
        if profiles.get_profile(self.current_user['id'])['role']!='admin':raise PermissionError('เฉพาะ admin')
        self.user_preview=not self.user_preview;self.shell();self.home()

    def ensure_not_preview(self):
        if self.user_preview:raise ValueError('นี่คือโหมดดูหน้าผู้ใช้ กลับฝั่งแอดมินเพื่อบันทึกข้อมูล')

    def visible_rate_message(self):
        if self.is_admin_view():return self.rate_message
        cached=online_rates.snapshot()
        stamp=min((v.get('time') or v['date'] for v in cached.values()),default='')
        return ('ยังอัปเดตไม่ได้ · ใช้ราคาล่าสุดที่บันทึกไว้' if 'ไม่สำเร็จ' in self.rate_message or 'ออฟไลน์' in self.rate_message or 'เก่าเกิน' in self.rate_message else 'ข้อมูลอ้างอิง')+(' · '+stamp if stamp else ' · กำลังตรวจสอบ')

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

    def label(self,parent,text,size=11,color=INK,bg=None,bold=False,**kwargs):
        return tk.Label(parent,text=text,font=ui_font(size,bold),fg=color,bg=bg or parent.cget('bg'),**kwargs)

    def button(self,parent,text,command,kind='primary',**kwargs):
        colors={'primary':(self.green,WHITE),'light':(LIME,INK),'secondary':('#eaf0e2',INK),'danger':('#ab4b3c',WHITE),'plain':(parent.cget('bg'),self.green)}
        bg,fg=colors[kind]
        button=tk.Button(parent,text=text,command=lambda:self.safe(command),bg=bg,fg=fg,font=ui_font(10,True),relief='flat',borderwidth=0,padx=18,pady=11,cursor='hand2',activebackground=bg,activeforeground=fg,**kwargs)
        effects.button_feedback(button,bg,lambda:self.motion_enabled.get());return button

    def card(self,parent,**kwargs):
        card=tk.Frame(parent,bg=WHITE,highlightthickness=1,highlightbackground=LINE,**kwargs)
        effects.card_feedback(card,lambda:self.motion_enabled.get());return card

    def field(self,parent,label,value='',secret=False):
        self.label(parent,label,10,MUTED).pack(anchor='w',pady=(12,6))
        var=tk.StringVar(value=value or '')
        entry=ttk.Entry(parent,textvariable=var,font=ui_font(11),show='●' if secret else '')
        entry.pack(fill='x'); return var,entry

    def clear_root(self):
        if hasattr(self,'transition'):self.transition.cancel()
        if self.busy_indicator and self.busy_indicator.frame.winfo_exists():self.busy_indicator.destroy()
        self.busy_indicator=None
        for widget in self.root.winfo_children():widget.destroy()
        self.images=[]

    def login_page(self):
        self.clear_root(); self.current_user=None;self.user_preview=False; self.shop=profiles.shop(); self.green=self.shop.get('accent') or '#125b4a'
        stage=tk.Frame(self.root,bg=WHITE,highlightbackground=LINE,highlightthickness=1)
        stage.place(relx=.5,rely=.5,anchor='center',width=1640,height=860);stage.grid_propagate(False)
        stage.columnconfigure(0,weight=55,uniform='login');stage.columnconfigure(1,weight=45,uniform='login');stage.rowconfigure(0,weight=1)
        left=tk.Canvas(stage,bg=self.green,highlightthickness=0);left.grid(row=0,column=0,sticky='nsew')
        right=tk.Frame(stage,bg=WHITE);right.grid(row=0,column=1,sticky='nsew')
        hero={'timer':None,'size':None}
        def redraw():
            hero['timer']=None
            if not left.winfo_exists():return
            size=(max(1,left.winfo_width()),max(1,left.winfo_height()))
            if hero['size']==size:return
            hero['size']=size;photo=ImageTk.PhotoImage(visuals.hero(*size));left.delete('travel-image');left.create_image(0,0,image=photo,anchor='nw',tags='travel-image');left.photo=photo
        def resized(event):
            if event.widget is self.root:
                width,height=visuals.login_size(event.width,event.height);stage.place_configure(width=width,height=height)
            if hero['timer']:
                try:left.after_cancel(hero['timer'])
                except tk.TclError:pass
            hero['timer']=left.after(40,redraw)
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
        def login():
            user=db.login(username.get(),password.get())
            if not user:raise ValueError('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
            self.current_user=user;self.shell();self.home()
        self.button(inner,'เข้าสู่ระบบ  ↗',login).pack(fill='x',pady=(25,10))
        self.button(inner,'ยังไม่มีบัญชี?  สมัครสมาชิก',self.signup,'plain').pack(fill='x')
        self.button(inner,'ลืมรหัสผ่าน?  รับ OTP ทางอีเมล',self.forgot_password,'plain').pack(fill='x')
        tk.Checkbutton(inner,text='เอฟเฟกต์',variable=self.motion_enabled,bg=WHITE,fg=MUTED,activebackground=WHITE,font=ui_font(9),highlightthickness=0).pack(anchor='w',pady=(12,0))
        entry.bind('<Return>',lambda e:pwd.focus_set());pwd.bind('<Return>',lambda e:self.safe(login));entry.focus_set()

    def dialog(self,title,width=650,height=680):
        self.root.update_idletasks()
        width,height,x,y=layout.dialog_geometry(self.root.winfo_screenwidth(),self.root.winfo_screenheight(),self.root.winfo_rootx(),self.root.winfo_rooty(),self.root.winfo_width(),self.root.winfo_height(),width,height)
        dialog=tk.Toplevel(self.root);dialog.title(title);dialog.geometry(f'{width}x{height}+{x}+{y}');dialog.configure(bg=BG)
        dialog.transient(self.root);dialog.grab_set();dialog.minsize(min(width,520),min(height,450));effects.dialog_reveal(dialog,lambda:self.motion_enabled.get())
        footer=tk.Canvas(dialog,height=24,bg=BG,highlightthickness=0);footer.pack(side='bottom',fill='x');MotionScene(footer,lambda:self.motion_enabled.get());return dialog

    def signup(self):
        win=self.dialog('EXORA | สร้างบัญชี',520,590);body=self.card(win);body.pack(fill='both',expand=True,padx=25,pady=25)
        inner=tk.Frame(body,bg=WHITE);inner.pack(fill='both',expand=True,padx=28,pady=24)
        self.label(inner,'เริ่มต้นการเดินทางของคุณ',21,bold=True).pack(anchor='w')
        username,_=self.field(inner,'ชื่อผู้ใช้');email,_=self.field(inner,'อีเมล');password,_=self.field(inner,'รหัสผ่านอย่างน้อย 8 ตัว',secret=True)
        confirm,_=self.field(inner,'ยืนยันรหัสผ่าน',secret=True)
        def save():
            if password.get()!=confirm.get():raise ValueError('รหัสผ่านไม่ตรงกัน')
            ok,message=db.register_user(username.get(),email.get(),password.get())
            if not ok:raise ValueError(message)
            win.destroy();messagebox.showinfo('EXORA',message,parent=self.root)
        self.button(inner,'สร้างบัญชี',save).pack(fill='x',pady=25)

    def forgot_password(self):
        win=self.dialog('EXORA | ยืนยัน OTP และตั้งรหัสผ่านใหม่',600,720)
        body=self.scroll_dialog(win)
        self.label(body,'กลับเข้าสู่การเดินทางของคุณ',21,bold=True).pack(anchor='w')
        self.label(body,'ส่งรหัสยืนยันไปยังอีเมลที่ลงทะเบียนไว้\nOTP 6 หลัก ใช้ได้ 10 นาที และใช้ได้ครั้งเดียว',10,MUTED,justify='left').pack(anchor='w',pady=12)
        address,email_entry=self.field(body,'อีเมลที่ลงทะเบียน')
        state={'challenge':None,'sending':False,'email':None}
        notice=self.label(body,'',10,MUTED,wraplength=500,justify='left')
        def send():
            if state['sending']:return
            requested_email=address.get().strip()
            state['sending']=True;send_button.configure(state='disabled',text='กำลังส่ง OTP…')
            def completed(result):
                state['sending']=False
                if not win.winfo_exists():return
                send_button.configure(state='normal',text='ส่ง / ขอ OTP ใหม่')
                if 'error' in result:notice.configure(text=result['error'],fg='#ab4b3c');return
                state['challenge']=result['challenge_id'];state['email']=requested_email
                notice.configure(text=result['message'],fg=self.green)
                otp_entry.focus_set()
            def request():
                try:return auth.request_otp(requested_email)
                except Exception as error:return {'error':str(error)}
            self.background(request,completed)
        send_button=self.button(body,'ส่ง OTP ไปยังอีเมล',send);send_button.pack(fill='x',pady=15)
        notice.pack(anchor='w',pady=(0,10))
        code,otp_entry=self.field(body,'OTP 6 หลัก')
        new,_=self.field(body,'รหัสผ่านใหม่อย่างน้อย 8 ตัว',secret=True)
        confirm,_=self.field(body,'ยืนยันรหัสผ่านใหม่',secret=True)
        def reset():
            if not state['challenge']:raise ValueError('กรุณาขอ OTP ก่อน')
            if address.get().strip()!=state['email']:raise ValueError('อีเมลเปลี่ยนแล้ว กรุณาขอ OTP สำหรับอีเมลนี้ใหม่')
            if new.get()!=confirm.get():raise ValueError('รหัสผ่านใหม่ไม่ตรงกัน')
            auth.reset_with_otp(state['challenge'],code.get(),new.get())
            win.destroy();messagebox.showinfo('EXORA','ตั้งรหัสผ่านใหม่แล้ว กรุณาเข้าสู่ระบบด้วยรหัสใหม่',parent=self.root)
        self.button(body,'ยืนยัน OTP และตั้งรหัสผ่านใหม่',reset).pack(fill='x',pady=25)

    def shell(self):
        self.root.unbind('<Configure>')
        self.clear_root();self.shop=profiles.shop();self.green=self.shop['accent'];self.configure_styles()
        self.profile_data=profiles.get_profile(self.current_user['id']);self.current_user['role']=self.profile_data['role']
        side=tk.Frame(self.root,bg=self.green,width=layout.SIDEBAR_WIDTH);side.pack(side='left',fill='y');side.pack_propagate(False)
        brand.header(side,self.shop['name'],dark=True,color=self.green,width=220).pack(anchor='w',padx=15,pady=(25,4))
        nav=[('⌂  หน้าร้าน',self.home),('⇄  แลกเปลี่ยนเงิน',self.exchange_page),('≡  ประวัติรายการ',self.history_page),('◉  โปรไฟล์ของฉัน',self.profile_page)]
        if self.is_admin_view():nav.extend([('✓  ตรวจสอบสลิป',self.review_page),('▦  จัดการร้าน',self.admin_page)])
        self.nav_buttons={}
        for text,fn in nav:
            button=tk.Button(side,text=text,command=lambda action=fn:self.safe(action),bg=self.green,fg=WHITE,activebackground='#24725f',activeforeground=WHITE,anchor='w',font=ui_font(11),relief='flat',padx=24,pady=15,cursor='hand2')
            button.pack(fill='x',padx=10,pady=3);self.nav_buttons[fn.__name__]=button
            effects.button_feedback(button,self.green,lambda:self.motion_enabled.get())
            button.bind('<Leave>',lambda e:e.widget.configure(bg='#24725f' if getattr(e.widget,'selected',False) else self.green),add='+')
        bottom=tk.Frame(side,bg=self.green);bottom.pack(side='bottom',fill='x',padx=22,pady=25)
        ornament=tk.Canvas(bottom,height=42,bg=self.green,highlightthickness=0);ornament.pack(fill='x',pady=(0,8));MotionScene(ornament,lambda:self.motion_enabled.get())
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
        def resize(event=None):
            width=self.canvas.winfo_width();content=min(width,layout.CONTENT_MAX)
            self.canvas.itemconfigure(self.window_id,width=content)
            if not getattr(self,'transition',None) or self.transition.timer is None:self.canvas.coords(self.window_id,max(0,(width-content)/2),0)
            self.canvas.configure(scrollregion=(0,0,width,max(self.canvas.winfo_height(),self.main_frame.winfo_reqheight())))
        self.main_frame.bind('<Configure>',resize);self.canvas.bind('<Configure>',resize)
        self.transition=layout.PageTransition(self.canvas,self.window_id,lambda:self.motion_enabled.get())
        self.root.bind('<MouseWheel>',self.wheel)

    def wheel(self,event):
        if not hasattr(self,'canvas') or not self.canvas.winfo_exists():return
        if isinstance(event.widget,(ttk.Treeview,tk.Text,ttk.Combobox)):return
        if event.widget.winfo_toplevel()!=self.root:return
        self.canvas.yview_scroll(int(-event.delta/120),'units')

    def page(self,title,subtitle):
        if hasattr(self,'transition'):self.transition.cancel()
        self.profile_data=profiles.get_profile(self.current_user['id'])
        self.current_user['role']=self.profile_data['role']
        for w in self.main_frame.winfo_children():w.destroy()
        self.images=[];self.canvas.yview_moveto(0)
        if self.is_admin_view():self.label(self.main_frame,subtitle.upper(),9,MUTED).pack(anchor='w',padx=32,pady=(20,9))
        self.label(self.main_frame,'หน้าร้าน' if title=='เตรียมพร้อมสำหรับทุกการเดินทาง' else title,26,bold=True).pack(anchor='w',padx=30,pady=(20,10))
        route=tk.Canvas(self.main_frame,height=42,bg=BG,highlightthickness=0);route.pack(fill='x',padx=32,pady=(0,10))
        MotionScene(route,lambda:self.motion_enabled.get())
        body=tk.Frame(self.main_frame,bg=BG);body.pack(fill='both',expand=True,padx=30,pady=(0,25))
        active={'เตรียมพร้อมสำหรับทุกการเดินทาง':'home','แลกเปลี่ยนเงิน':'exchange_page','ประวัติรายการ':'history_page','ตรวจสอบสลิป':'review_page','โปรไฟล์ของฉัน':'profile_page','จัดการร้าน':'admin_page'}.get(title)
        for key,button in getattr(self,'nav_buttons',{}).items():button.selected=(key==active);button.configure(bg='#24725f' if button.selected else self.green,fg=LIME if button.selected else WHITE)
        self.transition.start();effects.page_reveal(self.canvas,lambda:self.motion_enabled.get());return body

    def draw_notes(self,canvas,dark=False):
        canvas.create_oval(80,0,340,260,outline='#7c9c76',width=1)
        canvas.create_polygon(28,30,295,10,310,138,43,158,fill='#174f40',outline='#83aa7c',width=2)
        canvas.create_text(70,57,text='EXORA / EVERY JOURNEY',anchor='w',fill=LIME,font=ui_font(8))
        canvas.create_text(69,107,text='$ 100 USD',anchor='w',fill=LIME,font=('Georgia',24))
        canvas.create_polygon(83,116,344,140,333,250,72,226,fill='#cce3ac',outline='#92af77',width=2)
        canvas.create_text(120,166,text='EXCHANGE · EXPLORE',anchor='w',fill=INK,font=ui_font(8))
        canvas.create_text(115,204,text='€ 100 EUR',anchor='w',fill=INK,font=('Georgia',23))

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

    def responsive_columns(self,parent,left,right):
        parent.columnconfigure(0,weight=3);parent.columnconfigure(1,weight=1)
        mode={'wide':None}
        def resize(event):
            wide=event.width>=1040
            if mode['wide']==wide:return
            mode['wide']=wide
            left.grid_configure(row=0,column=0,sticky='nsew',padx=(0,20) if wide else 0)
            right.grid_configure(row=0 if wide else 1,column=1 if wide else 0,sticky='nsew',padx=0,pady=0 if wide else (18,0))
            parent.columnconfigure(1,weight=1 if wide else 0)
        parent.bind('<Configure>',resize,add='+')

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
        def highlight(event):
            row=tree.identify_row(event.y) if event.type!=tk.EventType.Leave else ''
            if row==hover['row']:return
            previous=hover['row']
            if previous and tree.exists(previous):tree.item(previous,tags=tuple(t for t in tree.item(previous,'tags') if t!='hover'))
            if row and tree.exists(row):tree.item(row,tags=tuple(tree.item(row,'tags'))+('hover',))
            hover['row']=row
        tree.bind('<Motion>',highlight,add='+');tree.bind('<Leave>',highlight,add='+')
        return tree

    def rate_board(self,parent,height=9):
        self.label(parent,'อัตราแลกเปลี่ยนของร้าน',16,bold=True).pack(anchor='w',padx=22,pady=(23,0))
        tree=self.table(parent,('code','name','buy','sell','market'),('สกุลเงิน','ชื่อ','รับซื้อ','ขาย','อ้างอิงออนไลน์'),height,[65,140,85,85,100])
        status=self.label(parent,self.visible_rate_message(),9,MUTED,wraplength=600,justify='left');status.pack(anchor='w',padx=22,pady=(0,8))
        self.label(parent,'THB ต่อ 1 หน่วย · '+(online_rates.source_label() if self.is_admin_view() else ('Twelve Data' if online_rates.live_enabled() else 'Frankfurter · อัตราอ้างอิงรายวัน')),9,MUTED,wraplength=600,justify='left').pack(anchor='w',padx=22,pady=(0,8))
        if self.is_admin_view():self.button(parent,'ตรวจสอบราคาออนไลน์ ↻',self.refresh_rates,'secondary').pack(anchor='w',padx=22,pady=(0,12))
        self.rate_views.append((tree,status));self.update_rate_views();return tree

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
        def calculate():
            q=profiles.quote(source.get(),target.get(),amount.get());holder['quote']=q
            result.configure(fg=self.green)
            effects.number_reveal(result,q['to_amount'],lambda value:f"ได้รับ {value:,.2f} {q['to_currency']}\n1 {q['from_currency']} = {q['exchange_rate']:.6f} {q['to_currency']}",lambda:self.motion_enabled.get())
        def start():calculate();self.payment_dialog(dict(holder['quote']))
        def changed(*args):effects.cancel(result,'number');holder['quote']=None;result.configure(text='คำนวณยอดใหม่หลังเปลี่ยนข้อมูล',fg=MUTED)
        for var in (source,target,amount):var.trace_add('write',changed)
        self.button(inner,'คำนวณยอด',calculate,'secondary').pack(fill='x',pady=(0,8))
        self.button(inner,'ทำรายการและแนบสลิป  ↗',start).pack(fill='x')

    def exchange_page(self):
        body=self.page('แลกเปลี่ยนเงิน','START YOUR JOURNEY');body.columnconfigure(0,weight=2);body.columnconfigure(1,weight=3)
        card=self.card(body);card.grid(row=0,column=0,sticky='nsew',padx=(0,20));self.converter(card)
        rates=self.card(body);rates.grid(row=0,column=1,sticky='nsew');self.rate_board(rates)
        self.responsive_columns(body,card,rates)

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

    def payment_dialog(self,data):
        win=self.dialog('EXORA | เลือกวิธีชำระเงินและแนบหลักฐาน',900,850)
        body=self.scroll_dialog(win)
        self.label(body,'เลือกวิธีชำระเงิน',23,bold=True).pack(anchor='w')
        self.label(body,f"{data['from_amount']:,.2f} {data['from_currency']}  →  {data['to_amount']:,.2f} {data['to_currency']}",18,self.green,bold=True).pack(anchor='w',pady=(15,5))
        self.label(body,f"อัตรา 1 {data['from_currency']} = {data['exchange_rate']:.6f} {data['to_currency']}",10,MUTED).pack(anchor='w')
        info=tk.Frame(body,bg=BG);info.pack(fill='x',pady=8);info.columnconfigure(0,weight=1);info.columnconfigure(1,weight=1)
        a=tk.Frame(info,bg=BG);a.grid(row=0,column=0,sticky='ew',padx=(0,12));b=tk.Frame(info,bg=BG);b.grid(row=0,column=1,sticky='ew')
        name,_=self.field(a,'ชื่อลูกค้า',self.profile_data['display_name'] or self.current_user['username']);phone,_=self.field(b,'เบอร์โทร',self.profile_data['phone'])
        tabs=ttk.Notebook(body);tabs.pack(fill='both',expand=True,pady=(20,12));layout.tab_feedback(tabs,lambda:self.motion_enabled.get())
        qr=tk.Frame(tabs,bg=WHITE);bank=tk.Frame(tabs,bg=WHITE)
        tabs.add(qr,text='สแกน QR พร้อมเพย์');tabs.add(bank,text='โอนบัญชีธนาคาร')
        qr_path=Path(db.BASE_DIR)/'EXORA_assets'/'payments'/'store_qr.png'
        if qr_path.is_file():
            with Image.open(qr_path) as image:
                image=image.copy();image.thumbnail((310,405),Image.Resampling.LANCZOS);photo=ImageTk.PhotoImage(image)
            image_label=tk.Label(qr,image=photo,bg=WHITE);image_label.image=photo;image_label.pack(pady=(16,6))
            self.button(qr,'เปิดภาพ QR ขนาดเต็ม',lambda:os.startfile(str(qr_path)),'plain').pack(pady=(0,8))
        else:self.label(qr,'ไม่พบ QR ชำระเงิน กรุณาติดต่อร้าน',11,'#ab4b3c',wraplength=650).pack(pady=45)
        self.label(qr,'ตรวจสอบชื่อผู้รับในแอปธนาคารให้ตรงกับผู้รับที่ต้องการ ก่อนโอนและแนบสลิป',10,MUTED,wraplength=740).pack(pady=(0,18))
        inner=tk.Frame(bank,bg=WHITE);inner.pack(fill='both',expand=True,padx=24,pady=20)
        settings=profiles.shop()
        if all(settings.get(k) for k in ('bank_name','bank_account_name','bank_account_number')):
            recipient=f"บัญชีรับเงินของร้าน\n{settings['bank_name']} · {settings['bank_account_name']}\nเลขบัญชี {settings['bank_account_number']}"
        else:recipient='ร้านยังไม่ได้ระบุบัญชีรับเงิน\nให้ admin กรอกข้อมูลใน จัดการร้าน → บัญชีธนาคารรับเงิน'
        self.label(inner,recipient,12,self.green,bold=True,justify='left',wraplength=740).pack(anchor='w',pady=(0,12))
        grid=tk.Frame(inner,bg=WHITE);grid.pack(fill='x');grid.columnconfigure(0,weight=1);grid.columnconfigure(1,weight=1)
        values={}
        specs=[('payer_bank','ธนาคารผู้โอน',''),('payer_name','ชื่อบัญชีผู้โอน',self.profile_data['display_name'] or self.current_user['username']),
               ('payer_account','เลขบัญชีผู้โอน',''),('transfer_amount','จำนวนเงินที่โอน (THB)',str(data['from_amount']) if data['from_currency']=='THB' else ''),
               ('transfer_at','วันเวลาโอน (YYYY-MM-DD HH:MM)',datetime.now().strftime('%Y-%m-%d %H:%M')),('transfer_reference','เลขอ้างอิง (ไม่บังคับ)','')]
        for index,(key,label,initial) in enumerate(specs):
            cell=tk.Frame(grid,bg=WHITE);cell.grid(row=index//2,column=index%2,sticky='ew',padx=(0,15) if index%2==0 else 0)
            values[key],_=self.field(cell,label,initial)
        self.label(body,settings['payment_note'],10,'#917129',wraplength=780,justify='left').pack(anchor='w',pady=(2,14))
        selected=tk.StringVar(value='ยังไม่ได้เลือกหลักฐาน')
        self.label(body,'แนบสลิป JPG / PNG ไม่เกิน 10 MB',10,MUTED).pack(anchor='w')
        self.label(body,textvariable=selected,text='',size=10,wraplength=760,justify='left').pack(anchor='w',pady=10)
        def choose():
            file=filedialog.askopenfilename(parent=win,title='เลือกหลักฐานชำระเงิน',filetypes=[('สลิป JPG/PNG','*.jpg *.jpeg *.png')])
            if file:selected.set(file)
        self.button(body,'เลือกหลักฐานชำระเงิน',choose,'secondary').pack(anchor='w')
        def submit():
            self.ensure_not_preview()
            if not Path(selected.get()).is_file():raise ValueError('กรุณาเลือกหลักฐานก่อนส่ง')
            method='qr' if tabs.index(tabs.select())==0 else 'bank'
            if method=='qr' and not qr_path.is_file():raise ValueError('ยังไม่มีภาพ QR ของร้าน')
            payload={**data,'customer_name':name.get().strip(),'customer_phone':phone.get().strip(),'payment_method':method}
            if method=='bank':payload.update({k:v.get().strip() for k,v in values.items()})
            number='EX'+datetime.now().strftime('%y%m%d')+'-'+uuid.uuid4().hex[:10].upper()
            payments.submit(number,self.current_user['id'],payload,selected.get());win.destroy();self.history_page()
            messagebox.showinfo('ส่งตรวจสอบแล้ว',f'เลขรายการ: {number}\nสถานะ: รอตรวจสอบ\nเจ้าหน้าที่จะตรวจหลักฐานก่อนอนุมัติ',parent=self.root)
        self.button(body,'ส่งหลักฐานให้เจ้าหน้าที่ตรวจสอบ  ↗',submit).pack(fill='x',pady=(20,8))

    def history_page(self):self.show_history(False)
    def review_page(self):self.show_history(True)
    def show_history(self,pending):
        if pending and not self.is_admin_view():raise PermissionError('เฉพาะ admin')
        body=self.page('ตรวจสอบสลิป' if pending else 'ประวัติรายการ','PAYMENT REVIEW' if pending else 'YOUR EXCHANGE JOURNAL')
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

    def selected_detail(self):
        selection=self.history_tree.selection()
        if not selection:raise ValueError('กรุณาเลือกรายการ')
        self.detail(self.history_tree.item(selection[0],'values')[0])

    def detail(self,number):
        row=payments.get_transaction(number,self.current_user['id'])
        if self.user_preview and row['user_id']!=self.current_user['id']:raise PermissionError('โหมดดูหน้าผู้ใช้แสดงเฉพาะรายการของบัญชีคุณ')
        win=self.dialog(f'EXORA | {number}',900,790)
        body=self.scroll_dialog(win)
        self.label(body,number,23,bold=True).pack(anchor='w');self.label(body,STATUS.get(row['payment_status'],row['payment_status']),11,self.green,bold=True).pack(anchor='w',pady=(8,16))
        split=tk.Frame(body,bg=BG);split.pack(fill='both',expand=True);split.columnconfigure(0,weight=1);split.columnconfigure(1,weight=1)
        left=tk.Frame(split,bg=BG);left.grid(row=0,column=0,sticky='nsew',padx=(0,20));right=tk.Frame(split,bg=BG);right.grid(row=0,column=1,sticky='nsew')
        fields=[('ลูกค้า',row['customer_name']),('เบอร์โทร',row['customer_phone']),('แลกจาก',f"{row['from_amount']:,.2f} {row['from_currency']}"),('ได้รับ',f"{row['to_amount']:,.2f} {row['to_currency']}"),('อัตรา',f"{row['exchange_rate']:.6f}"),('วันที่',row['transaction_date']),('ตรวจสอบเมื่อ',row['reviewed_at']),('หมายเหตุ',row['review_note'])]
        fields.insert(2,('วิธีชำระเงิน',{'qr':'QR พร้อมเพย์','bank':'โอนบัญชีธนาคาร','legacy':'ข้อมูลเดิม'}.get(row.get('payment_method'),'ข้อมูลเดิม')))
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
        else:self.label(right,'รายการเดิมไม่มีสลิป',11,MUTED).pack(anchor='w')
        audit=payments.get_audit(number,self.current_user['id']);audit_text='\n'.join(f"{a['created_at']} · {STATUS.get(a['action'],{'submitted':'แนบสลิป','resubmitted':'แนบสลิปใหม่'}.get(a['action'],a['action']))}" for a in audit[-4:])
        self.label(right,audit_text or 'ประวัติจากระบบเดิม',9,MUTED,wraplength=370,justify='left').pack(anchor='w',pady=15)
        actions=tk.Frame(body,bg=BG);actions.pack(fill='x',pady=(20,8))
        self.button(actions,'บันทึก PDF',lambda:self.export_pdf(number),'secondary').pack(side='left',padx=(0,9))
        def reload():win.destroy();self.load_history();self.detail(number)
        if row['payment_status']=='pending' and self.is_admin_view():
            def review(status):
                if status=='approved':
                    if not messagebox.askyesno('อนุมัติรายการ','ตรวจสอบยอดและสลิปกับข้อมูลของร้านแล้วใช่หรือไม่?\nการอนุมัตินี้ไม่ได้เชื่อมต่อธนาคาร',parent=win):return
                    note='ตรวจสอบสลิปโดยเจ้าหน้าที่'
                else:
                    from tkinter import simpledialog
                    note=simpledialog.askstring('ปฏิเสธรายการ','ระบุเหตุผลที่ปฏิเสธ',parent=win)
                    if note is None:return
                actor=self.current_user['id']
                payments.review(number,actor,status,note);reload()
                if status=='approved':
                    def completed(result):
                        messagebox.showinfo('EXORA','สร้างใบเสร็จธีม EXORA แล้ว กดส่งใบเสร็จในรายละเอียดเพื่อส่งให้ผู้ทำรายการ',parent=self.root)
                    self.background(lambda:receipts.ensure_receipt(number,actor),completed)
            self.button(actions,'✓ อนุมัติ',lambda:review('approved')).pack(side='left',padx=(0,9))
            self.button(actions,'ปฏิเสธ',lambda:review('rejected'),'danger').pack(side='left')
        if row['payment_status']=='rejected' and row['user_id']==self.current_user['id']:
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
            def send():
                self.ensure_not_preview()
                if mail_state['sending']:return
                recipient=(owner[0] or '').strip() if owner else ''
                if not recipient:raise ValueError('ให้ผู้ทำรายการเพิ่มอีเมลในโปรไฟล์ก่อนส่งใบเสร็จ')
                if not email_settings.configured():
                    raise ValueError('ระบบอีเมลยังไม่พร้อม กรุณาติดต่อร้าน' if not self.is_admin_view() else 'ตั้ง EXORA_GMAIL_APP_PASSWORD ของ '+email_settings.SENDER+' ก่อนส่งใบเสร็จ')
                actor=self.current_user['id']
                mail_state['sending']=True;mail_button.configure(state='disabled',text='กำลังส่งใบเสร็จ…');mail_status.configure(text='กำลังสร้าง PDF และส่งอีเมล')
                def work():
                    try:
                        result=receipts.send_to_user(number,actor)
                        return {'ok':result['status']=='sent','message':result['message'],'error':result['message']}
                    except Exception as error:return {'error':str(error)}
                def completed(result):
                    mail_state['sending']=False
                    if not win.winfo_exists():return
                    mail_button.configure(state='normal',text='ส่งใบเสร็จทางอีเมล  ↗')
                    mail_status.configure(text=(result.get('message') or 'ส่งใบเสร็จพร้อม PDF ไปยัง '+recipient) if result.get('ok') else ('ส่งไม่สำเร็จ: '+result['error']),fg=self.green if result.get('ok') else '#ab4b3c')
                self.background(work,completed)
            mail_button=self.button(body,'ส่งใบเสร็จทางอีเมล  ↗',send);mail_button.pack(anchor='w',pady=10)

    def export_pdf(self,number):
        path=filedialog.asksaveasfilename(parent=self.root,title='บันทึก PDF',defaultextension='.pdf',initialfile=number+'.pdf',filetypes=[('PDF','*.pdf')])
        if path:
            row=payments.get_transaction(number,self.current_user['id'])
            if row['payment_status']=='approved':
                import shutil
                saved=receipts.ensure_receipt(number,self.current_user['id'])
                if saved.resolve()!=Path(path).resolve():shutil.copy2(saved,path)
            else:receipts.export_pdf(number,self.current_user['id'],path)
            messagebox.showinfo('EXORA','บันทึก PDF แล้ว',parent=self.root)

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
        for key,label in [('display_name','ชื่อที่แสดง'),('email','อีเมล'),('phone','เบอร์โทร'),('bio','แนะนำตัว')]:values[key],_=self.field(inner,label,profile.get(key) or (profile['username'] if key=='display_name' else ''))
        accent=tk.StringVar(value=profile.get('accent') or self.green);avatar_file={'path':None}
        def color():
            chosen=colorchooser.askcolor(accent.get(),parent=self.root)[1]
            if chosen:accent.set(chosen)
        def choose():
            file=filedialog.askopenfilename(parent=self.root,title='รูปโปรไฟล์',filetypes=[('รูปภาพ','*.jpg *.jpeg *.png')])
            if file:avatar_file['path']=file;avatar_status.configure(text=Path(file).name)
        row=tk.Frame(inner,bg=WHITE);row.pack(fill='x',pady=18)
        self.button(row,'เลือกสี',color,'secondary').pack(side='left',padx=(0,10));self.button(row,'เลือกรูปโปรไฟล์',choose,'secondary').pack(side='left')
        avatar_status=self.label(inner,'',9,MUTED);avatar_status.pack(anchor='w')
        def save():
            self.ensure_not_preview()
            profiles.save_profile(self.current_user['id'],**{key:value.get() for key,value in values.items()},accent=accent.get(),avatar_source=avatar_file['path'])
            self.shell();self.profile_page();messagebox.showinfo('EXORA','บันทึกโปรไฟล์แล้ว',parent=self.root)
        self.button(inner,'บันทึกโปรไฟล์  ↗',save).pack(fill='x',pady=(15,0))
        card=self.card(grid);card.grid(row=0,column=1,sticky='nsew');inner=tk.Frame(card,bg=WHITE);inner.pack(fill='both',expand=True,padx=25,pady=24)
        self.label(inner,'เปลี่ยนรหัสผ่าน',17,bold=True).pack(anchor='w');old,_=self.field(inner,'รหัสผ่านปัจจุบัน',secret=True);new,_=self.field(inner,'รหัสผ่านใหม่อย่างน้อย 8 ตัว',secret=True);confirm,_=self.field(inner,'ยืนยันรหัสผ่านใหม่',secret=True)
        def password():
            if new.get()!=confirm.get():raise ValueError('รหัสผ่านใหม่ไม่ตรงกัน')
            self.ensure_not_preview();profiles.change_password(self.current_user['id'],old.get(),new.get());old.set('');new.set('');confirm.set('');messagebox.showinfo('EXORA','เปลี่ยนรหัสผ่านแล้ว',parent=self.root)
        self.button(inner,'เปลี่ยนรหัสผ่าน',password,'secondary').pack(fill='x',pady=22)

    def admin_page(self):
        if not self.is_admin_view():raise PermissionError('เฉพาะ admin')
        body=self.page('จัดการร้าน','EXORA MANAGEMENT')
        tabs=ttk.Notebook(body);tabs.pack(fill='both',expand=True);layout.tab_feedback(tabs,lambda:self.motion_enabled.get())
        store=tk.Frame(tabs,bg=WHITE);rates=tk.Frame(tabs,bg=WHITE);users=tk.Frame(tabs,bg=WHITE)
        tabs.add(store,text='หน้าร้าน');tabs.add(rates,text='อัตราแลกเปลี่ยน');tabs.add(users,text='ผู้ใช้งาน')
        news_tab=tk.Frame(tabs,bg=WHITE);tabs.add(news_tab,text='ข่าวหน้าแรก');self.news_admin(news_tab)
        form=tk.Frame(store,bg=WHITE);form.pack(fill='x',padx=28,pady=25);values={}
        fields=tk.Frame(form,bg=WHITE);fields.pack(fill='x');fields.columnconfigure(0,weight=1);fields.columnconfigure(1,weight=1)
        for index,(key,label) in enumerate([('name','ชื่อร้าน'),('tagline','ข้อความแนะนำ'),('phone','เบอร์โทรร้าน'),('address','ที่อยู่'),('hours','เวลาเปิดบริการ'),('payment_note','คำแนะนำก่อนแนบสลิป'),('bank_name','บัญชีธนาคารรับเงิน: ชื่อธนาคาร'),('bank_account_name','ชื่อบัญชีรับเงินของร้าน'),('bank_account_number','เลขบัญชีรับเงินของร้าน')]):
            cell=tk.Frame(fields,bg=WHITE);cell.grid(row=index//2,column=index%2,sticky='ew',padx=(0,20) if index%2==0 else 0)
            values[key],_=self.field(cell,label,self.shop.get(key))
        accent=tk.StringVar(value=self.green)
        def color():
            value=colorchooser.askcolor(accent.get(),parent=self.root)[1]
            if value:accent.set(value)
        self.button(form,'เลือกสีร้าน',color,'secondary').pack(anchor='w',pady=15)
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
        def save_online():
            if auto.get() and not messagebox.askyesno('EXORA','ราคาซื้อ–ขายของร้านจะเปลี่ยนตามข้อมูลออนไลน์และส่วนต่างที่กำหนด\nยืนยันเปิดใช้ราคาซื้อ–ขายอัตโนมัติ?',parent=self.root):return
            online_rates.settings(self.current_user['id'],auto.get(),spread.get());self.refresh_rates()
        self.button(controls,'บันทึก',save_online,'secondary').pack(side='left',padx=12)
        def rate_form():
            if profiles.shop().get('online_pricing')=='1':raise ValueError('กรุณาปิดราคาซื้อ–ขายอัตโนมัติก่อนแก้ไขราคาเอง')
            selection=tree.selection();code=tree.item(selection[0],'values')[0] if selection else '';existing=db.getcur(code) if code else None
            win=self.dialog('EXORA | อัตราแลกเปลี่ยน',510,520);inner=tk.Frame(win,bg=BG);inner.pack(fill='both',expand=True,padx=28,pady=25)
            cv,ce=self.field(inner,'รหัสสกุลเงิน 3 ตัว',code);nv,_=self.field(inner,'ชื่อสกุลเงิน',existing[2] if existing else '');bv,_=self.field(inner,'ราคาที่ร้านรับซื้อ (THB ต่อ 1 หน่วย)',existing[3] if existing else '');sv,_=self.field(inner,'ราคาที่ร้านขาย (THB ต่อ 1 หน่วย)',existing[4] if existing else '')
            if code:ce.configure(state='readonly')
            def update():profiles.set_rate(self.current_user['id'],cv.get(),nv.get(),bv.get(),sv.get());win.destroy();self.admin_page()
            self.button(inner,'บันทึกอัตรา',update).pack(fill='x',pady=25)
        self.button(rates,'แก้ไขที่เลือก / เพิ่มสกุลเงิน',rate_form).pack(anchor='w',padx=22,pady=(0,24))
        utree=self.table(users,('id','username','email','role','status'),('ID','ชื่อผู้ใช้','อีเมล','สิทธิ์','สถานะ'),10,[60,160,220,100,100])
        for user in profiles.list_users(self.current_user['id']):utree.insert('','end',values=[v or '' for v in user])
        def user_form():
            selection=utree.selection()
            if not selection:raise ValueError('กรุณาเลือกบัญชี')
            uid,username,email,role,status=utree.item(selection[0],'values');win=self.dialog('EXORA | สิทธิ์ผู้ใช้งาน',500,420);inner=tk.Frame(win,bg=BG);inner.pack(fill='both',expand=True,padx=28,pady=25)
            self.label(inner,username,20,bold=True).pack(anchor='w');rv=tk.StringVar(value=role);sv=tk.StringVar(value=status)
            self.label(inner,'สิทธิ์',10,MUTED).pack(anchor='w',pady=(22,8));ttk.Combobox(inner,textvariable=rv,values=['user','staff','admin'],state='readonly').pack(fill='x')
            self.label(inner,'สถานะ',10,MUTED).pack(anchor='w',pady=(22,8));ttk.Combobox(inner,textvariable=sv,values=['active','inactive','banned'],state='readonly').pack(fill='x')
            def update():profiles.update_user(self.current_user['id'],int(uid),rv.get(),sv.get());win.destroy();self.admin_page()
            self.button(inner,'บันทึกสิทธิ์',update).pack(fill='x',pady=28)
        self.button(users,'จัดการสิทธิ์ที่เลือก',user_form).pack(anchor='w',padx=22,pady=(0,25))
        actions=tk.Frame(users,bg=WHITE);actions.pack(fill='x',padx=22,pady=8)
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

    def news_admin(self,parent):
        self.label(parent,'ข่าวการเงินโลก · สไลด์หน้าแรก',20,bold=True).pack(anchor='w',padx=22,pady=(20,8))
        self.label(parent,'เพิ่มภาพข่าว JPG / PNG ไม่เกิน 10 MB',10,MUTED).pack(anchor='w',padx=22,pady=(0,10))
        tree=self.table(parent,('id','title','status'),('ID','หัวข้อข่าว','การแสดงผล'),9,[60,520,120])
        def load():
            tree.delete(*tree.get_children())
            for item in news.slides(True):tree.insert('','end',iid=str(item['id']),values=(item['id'],item['title'],'แสดง' if item['active'] else 'ซ่อน'))
        def selected():
            selection=tree.selection()
            if not selection:raise ValueError('กรุณาเลือกข่าว')
            return int(selection[0])
        def action(kind):
            ident=selected()
            if kind=='delete' and not messagebox.askyesno('EXORA','ลบข่าวนี้ออกจากสไลด์?',parent=self.root):return
            news.manage(self.current_user['id'],ident,kind);load()
            if tree.exists(str(ident)):tree.selection_set(str(ident))
        def add():
            win=self.dialog('EXORA | เพิ่มภาพข่าว',580,430);inner=tk.Frame(win,bg=BG);inner.pack(fill='both',expand=True,padx=25,pady=22)
            title,_=self.field(inner,'หัวข้อข่าว (ไม่เกิน 120 ตัวอักษร)')
            source={'path':None};filename=self.label(inner,'ยังไม่ได้เลือกภาพ',10,MUTED,wraplength=480);filename.pack(anchor='w',pady=16)
            def choose():
                path=filedialog.askopenfilename(parent=win,title='เลือกภาพข่าว',filetypes=[('ภาพข่าว JPG / PNG','*.jpg *.jpeg *.png')])
                if path:source['path']=path;filename.configure(text=Path(path).name)
            self.button(inner,'เลือกภาพข่าว',choose,'secondary').pack(anchor='w')
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
