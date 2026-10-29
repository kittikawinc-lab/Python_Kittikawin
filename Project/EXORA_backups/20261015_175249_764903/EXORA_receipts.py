"""PDF receipts and opt-in Gmail delivery with environment-only credentials."""
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า os: os — อ่าน environment variables และทำงานร่วมกับระบบปฏิบัติการ
import os
# คำอธิบาย import: นำเข้า re: re — ตรวจรูปแบบข้อความด้วย regular expressions
import re
# คำอธิบาย import: นำเข้า ssl: ssl — สร้างบริบท TLS สำหรับการเชื่อมต่ออีเมล
import ssl
# คำอธิบาย import: นำเข้า smtplib: smtplib — เชื่อมต่อ SMTP เพื่อส่งอีเมล
import smtplib
# คำอธิบาย import: นำเข้า datetime: datetime — จัดการวันที่ เวลา และเขตเวลา
# datetime: วันและเวลาของรายการและเอกสาร
from datetime import datetime
# คำอธิบาย import: นำเข้า EmailMessage: email.message — สร้างอีเมล ข้อความ HTML และไฟล์แนบด้วย EmailMessage
# EmailMessage: วัตถุสร้างเนื้อหา ผู้รับ และไฟล์แนบของอีเมล
from email.message import EmailMessage
# คำอธิบาย import: นำเข้า escape: xml.sax.saxutils — escape ข้อความก่อนแทรกลงในเนื้อหา PDF/HTML
# escape: แทนตัวอักษรพิเศษก่อนใส่ข้อความใน markup
from xml.sax.saxutils import escape
# คำอธิบาย import: นำเข้า EXORA_payments as payments: EXORA_payments — รับหลักฐาน ตรวจสิทธิ์ และจัดการสถานะรายการชำระเงิน
import EXORA_payments as payments
# คำอธิบาย import: นำเข้า EXORA_database as db: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
import EXORA_database as db
# คำอธิบาย import: นำเข้า EXORA_email_settings as email_settings: EXORA_email_settings — อ่าน Gmail App Password จาก environment variables และกำหนดผู้ส่ง
import EXORA_email_settings as email_settings
# คำอธิบาย import: นำเข้า tempfile: tempfile — สร้างไฟล์หรือโฟลเดอร์ชั่วคราว
import tempfile
# คำอธิบาย import: นำเข้า hashlib: hashlib — คำนวณค่าแฮชสำหรับรหัสผ่าน OTP และลายนิ้วมือไฟล์ตามจุดใช้งาน
import hashlib
# คำอธิบาย import: นำเข้า threading: threading — ป้องกันงานสร้างใบเสร็จชนกันด้วยล็อก
import threading
PDF_LOCK=threading.RLock()

