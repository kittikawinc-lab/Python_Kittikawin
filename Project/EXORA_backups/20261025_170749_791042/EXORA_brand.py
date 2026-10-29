"""Code-native EXORA compass logo and lightweight Tk travel animation."""
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า math: math — คำนวณเส้นทางแอนิเมชัน และตรวจว่าตัวเลขเป็นค่าจำกัด
import math
# คำอธิบาย import: นำเข้า time: time — จับเวลา เวลาหมดอายุ และรอบของแอนิเมชัน
import time
# คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
import tkinter as tk
# คำอธิบาย import: นำเข้า font as ui_font: EXORA_layout — กำหนดขนาด ฟอนต์ และการเปลี่ยนหน้าสำหรับจอ FHD
# ui_font: ฟังก์ชันกำหนดรูปแบบฟอนต์ของหน้าจอ
from EXORA_layout import font as ui_font
# คำอธิบาย import: นำเข้า Image, ImageDraw: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
# ImageDraw: วาดรูปทรงและข้อความลงภาพ
from PIL import Image, ImageDraw

GREEN='#125b4a';LIME='#d8ef9a';CREAM='#eef4e5'
SHAPES=[('#ffffff',[(58,59),(62,48),(100,22),(80,62),(69,69)]),
        (LIME,[(70,69),(66,80),(28,106),(48,66),(59,59)]),
        ('#ffffff',[(58,62),(46,58),(23,23),(58,46),(66,58)]),
        (LIME,[(70,66),(82,70),(105,105),(70,82),(62,70)])]

# คำอธิบาย def draw_mark: วาดสัญลักษณ์โลโก้ EXORA ลงบน Canvas
# รับค่า: canvas, x, y, size, color
def draw_mark(canvas,x,y,size,color=GREEN):
    scale=size/128
    canvas.create_oval(x+4*scale,y+4*scale,x+124*scale,y+124*scale,fill=color,outline=color)
    canvas.create_oval(x+15*scale,y+15*scale,x+113*scale,y+113*scale,outline='#71a18a',width=max(1,scale))
    for fill,points in SHAPES:
        canvas.create_polygon(*[v for px,py in points for v in (x+px*scale,y+py*scale)],fill=fill,outline='')
    canvas.create_oval(x+58*scale,y+58*scale,x+70*scale,y+70*scale,fill=color,outline='')

# คำอธิบาย def header: สร้างส่วนหัวที่แสดงโลโก้และชื่อร้าน
# รับค่า: parent, name, dark, color, width
def header(parent,name='EXORA',dark=False,color=GREEN,width=350):
    bg=color if dark else parent.cget('bg')
    canvas=tk.Canvas(parent,width=width,height=64,bg=bg,highlightthickness=0)
    draw_mark(canvas,0,0,60,color)
    canvas.create_text(72,29,text=name,fill='white' if dark else color,anchor='w',font=ui_font(17 if width<=220 else 24,True))
    return canvas

# คำอธิบาย def export_assets: สร้างไฟล์โลโก้ SVG และไอคอน PNG
# รับค่า: directory
def export_assets(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="160" viewBox="0 0 640 160">',
         '<g transform="translate(12 16)"><circle cx="64" cy="64" r="60" fill="#125b4a"/><circle cx="64" cy="64" r="49" fill="none" stroke="#71a18a"/>']
    for fill,points in SHAPES:svg.append('<polygon fill="'+fill+'" points="'+' '.join(f'{x},{y}' for x,y in points)+'"/>')
    svg.extend(['<circle cx="64" cy="64" r="6" fill="#125b4a"/></g>',
                '<text x="162" y="99" fill="#125b4a" font-family="Leelawadee UI, sans-serif" font-size="72" font-weight="700" letter-spacing="5">EXORA</text>',
                '<text x="168" y="132" fill="#617c66" font-family="Leelawadee UI, sans-serif" font-size="13" letter-spacing="3">EXCHANGE FOR YOUR NEXT JOURNEY</text></svg>'])
    (directory/'EXORA_logo.svg').write_text('\n'.join(svg),encoding='utf-8')
    image=Image.new('RGBA',(768,768),(0,0,0,0));draw=ImageDraw.Draw(image)
    draw.ellipse((24,24,744,744),fill=GREEN);draw.ellipse((90,90,678,678),outline='#71a18a',width=6)
    for fill,points in SHAPES:draw.polygon([(x*6,y*6) for x,y in points],fill=fill)
    draw.ellipse((348,348,420,420),fill=GREEN)
    image.resize((256,256),Image.Resampling.LANCZOS).save(directory/'EXORA_icon.png')

