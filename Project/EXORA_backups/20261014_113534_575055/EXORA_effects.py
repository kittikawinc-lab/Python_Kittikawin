"""Small native UI effects, with cancellation and reduced-motion support."""
import tkinter as tk

def mix(first,second,fraction):
    a=[int(first[i:i+2],16) for i in (1,3,5)];b=[int(second[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(x+(y-x)*fraction):02x}' for x,y in zip(a,b))

def cancel(widget,key):
    timers=getattr(widget,'_exora_timers',{})
    if key in timers:
        try:widget.after_cancel(timers.pop(key))
        except tk.TclError:pass

def _schedule(widget,key,callback):
    if not hasattr(widget,'_exora_timers'):
        widget._exora_timers={}
        def destroyed(event):
            if event.widget is widget:
                for name in list(widget._exora_timers):cancel(widget,name)
        widget.bind('<Destroy>',destroyed,add='+')
    def run():
        widget._exora_timers.pop(key,None)
        callback()
    widget._exora_timers[key]=widget.after(16,run)

def color_to(widget,option,target,enabled):
    key='color:'+option;cancel(widget,key);origin=widget.cget(option)
    def step(frame=0):
        if not enabled():widget.configure(**{option:target});return
        value=mix(origin,target,1-(1-frame/8)**3);widget.configure(**{option:value})
        if frame<8:_schedule(widget,key,lambda:step(frame+1))
    step()

def button_feedback(button,background,enabled):
    def base():return '#24725f' if getattr(button,'selected',False) else background
    def enter(event):
        if button.cget('state')!='disabled':color_to(button,'background',mix(base(),'#ffffff',.13),enabled)
    def leave(event):
        cancel(button,'color:background');button.configure(background=base(),relief='flat')
    button.bind('<Enter>',enter,add='+');button.bind('<Leave>',leave,add='+')
    def press(event):
        if button.cget('state')!='disabled':
            from EXORA_motion import button_spring
            button_spring(button,enabled)
            button.configure(relief='sunken');color_to(button,'background',mix(base(),'#000000',.14),enabled)
    def release(event):
        button.configure(relief='flat')
        if button.cget('state')!='disabled':color_to(button,'background',base(),enabled)
    button.bind('<ButtonPress-1>',press,add='+');button.bind('<ButtonRelease-1>',release,add='+')

def image_fade(widget,original,target,render,enabled):
    """Blend a news image into place; new slides cancel unfinished frames."""
    from PIL import Image
    cancel(widget,'news-fade')
    if original is None or original.size!=target.size:original=Image.new('RGB',target.size,'#eef3e8')
    def step(frame=0):
        fraction=1 if not enabled() else 1-(1-frame/18)**3
        render(target if fraction>=1 else Image.blend(original,target,fraction))
        if fraction<1:_schedule(widget,'news-fade',lambda:step(frame+1))
    step()

def page_reveal(canvas,enabled):
    """Thin progress accent settles as the new page slides into place."""
    cancel(canvas,'page-reveal');canvas.delete('page-reveal')
    if not enabled():return
    item=canvas.create_rectangle(0,0,0,3,fill='#125b4a',outline='',tags='page-reveal')
    def step(frame=0):
        if not enabled():canvas.delete('page-reveal');return
        canvas.coords(item,0,0,canvas.winfo_width()*(1-(1-frame/18)**3),3)
        canvas.itemconfigure(item,fill=mix('#125b4a','#f6f7f1',frame/18))
        if frame<18:_schedule(canvas,'page-reveal',lambda:step(frame+1))
        else:canvas.delete('page-reveal')
    step()

def card_feedback(card,enabled):
    def enter(event):color_to(card,'highlightbackground','#9cbc85',enabled)
    def leave(event):
        x,y=card.winfo_pointerxy()
        if card.winfo_rootx()<=x<card.winfo_rootx()+card.winfo_width() and card.winfo_rooty()<=y<card.winfo_rooty()+card.winfo_height():return
        color_to(card,'highlightbackground','#dfe5d9',enabled)
    card.bind('<Enter>',enter,add='+');card.bind('<Leave>',leave,add='+')

def number_reveal(label,value,formatter,enabled):
    cancel(label,'number')
    def step(frame=0):
        progress=1 if not enabled() else 1-(1-frame/14)**3
        label.configure(text=formatter(value*progress))
        if progress<1:_schedule(label,'number',lambda:step(frame+1))
    step()

def dialog_reveal(dialog,enabled):
    if not enabled():return
    try:dialog.attributes('-alpha',.90)
    except tk.TclError:return
    def step(frame=0):
        dialog.attributes('-alpha',1 if not enabled() else .90+.10*frame/8)
        if frame<8 and enabled():_schedule(dialog,'opacity',lambda:step(frame+1))
    _schedule(dialog,'opacity',step)

class BusyIndicator:
    def __init__(self,parent):
        self.frame=ttk_frame(parent)
        import tkinter.ttk as ttk
        self.caption=tk.Label(self.frame,text='',bg='#eaf1e1',fg='#125b4a',font=('Tahoma',-13),padx=15,pady=7)
        self.caption.pack(side='left')
        self.progress=ttk.Progressbar(self.frame,mode='indeterminate',length=115)
        self.progress.pack(side='right',padx=14)
        self.parent=parent
    def show(self,text,motion):
        self.caption.configure(text=text);self.frame.place(relx=1,x=-25,y=15,anchor='ne');self.frame.lift()
        if motion:self.progress.start(16)
    def hide(self):self.progress.stop();self.frame.place_forget()
    def destroy(self):self.progress.stop();self.frame.destroy()

def ttk_frame(parent):return tk.Frame(parent,bg='#eaf1e1',highlightbackground='#bed2ac',highlightthickness=1)