# คำอธิบาย def export_pdf: จัดเตรียมและบันทึก PDF รายการไปยังตำแหน่งที่ระบุ
# รับค่า: number, actor_id, destination | เรียกใช้: payments.get_transaction
def export_pdf(number, actor_id, destination):
    # คำอธิบาย import: นำเข้า colors: reportlab.lib — จัดหน้า สร้าง PDF และลงทะเบียนฟอนต์ใบเสร็จ
    # colors: ชุดสีสำหรับ PDF
    from reportlab.lib import colors
    # คำอธิบาย import: นำเข้า A4: reportlab.lib.pagesizes — จัดหน้า สร้าง PDF และลงทะเบียนฟอนต์ใบเสร็จ
    # A4: ขนาดกระดาษ A4
    from reportlab.lib.pagesizes import A4
    # คำอธิบาย import: นำเข้า getSampleStyleSheet, ParagraphStyle: reportlab.lib.styles — จัดหน้า สร้าง PDF และลงทะเบียนฟอนต์ใบเสร็จ
    # getSampleStyleSheet: อ่านชุดรูปแบบข้อความเริ่มต้น
    # ParagraphStyle: กำหนดรูปแบบข้อความใน PDF
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    # คำอธิบาย import: นำเข้า SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle: reportlab.platypus — จัดหน้า สร้าง PDF และลงทะเบียนฟอนต์ใบเสร็จ
    # SimpleDocTemplate: กำหนดเอกสาร PDF และพื้นที่หน้า
    # Paragraph: ข้อความที่จัดบรรทัดและรูปแบบได้
    # Spacer: เว้นระยะในเอกสาร
    # Table: จัดข้อมูลเป็นตาราง
    # TableStyle: กำหนดสี เส้น และระยะในตาราง
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    # คำอธิบาย import: นำเข้า pdfmetrics: reportlab.pdfbase — จัดหน้า สร้าง PDF และลงทะเบียนฟอนต์ใบเสร็จ
    # pdfmetrics: ลงทะเบียนและวัดฟอนต์ PDF
    from reportlab.pdfbase import pdfmetrics
    # คำอธิบาย import: นำเข้า TTFont: reportlab.pdfbase.ttfonts — จัดหน้า สร้าง PDF และลงทะเบียนฟอนต์ใบเสร็จ
    # TTFont: โหลดฟอนต์ TrueType เพื่อรองรับข้อความใบเสร็จ
    from reportlab.pdfbase.ttfonts import TTFont
    row = payments.get_transaction(number, actor_id)
    # คำอธิบาย import: นำเข้า shop: EXORA_profiles — จัดการโปรไฟล์ ร้าน ผู้ใช้ และการคำนวณยอดแลกเงิน
    from EXORA_profiles import shop
    store=shop()
    font_path = os.getenv('EXORA_PDF_FONT', r'C:\Windows\Fonts\tahoma.ttf')
    if not Path(font_path).is_file():
        raise ValueError('กรุณาตั้ง EXORA_PDF_FONT เป็นพาธฟอนต์ TTF ที่รองรับภาษาไทย')
    with PDF_LOCK:
        if 'EXORAThai' not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont('EXORAThai', font_path))
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = 'EXORAThai'
        style.fontSize=10;style.leading = 15
    # คำอธิบาย def export_pdf.p: สร้างข้อความ Paragraph ที่ escape แล้วสำหรับเอกสาร PDF
    # รับค่า: value
    def p(value):
        return Paragraph(escape(str(value or '-')), styles['Normal'])
    title = 'ใบเสร็จแลกเปลี่ยนเงิน / EXCHANGE RECEIPT' if row['payment_status'] == 'approved' else 'สรุปรายการ / TRANSACTION SUMMARY'
    styles.add(ParagraphStyle('ReceiptTitle',fontName='EXORAThai',fontSize=18,leading=26,textColor=colors.HexColor('#125b4a')))
    styles.add(ParagraphStyle('ReceiptNote',fontName='EXORAThai',fontSize=9,leading=14,textColor=colors.HexColor('#617c66')))
    story = [Paragraph(title, styles['ReceiptTitle']),Spacer(1,8),
             p('เลขที่รายการ '+number),p('ร้าน '+store['name']),Spacer(1,14)]
    fields = [('Transaction', number), ('Status', row['payment_status']),
              ('Customer', row['customer_name']), ('Phone', row['customer_phone']),
              ('Date', row['transaction_date']), ('Type', row['transaction_type']),
              ('From', f"{row['from_amount']:,.2f} {row['from_currency']}"),
              ('To', f"{row['to_amount']:,.2f} {row['to_currency']}"),
              ('Rate', f"{row['exchange_rate']:.6f}"),
              ('Reviewed at', row['reviewed_at']), ('Review note', row['review_note'])]
    fields.insert(2,('Payment method',{'qr':'PromptPay QR','bank':'Bank transfer','in_store':'Foreign currency handed over at store','card':'Credit/debit card','legacy':'Historical record'}.get(row.get('payment_method'),'Historical record')))
    if row.get('payment_method')=='bank':
        account=row.get('payer_account') or ''
        fields.extend([('Payer',f"{row['payer_bank']} / {row['payer_name']}"),
                       ('Payer account','****'+account[-4:]),
                       ('Paid amount',f"{row['transfer_amount']:,.2f} THB"),
                       ('Transfer date',row['transfer_at']),('Reference',row['transfer_reference']),
                       ('Recipient',f"{row['recipient_bank']} / {row['recipient_name']} / {row['recipient_account']}")])
    table = Table([[p(k), p(v)] for k,v in fields], colWidths=[120, 365])
    table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#eaf1e1')),
        ('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#d7e1ce')),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(table)
    story.extend([Spacer(1,16),Paragraph('ขอบคุณที่ให้ EXORA เป็นส่วนหนึ่งของการเดินทางของคุณ',styles['ReceiptNote']),
                  Paragraph('การอนุมัติเป็นการตรวจสอบหลักฐานโดยเจ้าหน้าที่ เอกสารนี้ไม่ใช่ใบกำกับภาษี',styles['ReceiptNote'])])
    path = Path(destination)
    # คำอธิบาย def export_pdf.decorate: วาดส่วนหัวและท้ายหน้าของใบเสร็จ PDF
    # รับค่า: canvas, document
    def decorate(canvas,document):
        width,height=A4;canvas.saveState()
        canvas.setFillColor(colors.HexColor('#f6f7f1'));canvas.rect(0,0,width,height,fill=1,stroke=0)
        canvas.setFillColor(colors.HexColor('#125b4a'));canvas.rect(0,height-105,width,105,fill=1,stroke=0)
        # คำอธิบาย import: นำเข้า SHAPES: EXORA_brand — วาดโลโก้และองค์ประกอบแบรนด์ EXORA
        from EXORA_brand import SHAPES
        canvas.saveState();canvas.translate(46,height-82);canvas.scale(.44,.44)
        canvas.setStrokeColor(colors.HexColor('#71a18a'));canvas.circle(64,64,58,stroke=1,fill=0)
        for fill,points in SHAPES:
            canvas.setFillColor(colors.HexColor(fill));shape=canvas.beginPath();shape.moveTo(points[0][0],128-points[0][1])
            for x,y in points[1:]:shape.lineTo(x,128-y)
            shape.close();canvas.drawPath(shape,fill=1,stroke=0)
        canvas.restoreState();canvas.setFillColor(colors.white);canvas.setFont('EXORAThai',27);canvas.drawString(115,height-51,'EXORA')
        canvas.setFont('EXORAThai',8);canvas.setFillColor(colors.HexColor('#d8ef9a'));canvas.drawString(117,height-73,'EXCHANGE FOR YOUR NEXT JOURNEY')
        canvas.setStrokeColor(colors.HexColor('#9fbd82'));canvas.setDash(3,4);canvas.line(365,height-61,548,height-61);canvas.setDash()
        for x in (365,453,548):canvas.circle(x,height-61,3,stroke=1,fill=0)
        canvas.setFillColor(colors.HexColor('#617c66'));canvas.setFont('EXORAThai',8)
        canvas.drawString(55,34,email_settings.SENDER);canvas.drawRightString(width-55,34,'EXORA / '+str(document.page))
        canvas.restoreState()
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=55, leftMargin=55,topMargin=125,bottomMargin=60).build(story,onFirstPage=decorate,onLaterPages=decorate)
    return path

