import tkinter as tk
from PIL import Image, ImageOps, ImageTk
import EXORA_news as news
from EXORA_layout import font

class NewsSlideshow(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent,bg='#ffffff',highlightthickness=1,highlightbackground='#dfe5d9')
        self.items=news.slides();self.resize_timer=None;self.photo=None;self.original=None
        header=tk.Frame(self,bg='#ffffff');header.pack(fill='x',padx=18,pady=(12,8))
        tk.Label(header,text='GLOBAL FINANCE / ข่าวการเงินโลก',bg='#ffffff',fg='#125b4a',font=font(11,True)).pack(side='left')
        self.counter=tk.Label(header,bg='#ffffff',fg='#788478',font=font(9));self.counter.pack(side='right')
        self.canvas=tk.Canvas(self,height=225,bg='#eef3e8',highlightthickness=0);self.canvas.pack(fill='x',padx=12)
        bottom=tk.Frame(self,bg='#ffffff');bottom.pack(fill='x',padx=12,pady=10)
        self.title=tk.Label(bottom,bg='#ffffff',fg='#173e33',font=font(11,True),anchor='w',justify='left',wraplength=600);self.title.pack(side='left',fill='x',expand=True)
        self.player=news.AutoPlayer(self,len(self.items),self.show)
        for text,command in (('‹',lambda:self.player.move(-1)),('›',lambda:self.player.move(1))):
            tk.Button(bottom,text=text,command=command,bg='#eaf0e2',fg='#125b4a',font=font(14,True),relief='flat',width=3,cursor='hand2',state='normal' if len(self.items)>1 else 'disabled').pack(side='left',padx=3)
        self.pause_button=tk.Button(bottom,text='หยุด',command=self.toggle,bg='#eaf0e2',fg='#125b4a',font=font(9),relief='flat',cursor='hand2',state='normal' if len(self.items)>1 else 'disabled');self.pause_button.pack(side='left',padx=3)
        self.bind('<Destroy>',self.destroyed,add='+');self.canvas.bind('<Configure>',self.resized)
        self.show(0);self.player.start()
    def toggle(self):
        self.player.pause(not self.player.paused);self.pause_button.configure(text='เล่น' if self.player.paused else 'หยุด')
    def destroyed(self,event):
        if event.widget is self:
            self.player.close()
            if self.resize_timer:self.after_cancel(self.resize_timer);self.resize_timer=None
    def resized(self,event):
        self.title.configure(wraplength=max(160,event.width-210))
        if self.resize_timer:self.after_cancel(self.resize_timer)
        self.resize_timer=self.after(80,self.draw)
    def show(self,index):
        self.original=None
        if not self.items:
            self.title.configure(text='ยังไม่มีข่าวที่เผยแพร่');self.counter.configure(text='EXORA NEWS');self.draw();return
        item=self.items[index];self.title.configure(text=item['title']);self.counter.configure(text=f'{index+1} / {len(self.items)} · เปลี่ยนทุก 6 วินาที')
        try:
            with Image.open(news.image_path(item['image_path'])) as image:self.original=image.convert('RGB')
        except (OSError,ValueError):pass
        self.draw()
    def draw(self):
        if self.resize_timer:self.after_cancel(self.resize_timer)
        self.resize_timer=None;self.canvas.delete('all');width=max(1,self.canvas.winfo_width());height=225
        if self.original:
            image=ImageOps.contain(self.original,(width,height),Image.Resampling.LANCZOS);self.photo=ImageTk.PhotoImage(image,master=self)
            self.canvas.create_image(width//2,height//2,image=self.photo)
        else:
            self.photo=None;self.canvas.create_text(width//2,height//2,text='GLOBAL FINANCE\nยังไม่มีภาพข่าว' if not self.items else 'ไม่พบภาพข่าว กรุณาติดต่อแอดมิน',fill='#125b4a',font=font(18,True),justify='center',width=max(1,width-30))
