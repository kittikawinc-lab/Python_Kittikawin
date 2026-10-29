"""Small native UI effects, with cancellation and reduced-motion support."""
# คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
import tkinter as tk

# คำอธิบาย def mix: ผสมค่าสีสองสีตามสัดส่วนเพื่อใช้ทำแอนิเมชัน
# รับค่า: first, second, fraction
def mix(first,second,fraction):
    a=[int(first[i:i+2],16) for i in (1,3,5)];b=[int(second[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(x+(y-x)*fraction):02x}' for x,y in zip(a,b))

# คำอธิบาย def cancel: ยกเลิก timer ที่ยังรอทำงาน เพื่อไม่ให้แอนิเมชันเก่าค้าง
# รับค่า: widget, key
def cancel(widget,key):
    timers=getattr(widget,'_exora_timers',{})
    if key in timers:
        try:widget.after_cancel(timers.pop(key))
        except tk.TclError:pass

# คำอธิบาย def _schedule: ตั้งเฟรมถัดไปและผูกการยกเลิก timer เมื่อ widget ถูกทำลาย
# รับค่า: widget, key, callback
def _schedule(widget,key,callback):
    if not hasattr(widget,'_exora_timers'):
        widget._exora_timers={}
        # คำอธิบาย def _schedule.destroyed: ยกเลิกงานที่ยังรอเมื่อ widget นี้ถูกทำลาย
        # รับค่า: event
        def destroyed(event):
            if event.widget is widget:
                for name in list(widget._exora_timers):cancel(widget,name)
        widget.bind('<Destroy>',destroyed,add='+')
    # คำอธิบาย def _schedule.run: ล้าง timer ที่กำลังทำงานแล้วเรียก callback
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def run():
        widget._exora_timers.pop(key,None)
        callback()
    widget._exora_timers[key]=widget.after(16,run)

# คำอธิบาย def color_to: เปลี่ยนสี widget ไปยังสีเป้าหมายอย่างนุ่มนวล
# รับค่า: widget, option, target, enabled
def color_to(widget,option,target,enabled):
    key='color:'+option;cancel(widget,key);origin=widget.cget(option)
    # คำอธิบาย def color_to.step: คำนวณค่าของเฟรมแอนิเมชันนี้ และตั้งเฟรมถัดไปจนถึงค่าเป้าหมาย
    # รับค่า: frame
    def step(frame=0):
        if not enabled():widget.configure(**{option:target});return
        value=mix(origin,target,1-(1-frame/8)**3);widget.configure(**{option:value})
        if frame<8:_schedule(widget,key,lambda:step(frame+1))
    step()

# คำอธิบาย def button_feedback: ผูกเอฟเฟกต์เมื่อชี้ กด และปล่อยปุ่ม
# รับค่า: button, background, enabled
def button_feedback(button,background,enabled):
    # คำอธิบาย def button_feedback.base: เลือกสีพื้นฐานตามสถานะเลือกเมนู
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def base():return '#24725f' if getattr(button,'selected',False) else background
    # คำอธิบาย def button_feedback.enter: ปรับรูปแบบเมื่อเมาส์เข้ามาในองค์ประกอบ
    # รับค่า: event
    def enter(event):
        if button.cget('state')!='disabled':color_to(button,'background',mix(base(),'#ffffff',.13),enabled)
    # คำอธิบาย def button_feedback.leave: คืนรูปแบบเมื่อเมาส์ออกจากองค์ประกอบ
    # รับค่า: event
    def leave(event):
        cancel(button,'color:background');button.configure(background=base(),relief='flat')
    button.bind('<Enter>',enter,add='+');button.bind('<Leave>',leave,add='+')
    # คำอธิบาย def button_feedback.press: แสดงเอฟเฟกต์กดปุ่มเมื่อปุ่มพร้อมใช้งาน
    # รับค่า: event
    def press(event):
        if button.cget('state')!='disabled':
            # คำอธิบาย import: นำเข้า button_spring: EXORA_motion — วาดยานพาหนะและองค์ประกอบเคลื่อนไหวตามธีมเดินทาง
            from EXORA_motion import button_spring
            button_spring(button,enabled)
            button.configure(relief='sunken');color_to(button,'background',mix(base(),'#000000',.14),enabled)
    # คำอธิบาย def button_feedback.release: คืนรูปแบบหลังปล่อยปุ่ม
    # รับค่า: event
    def release(event):
        button.configure(relief='flat')
        if button.cget('state')!='disabled':color_to(button,'background',base(),enabled)
    button.bind('<ButtonPress-1>',press,add='+');button.bind('<ButtonRelease-1>',release,add='+')

# คำอธิบาย def image_fade: ผสมภาพเดิมกับภาพใหม่เป็นเฟด โดยยกเลิกเฟรมเก่าเมื่อเปลี่ยนข่าว
# รับค่า: widget, original, target, render, enabled
def image_fade(widget,original,target,render,enabled):
    """Blend a news image into place; new slides cancel unfinished frames."""
    # คำอธิบาย import: นำเข้า Image: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
    # Image: อ่าน สร้าง และปรับภาพ
    from PIL import Image
    cancel(widget,'news-fade')
    if original is None or original.size!=target.size:original=Image.new('RGB',target.size,'#eef3e8')
    # คำอธิบาย def image_fade.step: คำนวณค่าของเฟรมแอนิเมชันนี้ และตั้งเฟรมถัดไปจนถึงค่าเป้าหมาย
    # รับค่า: frame
    def step(frame=0):
        fraction=1 if not enabled() else 1-(1-frame/18)**3
        render(target if fraction>=1 else Image.blend(original,target,fraction))
        if fraction<1:_schedule(widget,'news-fade',lambda:step(frame+1))
    step()

# คำอธิบาย def page_reveal: แสดงแถบสีเคลื่อนไหวสั้น ๆ ตอนเปลี่ยนหน้า
# รับค่า: canvas, enabled
def page_reveal(canvas,enabled):
    """Thin progress accent settles as the new page slides into place."""
    cancel(canvas,'page-reveal');canvas.delete('page-reveal')
    if not enabled():return
    item=canvas.create_rectangle(0,0,0,3,fill='#125b4a',outline='',tags='page-reveal')
    # คำอธิบาย def page_reveal.step: คำนวณค่าของเฟรมแอนิเมชันนี้ และตั้งเฟรมถัดไปจนถึงค่าเป้าหมาย
    # รับค่า: frame
    def step(frame=0):
        if not enabled():canvas.delete('page-reveal');return
        canvas.coords(item,0,0,canvas.winfo_width()*(1-(1-frame/18)**3),3)
        canvas.itemconfigure(item,fill=mix('#125b4a','#f6f7f1',frame/18))
        if frame<18:_schedule(canvas,'page-reveal',lambda:step(frame+1))
        else:canvas.delete('page-reveal')
    step()

# คำอธิบาย def card_feedback: เปลี่ยนสีขอบการ์ดเมื่อเลื่อนตัวชี้เข้าและออก
# รับค่า: card, enabled
def card_feedback(card,enabled):
    # คำอธิบาย def card_feedback.enter: ปรับรูปแบบเมื่อเมาส์เข้ามาในองค์ประกอบ
    # รับค่า: event
    def enter(event):color_to(card,'highlightbackground','#9cbc85',enabled)
    # คำอธิบาย def card_feedback.leave: คืนรูปแบบเมื่อเมาส์ออกจากองค์ประกอบ
    # รับค่า: event
    def leave(event):
        x,y=card.winfo_pointerxy()
        if card.winfo_rootx()<=x<card.winfo_rootx()+card.winfo_width() and card.winfo_rooty()<=y<card.winfo_rooty()+card.winfo_height():return
        color_to(card,'highlightbackground','#dfe5d9',enabled)
    card.bind('<Enter>',enter,add='+');card.bind('<Leave>',leave,add='+')

# คำอธิบาย def number_reveal: แสดงตัวเลขไล่ขึ้นจนถึงค่าจริง โดยไม่เปลี่ยนยอดธุรกรรม
# รับค่า: label, value, formatter, enabled
def number_reveal(label,value,formatter,enabled):
    cancel(label,'number')
    # คำอธิบาย def number_reveal.step: คำนวณค่าของเฟรมแอนิเมชันนี้ และตั้งเฟรมถัดไปจนถึงค่าเป้าหมาย
    # รับค่า: frame
    def step(frame=0):
        progress=1 if not enabled() else 1-(1-frame/14)**3
        label.configure(text=formatter(value*progress))
        if progress<1:_schedule(label,'number',lambda:step(frame+1))
    step()

# คำอธิบาย def dialog_reveal: ค่อย ๆ เพิ่มความทึบของหน้าต่างย่อย
# รับค่า: dialog, enabled
def dialog_reveal(dialog,enabled):
    if not enabled():return
    try:dialog.attributes('-alpha',.90)
    except tk.TclError:return
    # คำอธิบาย def dialog_reveal.step: คำนวณค่าของเฟรมแอนิเมชันนี้ และตั้งเฟรมถัดไปจนถึงค่าเป้าหมาย
    # รับค่า: frame
    def step(frame=0):
        dialog.attributes('-alpha',1 if not enabled() else .90+.10*frame/8)
        if frame<8 and enabled():_schedule(dialog,'opacity',lambda:step(frame+1))
    _schedule(dialog,'opacity',step)

class BusyIndicator:
    # คำอธิบาย def BusyIndicator.__init__: เตรียมค่าเริ่มต้น ทรัพยากร และองค์ประกอบของคลาส BusyIndicator
    # รับค่า: parent
    def __init__(self,parent):
        self.frame=ttk_frame(parent)
        # คำอธิบาย import: นำเข้า tkinter.ttk as ttk: tkinter.ttk — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
        import tkinter.ttk as ttk
        self.caption=tk.Label(self.frame,text='',bg='#eaf1e1',fg='#125b4a',font=('Tahoma',-13),padx=15,pady=7)
        self.caption.pack(side='left')
        self.progress=ttk.Progressbar(self.frame,mode='indeterminate',length=115)
        self.progress.pack(side='right',padx=14)
        self.parent=parent
    # คำอธิบาย def BusyIndicator.show: แสดงข้อมูลหรือ widget ตามสถานะของวัตถุนี้
    # รับค่า: text, motion
    def show(self,text,motion):
        self.caption.configure(text=text);self.frame.place(relx=1,x=-25,y=15,anchor='ne');self.frame.lift()
        if motion:self.progress.start(16)
    # คำอธิบาย def BusyIndicator.hide: ซ่อน widget และหยุดตัวแสดงความคืบหน้า
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def hide(self):self.progress.stop();self.frame.place_forget()
    # คำอธิบาย def BusyIndicator.destroy: หยุด timer หรือคืนทรัพยากรเมื่อ widget ถูกทำลาย
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def destroy(self):self.progress.stop();self.frame.destroy()

# คำอธิบาย def ttk_frame: สร้างกรอบสำหรับแสดงสถานะงานเบื้องหลัง
# รับค่า: parent
def ttk_frame(parent):return tk.Frame(parent,bg='#eaf1e1',highlightbackground='#bed2ac',highlightthickness=1)
