"""การ์ดค่าเงินแบบเลื่อนได้ พร้อมธงที่วาดในโปรแกรมและปุ่มรายการโปรด."""
# Tkinter สร้างหน้าจอ Pillow วาดธงขนาดเล็กโดยไม่ต้องดาวน์โหลดภาพ
from EXORA_i18n import tk,ttk
from PIL import Image,ImageDraw,ImageTk
import math
import EXORA_currency_cards as data
from EXORA_layout import font

# วาดดาวหลายแฉกตามตำแหน่งและขนาดที่กำหนด
def star(draw,x,y,r,color):
    points=[]
    for i in range(10):
        radius=r if i%2==0 else r*.4;angle=-math.pi/2+i*math.pi/5
        points.append((x+radius*math.cos(angle),y+radius*math.sin(angle)))
    draw.polygon(points,fill=color)

# วาดธงประเทศหลัก; EUR ใช้ธงสหภาพยุโรป และรหัสอื่นใช้ป้ายสกุลเงิน
def flag(code):
    image=Image.new('RGB',(90,60),'white');d=ImageDraw.Draw(image)
    if code=='USD':
        for i in range(0,13,2):d.rectangle((0,i*60/13,90,(i+1)*60/13),fill='#b22234')
        d.rectangle((0,0,36,32),fill='#3c3b6e')
        for row in range(9):
            for col in range(6 if row%2==0 else 5):star(d,3+col*6+(3 if row%2 else 0),3+row*3.2,1.5,'white')
    elif code in ('GBP','AUD'):
        d.rectangle((0,0,90,60),fill='#012169');w,h=(90,60) if code=='GBP' else (45,30)
        d.line((0,0,w,h),fill='white',width=10);d.line((0,h,w,0),fill='white',width=10)
        d.line((0,0,w,h),fill='#c8102e',width=3);d.line((0,h,w,0),fill='#c8102e',width=3)
        d.rectangle((w*.4,0,w*.6,h),fill='white');d.rectangle((0,h*.35,w,h*.65),fill='white')
        d.rectangle((w*.45,0,w*.55,h),fill='#c8102e');d.rectangle((0,h*.425,w,h*.575),fill='#c8102e')
        if code=='AUD':
            for x,y,r in ((22,45,7),(67,12,5),(60,30,5),(79,26,5),(69,49,5),(75,37,3)):star(d,x,y,r,'white')
    elif code=='EUR':
        d.rectangle((0,0,90,60),fill='#003399')
        for i in range(12):star(d,45+19*math.sin(i*math.pi/6),30-19*math.cos(i*math.pi/6),3,'#ffcc00')
    elif code=='JPY':d.ellipse((28,13,62,47),fill='#bc002d')
    elif code=='CNY':
        d.rectangle((0,0,90,60),fill='#de2910');star(d,16,17,9,'#ffde00')
        for x,y in ((30,7),(36,14),(36,24),(30,31)):star(d,x,y,3,'#ffde00')
    elif code=='SGD':
        d.rectangle((0,0,90,30),fill='#ef3340');d.ellipse((8,5,31,27),fill='white');d.ellipse((13,3,34,25),fill='#ef3340')
        for x,y in ((33,7),(41,12),(38,21),(28,21),(25,12)):star(d,x,y,2.4,'white')
    elif code=='CAD':
        d.rectangle((0,0,22,60),fill='#d80621');d.rectangle((68,0,90,60),fill='#d80621')
        d.polygon([(45,10),(49,21),(55,17),(53,29),(65,26),(60,38),(48,40),(47,52),(43,52),(44,40),(30,38),(25,26),(37,29),(35,17),(41,21)],fill='#d80621')
    elif code=='KRW':
        d.ellipse((30,15,60,45),fill='#cd2e3a');d.pieslice((30,15,60,45),0,180,fill='#0047a0');d.ellipse((30,23,45,38),fill='#cd2e3a');d.ellipse((45,23,60,38),fill='#0047a0')
        for x,y,angle,broken in ((7,4,-55,()),(62,4,55,(0,2)),(7,38,55,(1,)),(62,38,-55,(0,1,2))):
            bars=Image.new('RGBA',(22,16));pen=ImageDraw.Draw(bars)
            for j in range(3):
                pen.rectangle((2,j*5,19,j*5+2),fill='#111111')
                if j in broken:pen.rectangle((10,j*5,12,j*5+2),fill=(0,0,0,0))
            bars=bars.rotate(angle,expand=True);image.paste(bars,(x,y),bars)
    else:d.text((30,22),code,fill='#125b4a')
    return ImageTk.PhotoImage(image.resize((54,36),Image.Resampling.LANCZOS))

