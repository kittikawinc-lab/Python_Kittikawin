"""Offline travel illustrations and a design preview shared with the native login."""
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า Image, ImageDraw, ImageFont: PIL — อ่าน ตรวจสอบ ปรับขนาด วาดภาพ และแสดงภาพผ่าน Pillow
# Image: อ่าน สร้าง และปรับภาพ
# ImageDraw: วาดรูปทรงและข้อความลงภาพ
# ImageFont: โหลดฟอนต์เพื่อวาดข้อความ
from PIL import Image,ImageDraw,ImageFont
# คำอธิบาย import: นำเข้า EXORA_brand as brand: EXORA_brand — วาดโลโก้และองค์ประกอบแบรนด์ EXORA
import EXORA_brand as brand
import EXORA_i18n as i18n

BG='#f6f7f1';GREEN='#125b4a';INK='#173e33';LIME='#d8ef9a'
# คำอธิบาย def font: กำหนดหรือโหลดฟอนต์ตามขนาดที่ใช้แสดงผล
# รับค่า: size, bold
def font(size,bold=False):
    path=Path('C:/Windows/Fonts')/('tahomabd.ttf' if bold else 'tahoma.ttf')
    if i18n.language=='zh' and Path('C:/Windows/Fonts/msyh.ttc').is_file():path=Path('C:/Windows/Fonts/msyh.ttc')
    return ImageFont.truetype(str(path),max(10,int(size)))

# คำอธิบาย def login_size: คำนวณขนาดกรอบล็อกอินตามพื้นที่หน้าจอ
# รับค่า: width, height
def login_size(width,height):return min(1640,max(760,width-96)),min(860,max(560,height-100))

# คำอธิบาย def mark: วาดโลโก้ลงในภาพ Pillow
# รับค่า: draw, x, y, size, color
def mark(draw,x,y,size,color=GREEN):
    s=size/128;draw.ellipse((x+4*s,y+4*s,x+124*s,y+124*s),fill=color)
    draw.ellipse((x+15*s,y+15*s,x+113*s,y+113*s),outline='#80ab92',width=max(1,int(s)))
    for fill,points in brand.SHAPES:draw.polygon([(x+a*s,y+b*s) for a,b in points],fill=fill)
    draw.ellipse((x+58*s,y+58*s,x+70*s,y+70*s),fill=color)

# คำอธิบาย def hero: สร้างภาพประกอบการเดินทางสำหรับหน้าล็อกอิน
# รับค่า: width, height
def hero(width=900,height=860):
    w,h=900,860;image=Image.new('RGB',(w,h),GREEN);d=ImageDraw.Draw(image)
    d.ellipse((180,355,920,1060),fill='#206550');d.ellipse((275,425,830,980),outline='#548566',width=2)
    mark(d,49,42,59);d.text((125,48),'EXORA',font=font(32,True),fill='white')
    d.text((53,120),'EXCHANGE FOR YOUR NEXT JOURNEY',font=font(13),fill=LIME)
    d.text((49,175),'Your next journey,',font=font(48,True),fill='white')
    d.text((49,238),'starts with EXORA.',font=font(48,True),fill='white')
    d.text((53,319),i18n.translate('แลกเงินอย่างมั่นใจ พร้อมออกเดินทางไปทุกจุดหมาย'),font=font(20),fill='#d8e6d7')
    # Air route, aircraft and currencies: original vector-style travel artwork.
    for x in range(290,800,17):
        y=460-int(70*(1-((x-545)/260)**2));d.ellipse((x,y,x+3,y+3),fill='#b8d49a')
    d.polygon([(368,428),(731,383),(770,393),(730,407),(533,456),(432,543),(403,546),(450,475),(340,500),(310,476),(421,448)],fill='#f9fbef')
    d.polygon([(477,432),(401,368),(421,354),(546,413)],fill='#b3d6b7')
    d.line((421,448,717,393),fill='#92bb9b',width=3)
    for x,y,label,color in [(666,506,'USD  $','#e8efce'),(731,574,'EUR  €','#f6eed2')]:
        d.rounded_rectangle((x,y,x+125,y+69),radius=12,fill=color)
        d.text((x+20,y+24),label,font=font(20,True),fill=INK)
    d.rounded_rectangle((90,452,275,677),radius=20,fill='#092f32',outline='#769c7e',width=2)
    mark(d,144,478,82,color='#092f32');d.text((126,586),'PASSPORT',font=font(21,True),fill='#cee0b7')
    d.text((119,626),'EXORA / EXPLORER',font=font(11),fill='#91ae94')
    d.rounded_rectangle((276,522,365,545),radius=6,outline='#c8da9d',width=7)
    d.rounded_rectangle((258,542,430,704),radius=17,fill='#d8ef9a')
    for x in (286,312,338,365,392):d.line((x,558,x,688),fill='#b8ce7b',width=3)
    d.ellipse((283,699,299,715),fill='#0b3c30');d.ellipse((390,699,406,715),fill='#0b3c30')
    d.rounded_rectangle((457,649,815,762),radius=12,fill='#faf8ed')
    d.text((480,668),'BOARDING PASS',font=font(12,True),fill='#6b8260')
    d.text((480,698),'BKK  →  YOUR NEXT STOP',font=font(17,True),fill=INK)
    for x in range(755,794,4):d.rectangle((x,672,x+1,733),fill=INK)
    d.text((53,807),'PLAN  ·  EXCHANGE  ·  EXPLORE',font=font(12),fill='#b7d1b4')
    return image.resize((max(1,width),max(1,height)),Image.Resampling.LANCZOS)