# คำอธิบาย def journey_scene: วาดลูกโลกและเครื่องบินเคลื่อนไหว พร้อมหยุด timer เมื่อออกจากหน้า
# รับค่า: canvas, enabled
def journey_scene(canvas,enabled=lambda:True):
    """Draw a globe and animated plane. Timers stop when the canvas is destroyed."""
    bg=canvas.cget('bg');ink=GREEN
    canvas.create_oval(105,22,310,227,fill=CREAM,outline='#a7bb96',width=2)
    for inset in (28,65):canvas.create_oval(105+inset,22,310-inset,227,outline='#c7d5b9')
    for y in (68,116,168):canvas.create_line(120,y,295,y,fill='#c7d5b9')
    canvas.create_arc(63,55,330,214,start=0,extent=180,style='arc',outline='#80a463',dash=(4,5),width=2)
    for x,y,label in [(85,164,'BKK'),(201,56,'NRT'),(312,157,'CDG')]:
        canvas.create_oval(x-5,y-5,x+5,y+5,fill=ink,outline=bg)
        canvas.create_text(x,y+17,text=label,font=ui_font(9,True),fill=ink)
    canvas.create_text(27,22,text='YOUR NEXT CHAPTER',anchor='w',font=ui_font(8),fill='#698560')
    canvas.create_rectangle(30,188,92,232,fill=GREEN,outline='')
    canvas.create_rectangle(50,179,72,188,outline=GREEN,width=3)
    canvas.create_line(61,191,61,231,fill=LIME,width=2)
    plane=canvas.create_polygon(0,0,0,0,0,0,fill=ink,outline=LIME,width=1)
    started=time.monotonic();timer={'id':None,'dead':False}
    # คำอธิบาย def journey_scene.frame: คำนวณตำแหน่งองค์ประกอบในเฟรมปัจจุบันและตั้ง timer เฟรมถัดไป
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def frame():
        if timer['dead']:return
        phase=((time.monotonic()-started)/12)%1 if enabled() else .55
        angle=math.pi*(1-phase);x=196+123*math.cos(angle);y=157-84*math.sin(angle)
        heading=math.atan2(84*math.cos(angle),123*math.sin(angle))
        shape=[(14,0),(-10,-6),(-5,0),(-10,6)]
        points=[]
        for px,py in shape:points.extend((x+px*math.cos(heading)-py*math.sin(heading),y+px*math.sin(heading)+py*math.cos(heading)))
        canvas.coords(plane,*points)
        timer['id']=canvas.after(50,frame)
    # คำอธิบาย def journey_scene.stop: หยุดแอนิเมชันและยกเลิก timer เมื่อออกจากหน้า
    # รับค่า: event
    def stop(event):
        if event.widget is canvas:
            timer['dead']=True
            if timer['id']:
                try:canvas.after_cancel(timer['id'])
                except tk.TclError:pass
    canvas.bind('<Destroy>',stop,add='+');frame()

# คำอธิบาย def travel_ribbon: วาดเส้นทางและเครื่องบินในแถบตกแต่งรุ่นเดิม
# รับค่า: canvas, enabled
def travel_ribbon(canvas,enabled=lambda:True):
    line=canvas.create_line(15,19,550,19,fill='#c8d7b9',dash=(4,5))
    marker=canvas.create_text(15,19,text='✈',fill=GREEN,font=ui_font(15))
    started=time.monotonic();timer={'id':None,'dead':False}
    # คำอธิบาย def travel_ribbon.frame: คำนวณตำแหน่งองค์ประกอบในเฟรมปัจจุบันและตั้ง timer เฟรมถัดไป
    # รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
    def frame():
        if timer['dead']:return
        width=max(150,canvas.winfo_width()-20);canvas.coords(line,15,19,width,19)
        phase=((time.monotonic()-started)/18)%1 if enabled() else .5
        canvas.coords(marker,15+(width-15)*phase,19)
        timer['id']=canvas.after(60,frame)
    # คำอธิบาย def travel_ribbon.stop: หยุดแอนิเมชันและยกเลิก timer เมื่อออกจากหน้า
    # รับค่า: event
    def stop(event):
        if event.widget is canvas:
            timer['dead']=True
            if timer['id']:
                try:canvas.after_cancel(timer['id'])
                except tk.TclError:pass
    canvas.bind('<Destroy>',stop,add='+');frame()