class CurrencyBoard(tk.Frame):
    # สร้างตัวกรองรายการโปรดและพื้นที่การ์ดปรับจำนวนคอลัมน์ตามความกว้าง
    def __init__(self,parent,app):
        super().__init__(parent,bg='white');self.app=app;self.only=tk.BooleanVar();self.columns=0;self.tiles=[];self.images=[]
        header=tk.Frame(self,bg='white');header.pack(fill='x',padx=18,pady=14)
        tk.Label(header,text='เลือกสกุลเงินสำหรับการเดินทาง',bg='white',fg='#173e33',font=font(16,True)).pack(anchor='w')
        tk.Label(header,text='ราคาซื้อ–ขายของร้าน · THB ต่อ 1 หน่วย',bg='white',fg='#788478',font=font(9)).pack(anchor='w',pady=5)
        ttk.Checkbutton(header,text='★ รายการโปรดเท่านั้น',variable=self.only,command=lambda:app.safe(self.refresh)).pack(anchor='w')
        app.button(header,'อัปเดตค่าเงินทันที ↻',app.refresh_rates,'secondary').pack(anchor='w',pady=(8,0))
        self.status=tk.Label(header,text=app.visible_rate_message(),bg='white',fg='#788478',font=font(9));self.status.pack(anchor='w',pady=5)
        area=tk.Frame(self,bg='white');area.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(area,bg='#f6f7f1',highlightthickness=0,height=320)
        scrollbar=ttk.Scrollbar(area,orient='vertical',command=self.canvas.yview);scrollbar.pack(side='right',fill='y');self.canvas.pack(side='left',fill='both',expand=True);self.canvas.configure(yscrollcommand=scrollbar.set)
        self.inner=tk.Frame(self.canvas,bg='#f6f7f1');self.window=self.canvas.create_window(0,0,window=self.inner,anchor='nw')
        self.canvas.bind('<Configure>',self.resize);self.inner.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.refresh()

    # ปรับกริดการ์ดโดยไม่สร้างใบเสนอราคาอัตโนมัติ
    def resize(self,event):
        self.canvas.itemconfigure(self.window,width=event.width);columns=max(1,min(5,event.width//270))
        if columns!=self.columns:
            for i in range(5):self.inner.columnconfigure(i,weight=1 if i<columns else 0)
            self.columns=columns
            for i,tile in enumerate(self.tiles):tile.grid(row=i//columns,column=i%columns,sticky='nsew',padx=8,pady=8)

    # โหลดราคาปัจจุบันและดาวใหม่เมื่อข้อมูลออนไลน์กลับมา
    def refresh(self):
        rows=data.listing(self.app.current_user['id']);rows.sort(key=lambda row:(not row['favorite'],row['code']))
        for tile in self.inner.winfo_children():tile.destroy()
        self.tiles=[];self.images=[];self.columns=0;self.status.configure(text=self.app.visible_rate_message())
        for row in rows:
            if self.only.get() and not row['favorite']:continue
            tile=tk.Frame(self.inner,bg='white',highlightbackground='#dfe5d9',highlightthickness=1);self.tiles.append(tile)
            top=tk.Frame(tile,bg='white');top.pack(fill='x',padx=14,pady=(14,8));picture=flag(row['code']);self.images.append(picture)
            tk.Label(top,image=picture,bg='white').pack(side='left')
            tk.Label(top,text=row['code'],font=font(17,True),bg='white',fg='#173e33').pack(side='left',padx=10)
            self.app.button(top,'★' if row['favorite'] else '☆',lambda row=row:self.toggle(row),'secondary').pack(side='right')
            tk.Label(tile,text=row['name'],font=font(10),bg='white',fg='#788478',wraplength=230,anchor='w').pack(fill='x',padx=14)
            for title,key in (('ร้านรับซื้อ','buy'),('ร้านขาย','sell')):
                tk.Label(tile,text=f"{title}   {row[key]:,.4f}" if row[key]>0 else title+'   รอตั้งราคา',font=font(13,True),bg='white',fg='#173e33',anchor='w').pack(fill='x',padx=14,pady=(10,4))
            self.app.button(tile,'เลือกคำนวณ  ↗',lambda code=row['code']:self.app.select_currency(code)).pack(fill='x',padx=14,pady=(0,14))
        if not self.tiles:
            empty=tk.Label(self.inner,text='ยังไม่มีรายการโปรด · กด ☆ บนการ์ดเพื่อเพิ่ม',bg='#f6f7f1',fg='#788478',font=font(11));self.tiles.append(empty)
        # ผูกล้อเมาส์เฉพาะการ์ดนี้ ไม่รบกวนเมนูหรือหน้าต่างอื่น
        def bind_scroll(widget):
            widget.bind('<MouseWheel>',lambda e:(self.canvas.yview_scroll(-int(e.delta/120),'units'),'break')[-1])
            for child in widget.winfo_children():bind_scroll(child)
        bind_scroll(self.inner);self.resize(type('Size',(),{'width':max(270,self.canvas.winfo_width())})())

    # เก็บดาวให้บัญชีปัจจุบัน แล้วแสดงลำดับใหม่
    def toggle(self,row):
        data.favorite(self.app.current_user['id'],row['code'],not row['favorite']);self.app.update_rate_views()
