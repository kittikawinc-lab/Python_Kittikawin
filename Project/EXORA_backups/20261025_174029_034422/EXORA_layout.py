"""FHD pixel sizing and cancellable native Tk page transitions."""
# คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
import tkinter as tk

CONTENT_MAX=1480
SIDEBAR_WIDTH=248

# คำอธิบาย def font: กำหนดหรือโหลดฟอนต์ตามขนาดที่ใช้แสดงผล
# รับค่า: size, bold
def font(size,bold=False):
    from EXORA_i18n import language
    from EXORA_fonts import family
    return (family(language),-max(11,round(size*1.35)),'bold' if bold else 'normal')

# คำอธิบาย def dialog_geometry: คำนวณขนาดและตำแหน่งหน้าต่างย่อยให้อยู่ภายในจอ
# รับค่า: screen_w, screen_h, owner_x, owner_y, owner_w, owner_h, width, height
def dialog_geometry(screen_w,screen_h,owner_x,owner_y,owner_w,owner_h,width,height):
    width=min(width,max(360,screen_w-80));height=min(height,max(400,screen_h-110))
    x=max(0,min(screen_w-width,owner_x+(owner_w-width)//2))
    y=max(0,min(screen_h-height-50,owner_y+(owner_h-height)//2))
    return width,height,x,y

class PageTransition:
    # คำอธิบาย def PageTransition.__init__: เตรียมค่าเริ่มต้น ทรัพยากร และองค์ประกอบของคลาส PageTransition
    # รับค่า: canvas, item, enabled
    def __init__(self,canvas,item,enabled):
        self.canvas=canvas;self.item=item;self.enabled=enabled;self.timer=None;self.generation=0
        canvas.bind('<Destroy>',self.destroy,add='+')
    # คำอธิบาย def PageTransition.position: คำนวณตำแหน่งแนวนอนกึ่งกลางเนื้อหา
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def position(self):
        width=max(1,self.canvas.winfo_width());return 0
    # คำอธิบาย def PageTransition.cancel: ยกเลิก timer ที่ยังรอทำงาน เพื่อไม่ให้แอนิเมชันเก่าค้าง
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def cancel(self):
        self.generation+=1
        if self.timer:
            try:self.canvas.after_cancel(self.timer)
            except tk.TclError:pass
            self.timer=None
    # คำอธิบาย def PageTransition.destroy: หยุด timer หรือคืนทรัพยากรเมื่อ widget ถูกทำลาย
    # รับค่า: event
    def destroy(self,event):
        if event.widget is self.canvas:self.cancel()
    # คำอธิบาย def PageTransition.start: เริ่มงานของตัวควบคุมและจัดการ timer เดิม
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def start(self):
        self.cancel();generation=self.generation
        if not self.enabled():self.canvas.coords(self.item,self.position(),0);return
        # คำอธิบาย def PageTransition.start.step: คำนวณค่าของเฟรมแอนิเมชันนี้ และตั้งเฟรมถัดไปจนถึงค่าเป้าหมาย
        # รับค่า: frame
        def step(frame=0):
            if generation!=self.generation:return
            self.timer=None
            if not self.enabled():self.canvas.coords(self.item,self.position(),0);return
            remaining=(1-frame/15)**3
            self.canvas.coords(self.item,self.position()+26*remaining,10*remaining)
            if frame<15:self.timer=self.canvas.after(16,lambda:step(frame+1))
        step()

# คำอธิบาย def tab_feedback: เพิ่มเอฟเฟกต์สั้น ๆ เมื่อเลือกแท็บและยกเลิก timer เมื่อปิด
# รับค่า: notebook, enabled
def tab_feedback(notebook,enabled):
    """Brief selected-tab accent; no animation over QR/payment controls."""
    pending={'id':None}
    # คำอธิบาย def tab_feedback.changed: ยกเลิกผลหรือเอฟเฟกต์เดิมหลังข้อมูลที่ผู้ใช้เลือกเปลี่ยน
    # รับค่า: event
    def changed(event):
        if pending['id']:
            try:notebook.after_cancel(pending['id'])
            except tk.TclError:pass
        if not enabled():return
        notebook.configure(style='Travel.TNotebook')
        # คำอธิบาย def tab_feedback.changed.restore: คืนรูปแบบแท็บหลังเอฟเฟกต์จบ
        # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
        def restore():pending['id']=None;notebook.configure(style='TNotebook')
        pending['id']=notebook.after(180,restore)
    # คำอธิบาย def tab_feedback.destroy: หยุด timer หรือคืนทรัพยากรเมื่อ widget ถูกทำลาย
    # รับค่า: event
    def destroy(event):
        if event.widget is notebook and pending['id']:
            try:notebook.after_cancel(pending['id'])
            except tk.TclError:pass
    notebook.bind('<<NotebookTabChanged>>',changed,add='+');notebook.bind('<Destroy>',destroy,add='+')