# คำอธิบาย def ensure_receipt: สร้างหรือใช้ PDF ใบเสร็จที่บันทึกไว้ พร้อมตรวจข้อมูลเอกสาร
# รับค่า: number, actor_id | เรียกใช้: payments.get_transaction, db.getconnect
def ensure_receipt(number,actor_id):
    """Create and archive the approved receipt once, independently of email."""
    row=payments.get_transaction(number,actor_id)
    if row['payment_status']!='approved':raise ValueError('สร้างใบเสร็จได้เมื่ออนุมัติรายการแล้ว')
    with PDF_LOCK:
        conn=db.getconnect()
        try:
            conn.execute('CREATE TABLE IF NOT EXISTS receipt_documents(transaction_no TEXT PRIMARY KEY,path TEXT,sha256 TEXT,created_at TEXT)')
            saved=conn.execute('SELECT path,sha256 FROM receipt_documents WHERE transaction_no=?',(number,)).fetchone()
            base=Path(db.BASE_DIR).resolve();directory=base/'EXORA_assets'/'receipts';directory.mkdir(parents=True,exist_ok=True)
            if saved:
                path=(base/saved[0]).resolve()
                if path.is_relative_to(directory) and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==saved[1]:return path
            path=directory/(hashlib.sha256(number.encode()).hexdigest()[:24]+'.pdf')
            export_pdf(number,actor_id,path)
            conn.execute('INSERT OR REPLACE INTO receipt_documents VALUES (?,?,?,?)',(number,str(path.relative_to(base)),hashlib.sha256(path.read_bytes()).hexdigest(),datetime.now().isoformat(timespec='seconds')));conn.commit()
            return path
        finally:conn.close()

