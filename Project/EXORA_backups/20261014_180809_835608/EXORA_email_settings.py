"""Public sender identity; the App Password stays in the environment."""
# คำอธิบาย import: นำเข้า os: os — อ่าน environment variables และทำงานร่วมกับระบบปฏิบัติการ
import os
SENDER='exoraadmin@gmail.com'
# คำอธิบาย def password: อ่าน Gmail App Password จาก environment โดยไม่ฝังรหัสในโค้ด
# รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
def password():return os.getenv('EXORA_GMAIL_APP_PASSWORD','').replace(' ','')
# คำอธิบาย def configured: ตรวจว่าตั้ง Gmail App Password แล้วหรือยัง
# รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
def configured():return bool(password())
