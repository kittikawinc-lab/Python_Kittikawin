"""Small travel-themed canvas scenes; never draw over payment evidence."""
# คำอธิบาย import: นำเข้า math: math — คำนวณเส้นทางแอนิเมชัน และตรวจว่าตัวเลขเป็นค่าจำกัด
import math
# คำอธิบาย import: นำเข้า time: time — จับเวลา เวลาหมดอายุ และรอบของแอนิเมชัน
import time
# คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
import tkinter as tk

class MotionScene:
    # คำอธิบาย def MotionScene.__init__: เตรียมค่าเริ่มต้น ทรัพยากร และองค์ประกอบของคลาส MotionScene
    # รับค่า: canvas, enabled, login, theme
    def __init__(self,canvas,enabled,login=False,theme='plane'):
        self.canvas=canvas;self.enabled=enabled;self.login=login;self.timer=None;self.closed=False;self.started=time.monotonic()
        self.theme=theme if theme in ('plane','car','train','boat') else 'plane'
        color=canvas.cget('background')
        dark=login or (color.startswith('#') and len(color)==7 and sum(int(color[i:i+2],16) for i in (1,3,5))<380)
        self.route=canvas.create_line(0,0,1,1,fill='#91b99a',dash=(5,7),width=1,tags='motion')
        self.clouds=[[canvas.create_oval(0,0,0,0,fill='#a5c8b0' if login else '#e0e9d8',outline='',tags='motion') for _ in range(3)] for _ in range(3)]
        self.pins=[(canvas.create_polygon(0,0,0,0,0,0,fill='#7aab79',outline='',tags='motion'),canvas.create_oval(0,0,0,0,fill='#d8ef9a',outline='',tags='motion')) for _ in range(3)]
        ink='#d8ef9a' if dark else '#125b4a';window='#125b4a' if dark else '#d8ef9a'
        shapes={
            'plane': [('polygon',[18,0,3,-3,-7,-12,-11,-12,-5,-2,-14,-2,-18,-6,-20,-5,-16,0,-20,5,-18,6,-14,2,-5,2,-11,12,-7,12,3,3],ink)],
            'car': [('polygon',[-19,4,-19,-3,-12,-5,-7,-13,9,-13,15,-5,21,-2,21,4],ink),('polygon',[-9,-5,-5,-10,6,-10,11,-5],window),('oval',[-14,1,-6,9],ink),('oval',[9,1,17,9],ink)],
            'train': [('polygon',[-25,3,-25,-12,17,-12,25,-4,25,3],ink),('polygon',[-20,-9,-13,-9,-13,-3,-20,-3],window),('polygon',[-8,-9,-1,-9,-1,-3,-8,-3],window),('polygon',[4,-9,15,-9,21,-3,4,-3],window),('oval',[-19,1,-12,8],ink),('oval',[12,1,19,8],ink)],
            'boat': [('polygon',[-23,1,24,1,16,9,-15,9],ink),('polygon',[-8,-2,-8,-22,11,-2],window),('polygon',[-11,-2,-11,-18,-22,-2],ink)]}
        self.parts=[]
        for kind,points,color in shapes[self.theme]:
            create=canvas.create_oval if kind=='oval' else canvas.create_polygon
            self.parts.append((create(*([0]*len(points)),fill=color,outline='',tags='motion'),points))
        canvas.bind('<Destroy>',self.destroy,add='+');self.frame()
    # คำอธิบาย def MotionScene.frame: คำนวณตำแหน่งองค์ประกอบในเฟรมปัจจุบันและตั้ง timer เฟรมถัดไป
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def frame(self):
        if self.closed:return
        if not getattr(self.canvas,'winfo_ismapped',lambda:True)():
            self.timer=self.canvas.after(400,self.frame);return
        moving=self.enabled();phase=time.monotonic()-self.started if moving else 0
        width=max(1,self.canvas.winfo_width());height=max(1,self.canvas.winfo_height())
        base=height*.83 if self.login else height*.68
        scale=min(1.2,max(.4,height/42));spread=min(25,height*.12)
        path=[]
        for point in range(25):
            fraction=point/24;path.extend((width*(.07+.86*fraction),base-(math.sin(math.pi*fraction)*spread if self.theme=='plane' else 0)))
        self.canvas.coords(self.route,*path)
        for index,cloud in enumerate(self.clouds):
            x=width*((.2+index*.3+phase*.003)%1);y=(height*.68 if self.login else height*.24)
            for part,item in enumerate(cloud):
                dx=(part-1)*8*scale;r=(8 if part==1 else 6)*scale
                self.canvas.coords(item,x+dx-r,y-r,x+dx+r,y+r)
        for index,(pin,center) in enumerate(self.pins):
            x=width*(.09+index*.41);y=base;bob=math.sin(phase*.8+index)*1.5 if moving else 0
            self.canvas.coords(pin,x,y,x-5*scale,y-9*scale+bob,x,y-15*scale+bob,x+5*scale,y-9*scale+bob)
            self.canvas.coords(center,x-2*scale,y-11*scale+bob,x+2*scale,y-7*scale+bob)
        fraction=(phase/20)%1 if moving else .45
        x=width*(.07+.86*fraction);y=base-(math.sin(math.pi*fraction)*spread if self.theme=='plane' else 0)-5*scale
        for item,points in self.parts:self.canvas.coords(item,*[value*scale+(x if index%2==0 else y) for index,value in enumerate(points)])
        if self.login:self.canvas.coords('travel-image',0,math.sin(phase*.5)*4 if moving else 0)
        self.canvas.tag_raise('motion')
        self.timer=self.canvas.after(66 if moving else 400,self.frame)
    # คำอธิบาย def MotionScene.destroy: หยุด timer หรือคืนทรัพยากรเมื่อ widget ถูกทำลาย
    # รับค่า: event
    def destroy(self,event):
        if event.widget is self.canvas:
            self.closed=True
            if self.timer:
                try:self.canvas.after_cancel(self.timer)
                except tk.TclError:pass
                self.timer=None

# คำอธิบาย def button_spring: ปรับ padding ปุ่มเป็นจังหวะยุบ–คืนตัวโดยรักษาค่าเดิม
# รับค่า: button, enabled
def button_spring(button,enabled):
    # คำอธิบาย import: นำเข้า cancel, _schedule: EXORA_effects — เอฟเฟกต์ปุ่ม เฟดภาพ และการแสดงผล พร้อมยกเลิก timer
    from EXORA_effects import cancel,_schedule
    cancel(button,'spring')
    if not hasattr(button,'_exora_padding'):button._exora_padding=int(float(button.cget('pady')))
    original=button._exora_padding
    # คำอธิบาย def button_spring.step: คำนวณค่าของเฟรมแอนิเมชันนี้ และตั้งเฟรมถัดไปจนถึงค่าเป้าหมาย
    # รับค่า: frame
    def step(frame=0):
        offset=0 if not enabled() else round(2*math.sin(math.pi*frame/12)*(1-frame/12))
        button.configure(pady=max(0,original-offset))
        if frame<12 and enabled():_schedule(button,'spring',lambda:step(frame+1))
    step()
