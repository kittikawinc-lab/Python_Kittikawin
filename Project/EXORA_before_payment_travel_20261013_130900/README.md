# EXORA Desktop — Python/Tkinter บน Windows

เปิดโฟลเดอร์โปรเจกต์ใน VS Code เปิด `EXORA_main.py` แล้วกด **Run Python File** เหมือนเดิม หรือกด F5 เลือก **EXORA Desktop** โปรแกรมเปิดเป็นหน้าต่าง Tkinter ไม่มีเว็บเซิร์ฟเวอร์และไม่เปิดเบราว์เซอร์

เลือก Python interpreter ที่มี Pillow และ ReportLab หากยังไม่มี ใช้ `python -m pip install -r requirements.txt` หรือใช้ Python ที่มากับ Codex ซึ่งทดสอบ dependencies แล้วที่ `%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` ตัวเปิด `Start_EXORA.bat` ใช้ Python ชุดนี้บนเครื่องนี้ได้

## การใช้งาน

- เข้าสู่ระบบด้วยบัญชี EXORA เดิม หรือสมัครบัญชีใหม่
- หน้าร้านมีอัตรารับซื้อ/ขายต่อ 1 หน่วยเทียบบาท และเครื่องคำนวณ จำนวนเงินต้นทาง × ราคารับซื้อ / ราคาขายปลายทาง โดย THB ใช้อัตรา 1 ปัดยอดเป็น 2 หลักทศนิยม
- คำนวณและทำรายการ กรอกชื่อลูกค้า/เบอร์โทร เลือกสลิป JPG/PNG ไม่เกิน 10 MB แล้วส่งตรวจสอบ ระบบคัดลอกสลิปไว้ใน EXORA_assets/slips
- ประวัติของผู้ใช้แสดงเฉพาะรายการตนเอง ส่วน admin เห็นทุกคน คลิกดูรายละเอียดเพื่อตรวจสลิปและบันทึก PDF
- admin ใช้เมนูตรวจสอบสลิป อนุมัติหรือปฏิเสธพร้อมเหตุผล ผู้ใช้แนบสลิปใหม่ได้เมื่อถูกปฏิเสธ มีประวัติการตรวจสอบเก็บไว้
- โปรไฟล์แก้ชื่อ อีเมล เบอร์โทร แนะนำตัว รูป และสีได้ในโปรแกรม เปลี่ยนรหัสผ่านโดยตรวจรหัสปัจจุบัน
- admin เปลี่ยนชื่อ/สี/ข้อความ/ข้อมูลติดต่อร้าน ตั้งอัตรา และจัดการสิทธิ์ผู้ใช้ได้
- PDF สถานะอนุมัติเป็นใบเสร็จ สถานะอื่นเป็นสรุปรายการ ส่ง Gmail ได้เฉพาะรายการอนุมัติ โดยผู้ใช้กดส่งและตรวจอีเมลปลายทางก่อนส่ง

QR เป็น placeholder แสดงขั้นตอนเท่านั้น ไม่ใช่ QR จ่ายเงินจริง ไม่มีการยืนยันธนาคารอัตโนมัติ การอนุมัติสลิปเป็นการตรวจสอบโดยเจ้าหน้าที่ อัตราเป็นราคาที่ร้านตั้งเอง ไม่มีการจัดการเงินสดคงเหลือ

## รักษาข้อมูลเดิม

ใช้ชื่อไฟล์หลักเดิม: EXORA_main.py, EXORA_gui.py, EXORA_database.py, EXORA.db และ EXORA_assets เพิ่มโมดูล EXORA_payments.py, EXORA_profiles.py และ EXORA_receipts.py

ฐานข้อมูลเดิมเพิ่มเฉพาะคอลัมน์และตารางที่ต้องใช้ รายการเก่าติดป้าย “ประวัติเดิม” ไม่เปลี่ยนยอด อัตรา เลขรายการ หรือวันที่เดิม ก่อนใช้งานสำเนาที่จัดเตรียมไว้มีผู้ใช้เดิม 3 บัญชี สกุลเงิน 10 รายการ และประวัติ 2 รายการ การแก้ฐานข้อมูลเกิดเมื่อเปิด EXORA_main.py

สำรองทั้ง EXORA.db และ EXORA_assets ก่อนเปลี่ยนเวอร์ชัน ปิดโปรแกรมก่อนคัดลอกฐานข้อมูล ไฟล์สำรองเดิมใน EXORA_Backup เป็นสำเนาที่สร้างด้วย SQLite backup API

หากบัญชี admin ยังใช้รหัสเริ่มต้น แนะนำให้เปลี่ยนจากหน้าโปรไฟล์ก่อนใช้งานจริง

## Gmail และ PDF

กำหนดใน environment ก่อน Run VS Code หรือก่อน Run Python ใน terminal โดยไม่ใส่รหัสลับในไฟล์โค้ด:

```powershell
$env:EXORA_GMAIL_USER = 'your-account@gmail.com'
$exoraSecret = Read-Host 'Gmail App Password' -AsSecureString
$env:EXORA_GMAIL_APP_PASSWORD = [System.Net.NetworkCredential]::new('', $exoraSecret).Password
python EXORA_main.py
```

ถ้ากดปุ่ม Run จาก VS Code ให้ตั้ง environment ใน Windows แล้วเปิด VS Code ใหม่เพื่อให้โปรแกรมรับค่าด้วย หรือเปิด VS Code จาก terminal ที่ตั้งค่าไว้ ห้ามส่ง App Password ในแชต

Gmail App Password ต้องเป็นบัญชีที่เปิด 2-Step Verification และอนุญาตให้ใช้งาน บัญชีองค์กรบางบัญชีอาจปิดการใช้ App Password ดู [คู่มือ Google](https://support.google.com/accounts/answer/185833) ใช้ smtp.gmail.com:465 ผ่าน SSL ตาม [เอกสาร Gmail SMTP](https://developers.google.com/workspace/gmail/imap/imap-smtp)

`EXORA_PDF_FONT` กำหนดพาธฟอนต์ TTF ภาษาไทย ค่าเริ่มต้น C:\Windows\Fonts\tahoma.ttf

ไม่มีการส่ง Gmail จริงระหว่างทดสอบ ใช้ SMTP จำลอง

## ทดสอบ

`python test_exora.py` ทดสอบกับฐานข้อมูลชั่วคราว ไม่แก้ฐานข้อมูลใช้งานจริง
