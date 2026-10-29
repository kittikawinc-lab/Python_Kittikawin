"""FHD pixel sizing and cancellable native Tk page transitions."""
import tkinter as tk

CONTENT_MAX=1480
SIDEBAR_WIDTH=248

def font(size,bold=False):
    return ('Tahoma',-max(11,round(size*1.35)),'bold' if bold else 'normal')

def dialog_geometry(screen_w,screen_h,owner_x,owner_y,owner_w,owner_h,width,height):
    width=min(width,max(360,screen_w-80));height=min(height,max(400,screen_h-110))
    x=max(0,min(screen_w-width,owner_x+(owner_w-width)//2))
    y=max(0,min(screen_h-height-50,owner_y+(owner_h-height)//2))
    return width,height,x,y

class PageTransition:
    def __init__(self,canvas,item,enabled):
        self.canvas=canvas;self.item=item;self.enabled=enabled;self.timer=None;self.generation=0
        canvas.bind('<Destroy>',self.destroy,add='+')
    def position(self):
        width=max(1,self.canvas.winfo_width());return max(0,(width-min(width,CONTENT_MAX))/2)
    def cancel(self):
        self.generation+=1
        if self.timer:
            try:self.canvas.after_cancel(self.timer)
            except tk.TclError:pass
            self.timer=None
    def destroy(self,event):
        if event.widget is self.canvas:self.cancel()
    def start(self):
        self.cancel();generation=self.generation
        if not self.enabled():self.canvas.coords(self.item,self.position(),0);return
        def step(frame=0):
            if generation!=self.generation:return
            self.timer=None
            if not self.enabled():self.canvas.coords(self.item,self.position(),0);return
            remaining=(1-frame/15)**3
            self.canvas.coords(self.item,self.position()+26*remaining,10*remaining)
            if frame<15:self.timer=self.canvas.after(16,lambda:step(frame+1))
        step()

def tab_feedback(notebook,enabled):
    """Brief selected-tab accent; no animation over QR/payment controls."""
    pending={'id':None}
    def changed(event):
        if pending['id']:
            try:notebook.after_cancel(pending['id'])
            except tk.TclError:pass
        if not enabled():return
        notebook.configure(style='Travel.TNotebook')
        def restore():pending['id']=None;notebook.configure(style='TNotebook')
        pending['id']=notebook.after(180,restore)
    def destroy(event):
        if event.widget is notebook and pending['id']:
            try:notebook.after_cancel(pending['id'])
            except tk.TclError:pass
    notebook.bind('<<NotebookTabChanged>>',changed,add='+');notebook.bind('<Destroy>',destroy,add='+')