# คำอธิบาย def send_gmail: ส่งใบเสร็จ PDF ผ่าน Gmail SMTP และบันทึกผลการส่ง
# รับค่า: number, actor_id, recipient, pdf_path | เรียกใช้: payments.get_transaction, db.getconnect
def send_gmail(number, actor_id, recipient, pdf_path):
    row = payments.get_transaction(number, actor_id)
    if row['payment_status'] != 'approved':
        raise ValueError('ส่งใบเสร็จได้เฉพาะรายการที่อนุมัติแล้ว')
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', recipient):
        raise ValueError('Email ไม่ถูกต้อง')
    sender = email_settings.SENDER
    password = email_settings.password()
    if not sender or not password:
        raise ValueError('ตั้ง EXORA_GMAIL_APP_PASSWORD ของ '+sender+' ก่อนส่งใบเสร็จ')
    msg = EmailMessage()
    msg['From'], msg['To'], msg['Subject'] = sender, recipient, f'EXORA receipt {number}'
    msg.set_content(f'ใบเสร็จรายการ {number}\nสถานะ: approved\nโปรดดู PDF ที่แนบมา')
    msg.add_alternative(f'''<html><body style="margin:0;background:#f6f7f1;font-family:Tahoma,Arial,sans-serif;color:#173e33">
      <div style="max-width:580px;margin:24px auto;background:white;border:1px solid #dfe5d9">
      <div style="background:#125b4a;color:white;padding:28px"><h1 style="margin:0">EXORA ↗</h1>
      <p style="color:#d8ef9a">EXCHANGE FOR YOUR NEXT JOURNEY</p></div>
      <div style="padding:28px"><h2>ใบเสร็จแลกเปลี่ยนเงิน</h2><p>เรียน {escape(str(row['customer_name'] or 'ผู้ใช้ EXORA'))}</p>
      <p>เลขที่รายการ: <strong>{escape(number)}</strong></p>
      <div style="background:#eaf1e1;padding:20px">{row['from_amount']:,.2f} {escape(row['from_currency'])} →
      <strong>{row['to_amount']:,.2f} {escape(row['to_currency'])}</strong></div>
      <p>รายการได้รับการอนุมัติแล้ว ใบเสร็จ PDF แนบมากับอีเมลนี้</p>
      <p>ขอบคุณที่ให้ EXORA เป็นส่วนหนึ่งของการเดินทางของคุณ</p></div>
      <div style="padding:18px 28px;color:#617c66">{sender}</div></div></body></html>''',subtype='html')
    msg.add_attachment(Path(pdf_path).read_bytes(), maintype='application', subtype='pdf', filename=f'{number}.pdf')
    status='failed'
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context(), timeout=20) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        status='sent'
    finally:
        conn=db.getconnect()
        try:
            conn.execute('INSERT INTO email_log(transaction_no,actor_id,recipient,status,created_at) VALUES (?,?,?,?,?)',
                (number,actor_id,recipient,status,datetime.now().isoformat(timespec='seconds')))
            conn.commit()
        finally: conn.close()

# คำอธิบาย def send_to_user: หาอีเมลเจ้าของรายการและส่งใบเสร็จ โดยป้องกันการส่งซ้ำ
# รับค่า: number, actor_id | เรียกใช้: payments.get_transaction, db.getconnect
def send_to_user(number, actor_id):
    """Automatic approval receipt: recipient is the transaction owner's email."""
    row=payments.get_transaction(number,actor_id)
    if row['payment_status']!='approved':raise ValueError('ยังไม่ได้อนุมัติรายการ')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        conn.execute('''CREATE TABLE IF NOT EXISTS receipt_delivery(
            transaction_no TEXT PRIMARY KEY,recipient TEXT,status TEXT,error TEXT,updated_at TEXT)''')
        previous=conn.execute('SELECT status FROM receipt_delivery WHERE transaction_no=?',(number,)).fetchone()
        if previous and previous[0] in {'sent','sending'}:
            return {'status':previous[0],'message':'ส่งใบเสร็จแล้วหรือกำลังส่ง ไม่ส่งซ้ำ'}
        owner=conn.execute('SELECT email FROM users WHERE id=?',(row['user_id'],)).fetchone()
        recipient=(owner[0] or '').strip() if owner else ''
        conn.execute('INSERT OR REPLACE INTO receipt_delivery VALUES (?,?,?,NULL,?)',(number,recipient,'sending',datetime.now().isoformat(timespec='seconds')))
        conn.commit()
    finally:conn.close()
    try:
        # เก็บ PDF ของรายการอนุมัติไว้ แม้บัญชียังไม่มีอีเมลหรือ Gmail ยังไม่พร้อม
        pdf=ensure_receipt(number,actor_id)
        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',recipient):
            raise ValueError('ผู้ใช้ยังไม่มีอีเมลที่ถูกต้องในโปรไฟล์ กรุณาเพิ่มอีเมลแล้วส่งอีกครั้ง')
        send_gmail(number,actor_id,recipient,pdf)
        status,error='sent',None
    except Exception as failure:
        status,error='failed',str(failure)
    conn=db.getconnect()
    try:
        conn.execute('UPDATE receipt_delivery SET status=?,error=?,updated_at=? WHERE transaction_no=?',
            (status,error,datetime.now().isoformat(timespec='seconds'),number));conn.commit()
    finally:conn.close()
    return {'status':status,'recipient':recipient,'message':error or ('ส่งใบเสร็จพร้อม PDF ไปยัง '+recipient)}

# คำอธิบาย def delivery_status: อ่านสถานะการส่งใบเสร็จของรายการที่มีสิทธิ์ดู
# รับค่า: number, actor_id | เรียกใช้: payments.get_transaction, db.getconnect
def delivery_status(number,actor_id):
    payments.get_transaction(number,actor_id)
    conn=db.getconnect()
    try:
        exists=conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='receipt_delivery'").fetchone()
        if not exists:return None
        row=conn.execute('SELECT recipient,status,error FROM receipt_delivery WHERE transaction_no=?',(number,)).fetchone()
        return {'recipient':row[0],'status':row[1],'error':row[2]} if row else None
    finally:conn.close()
