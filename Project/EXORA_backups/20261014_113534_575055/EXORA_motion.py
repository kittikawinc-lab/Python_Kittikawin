"""Small travel-themed canvas scenes; never draw over payment evidence."""
import math
import time
import tkinter as tk

class MotionScene:
    def __init__(self,canvas,enabled,login=False):
        self.canvas=canvas;self.enabled=enabled;self.login=login;self.timer=None;self.closed=False;self.started=time.monotonic()
        self.dots=[canvas.create_oval(0,0,0,0,fill='#b9d891',outline='',tags='motion') for _ in range(10)]
        self.rings=[canvas.create_oval(0,0,0,0,outline='#75a88d',width=1,tags='motion') for _ in range(3)]
        self.plane=canvas.create_polygon(0,0,0,0,0,0,fill='#d8ef9a' if login else '#125b4a',outline='',tags='motion')
        canvas.bind('<Destroy>',self.destroy,add='+');self.frame()
    def frame(self):
        if self.closed:return
        if not getattr(self.canvas,'winfo_ismapped',lambda:True)():
            self.timer=self.canvas.after(400,self.frame);return
        moving=self.enabled();phase=time.monotonic()-self.started if moving else 0
        width=max(1,self.canvas.winfo_width());height=max(1,self.canvas.winfo_height())
        base=height*.78 if self.login else height*.52
        spread=min(65,height*.15) if self.login else height*.28
        for index,item in enumerate(self.dots):
            x=((index+.5)*width/10+math.sin(phase*.3+index)*12)%width
            y=base+math.sin(phase*.7+index*1.7)*spread;r=2+index%3
            self.canvas.coords(item,x-r,y-r,x+r,y+r)
        for index,item in enumerate(self.rings):
            x=width*(.2+index*.3);y=base+math.cos(phase*.4+index)*spread
            r=8+3*math.sin(phase*.8+index)
            self.canvas.coords(item,x-r,y-r,x+r,y+r)
        x=width*(.1+.8*((phase/18)%1));y=base+math.sin(phase*.5)*spread*.6
        self.canvas.coords(self.plane,x+13,y,x-8,y-5,x-3,y,x-8,y+5)
        if self.login:self.canvas.coords('travel-image',0,math.sin(phase*.5)*4 if moving else 0)
        self.canvas.tag_raise('motion')
        self.timer=self.canvas.after(66 if moving else 400,self.frame)
    def destroy(self,event):
        if event.widget is self.canvas:
            self.closed=True
            if self.timer:
                try:self.canvas.after_cancel(self.timer)
                except tk.TclError:pass
                self.timer=None

def button_spring(button,enabled):
    from EXORA_effects import cancel,_schedule
    cancel(button,'spring')
    if not hasattr(button,'_exora_padding'):button._exora_padding=int(float(button.cget('pady')))
    original=button._exora_padding
    def step(frame=0):
        offset=0 if not enabled() else round(2*math.sin(math.pi*frame/12)*(1-frame/12))
        button.configure(pady=max(0,original-offset))
        if frame<12 and enabled():_schedule(button,'spring',lambda:step(frame+1))
    step()
