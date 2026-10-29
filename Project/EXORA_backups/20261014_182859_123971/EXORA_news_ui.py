# คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
import tkinter as tk
from tkinter import messagebox
# เปิดเว็บเฉพาะเมื่อผู้ใช้กดภาพข่าว
import webbrowser
# คำอธิบาย import: นำเข้า Image, ImageOps, ImageTk: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
# ImageOps: ปรับทิศทางภาพและย่อภาพให้พอดีกรอบ
# ImageTk: แปลงภาพ Pillow เป็น PhotoImage สำหรับ Tkinter
from PIL import Image, ImageOps, ImageTk
# คำอธิบาย import: นำเข้า EXORA_news as news: EXORA_news — จัดเก็บและจัดการภาพข่าว รวมตัวควบคุมการเลื่อนสไลด์
import EXORA_news as news
# คำอธิบาย import: นำเข้า EXORA_effects as effects: EXORA_effects — เอฟเฟกต์ปุ่ม เฟดภาพ และการแสดงผล พร้อมยกเลิก timer
import EXORA_effects as effects
# คำอธิบาย import: นำเข้า font: EXORA_layout — กำหนดขนาด ฟอนต์ และการเปลี่ยนหน้าสำหรับจอ FHD
# font: ฟังก์ชันกำหนดรูปแบบฟอนต์ของหน้าจอ
from EXORA_layout import font

class NewsSlideshow(tk.Frame):
    # คำอธิบาย def NewsSlideshow.__init__: เตรียมค่าเริ่มต้น ทรัพยากร และองค์ประกอบของคลาส NewsSlideshow
    # รับค่า: parent, motion | เรียกใช้: news.slides, news.AutoPlayer
    def __init__(self,parent,motion=lambda:True):
        super().__init__(parent,bg='#ffffff',highlightthickness=1,highlightbackground='#dfe5d9')
        self.items=news.slides();self.resize_timer=None;self.photo=None;self.original=None;self.displayed=None;self.motion=motion
        self.index=0
        self.canvas=tk.Canvas(self,height=225,bg='#eef3e8',highlightthickness=0);self.canvas.pack(fill='x')
        bottom=tk.Frame(self,bg='#ffffff');bottom.pack(padx=12,pady=10)
        self.player=news.AutoPlayer(self,len(self.items),self.show)
        for text,command in (('‹',lambda:self.player.move(-1)),('›',lambda:self.player.move(1))):
            button=tk.Button(bottom,text=text,command=command,bg='#eaf0e2',fg='#125b4a',font=font(14,True),relief='flat',width=3,cursor='hand2',state='normal' if len(self.items)>1 else 'disabled');button.pack(side='left',padx=3);effects.button_feedback(button,'#eaf0e2',motion)
        self.bind('<Destroy>',self.destroyed,add='+');self.canvas.bind('<Configure>',self.resized)
        self.canvas.bind('<Button-1>',self.open_link)
        self.canvas.bind('<Enter>',lambda event:self.player.pause(True))
        self.canvas.bind('<Leave>',lambda event:self.player.pause(False))
        self.show(0);self.player.start()

    # เปิดลิงก์ของข่าวที่แสดงอยู่ โดยตรวจชนิดลิงก์ซ้ำก่อนส่งให้เบราว์เซอร์
    def open_link(self,event=None):
        if not self.items or self.original is None:return
        try:
            url=news.validate_url(self.items[self.index].get('url') or '')
            if url:webbrowser.open(url,new=2)
        except (ValueError,OSError):messagebox.showerror('EXORA','เปิดลิงก์ข่าวไม่ได้ กรุณาติดต่อแอดมิน',parent=self)
    # คำอธิบาย def NewsSlideshow.destroyed: ยกเลิกงานที่ยังรอเมื่อ widget นี้ถูกทำลาย
    # รับค่า: event
    def destroyed(self,event):
        if event.widget is self:
            self.player.close()
            effects.cancel(self.canvas,'news-fade')
            if self.resize_timer:self.after_cancel(self.resize_timer);self.resize_timer=None
    # คำอธิบาย def NewsSlideshow.resized: รับเหตุการณ์เปลี่ยนขนาดและเลื่อนการวาดใหม่เพื่อลดงานซ้ำ
    # รับค่า: event
    def resized(self,event):
        if self.resize_timer:self.after_cancel(self.resize_timer)
        self.resize_timer=self.after(80,self.draw)
    # คำอธิบาย def NewsSlideshow.show: อ่านภาพและหัวข้อสไลด์ที่เลือกแล้วแสดงเฟดภาพ
    # รับค่า: index | เรียกใช้: news.image_path
    def show(self,index):
        self.original=None
        self.index=index
        self.canvas.configure(cursor='')
        if not self.items:
            self.draw();return
        item=self.items[index]
        try:
            with Image.open(news.image_path(item['image_path'])) as image:self.original=image.convert('RGB')
        except (OSError,ValueError):pass
        if self.original is not None and item.get('url'):self.canvas.configure(cursor='hand2')
        self.draw(fade=True)
    # คำอธิบาย def NewsSlideshow.draw: วาดภาพข่าวให้พอดีกรอบและเลือกแสดงแบบเฟดหรือทันที
    # รับค่า: fade
    def draw(self,fade=False):
        if self.resize_timer:self.after_cancel(self.resize_timer)
        effects.cancel(self.canvas,'news-fade')
        self.resize_timer=None;self.canvas.delete('all');width=max(1,self.canvas.winfo_width())
        # รักษาสัดส่วนภาพและจำกัดความสูง ไม่ครอปข้อความในภาพข่าว
        height=max(160,min(420,round(width*self.original.height/self.original.width))) if self.original else 180
        if int(self.canvas.cget('height'))!=height:self.canvas.configure(height=height)
        if self.original:
            image=ImageOps.contain(self.original,(width,height),Image.Resampling.LANCZOS)
            target=Image.new('RGB',(width,height),'#eef3e8');target.paste(image,((width-image.width)//2,(height-image.height)//2))
            item=self.canvas.create_image(0,0,anchor='nw')
            # คำอธิบาย def NewsSlideshow.draw.render: แสดงเฟรมภาพปัจจุบันบน Canvas และเก็บ reference ของ PhotoImage
            # รับค่า: frame
            def render(frame):
                self.displayed=frame;self.photo=ImageTk.PhotoImage(frame,master=self);self.canvas.itemconfigure(item,image=self.photo)
            if fade:effects.image_fade(self.canvas,self.displayed,target,render,self.motion)
            else:render(target)
        else:
            self.photo=None;self.canvas.create_text(width//2,height//2,text='GLOBAL FINANCE\nยังไม่มีภาพข่าว' if not self.items else 'ไม่พบภาพข่าว กรุณาติดต่อแอดมิน',fill='#125b4a',font=font(18,True),justify='center',width=max(1,width-30))