# คำอธิบาย def preview: สร้างภาพตัวอย่างการออกแบบ ไม่ใช่ภาพจับหน้าจอจริง
# รับค่า: destination, width, height
def preview(destination,width=1920,height=1080):
    image=Image.new('RGB',(width,height),BG);d=ImageDraw.Draw(image)
    d.rectangle((0,0,width,30),fill='#e5f6f1');mark(d,3,3,24);d.text((34,5),'EXORA | Currency Exchange',font=font(16),fill=INK)
    stage_w,stage_h=login_size(width,height-30);x=(width-stage_w)//2;y=30+(height-30-stage_h)//2
    left=int(stage_w*.55);d.rounded_rectangle((x-1,y-1,x+stage_w+1,y+stage_h+1),radius=12,fill='white',outline='#e0e7d8')
    image.paste(hero(left,stage_h),(x,y))
    form_x=x+left+(stage_w-left-460)//2;top=y+(stage_h-514)//2
    d.text((form_x,top),'WELCOME TO EXORA',font=font(12),fill='#788478')
    d.text((form_x,top+36),'ยินดีต้อนรับกลับ',font=font(34,True),fill=INK)
    d.text((form_x,top+90),'เข้าสู่ระบบเพื่อเริ่มการเดินทางครั้งใหม่ของคุณ',font=font(15),fill='#788478')
    for row,label in [(0,'ชื่อผู้ใช้ หรืออีเมล'),(1,'รหัสผ่าน')]:
        sy=top+143+row*92;d.text((form_x,sy),label,font=font(14),fill='#657867')
        d.rounded_rectangle((form_x,sy+27,form_x+460,sy+73),radius=5,fill='#fbfcf7',outline='#cbd8c6')
    d.rounded_rectangle((form_x,top+347,form_x+460,top+396),radius=6,fill=GREEN)
    text='เข้าสู่ระบบ';bbox=d.textbbox((0,0),text,font=font(15,True));d.text((form_x+(460-bbox[2])/2,top+363),text,font=font(15,True),fill='white')
    d.line((form_x+294,top+379,form_x+304,top+369),fill='white',width=2);d.line((form_x+296,top+369,form_x+304,top+369,form_x+304,top+377),fill='white',width=2)
    for yy,text in [(428,'ยังไม่มีบัญชี?  สมัครสมาชิก'),(471,'ลืมรหัสผ่าน?  รับ OTP ทางอีเมล')]:
        bbox=d.textbbox((0,0),text,font=font(14));d.text((form_x+(460-bbox[2])/2,top+yy),text,font=font(14),fill=GREEN)
    d.text((x+left+55,y+stage_h-35),'WINDOWS DESKTOP EDITION  ·  EXORA',font=font(11),fill='#8a9785')
    image.save(destination)
