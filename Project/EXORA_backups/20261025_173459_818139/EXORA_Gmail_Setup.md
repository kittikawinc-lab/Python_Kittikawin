# ตั้งค่าผู้ส่ง exoraadmin@gmail.com

โปรแกรมสร้างใบเสร็จธีม EXORA เมื่ออนุมัติรายการ และเมื่อกดส่งใบเสร็จจะส่ง PDF ไปยังอีเมลเจ้าของรายการจากโปรไฟล์ ใช้ผู้ส่ง exoraadmin@gmail.com ทั้ง OTP และใบเสร็จ ไม่ต้องกรอกอีเมลผู้รับเอง

## ฝั่ง Gmail

1. เข้าบัญชี Google ของ **exoraadmin@gmail.com** ด้วยตนเอง ตรวจสอบว่ามีสิทธิ์ใช้งานบัญชีนี้
2. เปิด **2-Step Verification** ที่ [ความปลอดภัยบัญชี Google](https://myaccount.google.com/security)
3. เปิด [App passwords](https://myaccount.google.com/apppasswords) ตั้งชื่อ `EXORA Desktop` แล้วสร้างรหัสสำหรับแอพ ใช้รหัสนี้แทนรหัสผ่าน Gmail ปกติ ไม่ต้องส่งรหัสในแชต
4. ใน Windows ค้นหา `Edit environment variables for your account` แล้วเพิ่ม **User variable**:
   - ชื่อ: `EXORA_GMAIL_APP_PASSWORD`
   - ค่า: App Password ของ exoraadmin@gmail.com (ลบช่องว่างได้)
5. ปิด VS Code ทุกหน้าต่างแล้วเปิดใหม่ เพื่อให้รับค่า environment จากนั้น Run EXORA_main.py เหมือนเดิม

รายละเอียดและข้อจำกัดจาก [Google](https://support.google.com/accounts/answer/185833): App Password ต้องเปิดการยืนยันสองขั้นตอนก่อน หากไม่พบเมนู อาจเป็นบัญชีองค์กรที่ไม่อนุญาต บัญชีที่ใช้เฉพาะ security keys หรือบัญชี Advanced Protection อย่าปิดการป้องกันเหล่านี้เพื่อให้โปรแกรมทำงาน ให้ใช้การเชื่อมต่อ OAuth แทนหากบัญชีไม่รองรับ App Password

โปรแกรมใช้ smtp.gmail.com พอร์ต 465 ผ่าน SSL และล็อกอินเป็น exoraadmin@gmail.com ตาม [เอกสาร Gmail SMTP](https://developers.google.com/workspace/gmail/imap/imap-smtp) ไม่ต้องเพิ่มการตั้งค่า SMTP ใน Gmail

## ฝั่ง EXORA

- ผู้ทำรายการต้องบันทึกอีเมลที่ถูกต้องในหน้าโปรไฟล์
- admin อนุมัติ → สร้าง PDF อัตโนมัติ → เปิดรายละเอียด → กดส่งใบเสร็จ
- อีเมลส่งจาก exoraadmin@gmail.com มีเนื้อหาในธีม EXORA และแนบ PDF
- ถ้าไม่มี App Password โปรแกรมยังสร้างและบันทึก PDF ได้ แต่ส่งอีเมลไม่ได้
- ถ้าส่งผิดพลาด สถานะอนุมัติคงเดิม แก้การตั้งค่าแล้วลองส่งอีกครั้งได้ มีการป้องกันส่งซ้ำไปยังผู้ทำรายการ
- หากเปลี่ยนรหัสผ่าน Google ต้องสร้าง App Password ใหม่ เพราะ Google จะเพิกถอนรหัสแอพเดิม

ถ้าต้องการเปลี่ยนผู้ส่งภายหลัง แก้ค่า `SENDER` ใน EXORA_email_settings.py และตั้ง App Password ของบัญชีผู้ส่งใหม่ให้ตรงกัน ใช้เพียงการเปลี่ยนข้อความ From จะไม่ทำให้ส่งในนามบัญชีอื่นได้

อัปเดตนี้ทดสอบด้วย SMTP จำลอง ไม่ได้เข้า Gmail หรือส่งอีเมลจริงให้ลูกค้า
