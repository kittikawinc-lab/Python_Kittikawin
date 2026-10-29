"""PDF receipts and opt-in Gmail delivery with environment-only credentials."""
from pathlib import Path
import os
import re
import ssl
import smtplib
from datetime import datetime
from email.message import EmailMessage
from xml.sax.saxutils import escape
import EXORA_payments as payments
import EXORA_database as db

def export_pdf(number, actor_id, destination):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    row = payments.get_transaction(number, actor_id)
    font_path = os.getenv('EXORA_PDF_FONT', r'C:\Windows\Fonts\tahoma.ttf')
    if not Path(font_path).is_file():
        raise ValueError('กรุณาตั้ง EXORA_PDF_FONT เป็นพาธฟอนต์ TTF ที่รองรับภาษาไทย')
    pdfmetrics.registerFont(TTFont('EXORAThai', font_path))
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = 'EXORAThai'
        style.leading = 18
    def p(value):
        return Paragraph(escape(str(value or '-')), styles['Normal'])
    title = 'EXORA - Exchange Receipt' if row['payment_status'] == 'approved' else 'EXORA - Transaction Summary'
    story = [Paragraph(title, styles['Title']), Spacer(1, 22),
             p('QR placeholder / manual slip review. No bank payment verification.'), Spacer(1, 18)]
    fields = [('Transaction', number), ('Status', row['payment_status']),
              ('Customer', row['customer_name']), ('Phone', row['customer_phone']),
              ('Date', row['transaction_date']), ('Type', row['transaction_type']),
              ('From', f"{row['from_amount']:,.2f} {row['from_currency']}"),
              ('To', f"{row['to_amount']:,.2f} {row['to_currency']}"),
              ('Rate', f"{row['exchange_rate']:.6f}"),
              ('Reviewed at', row['reviewed_at']), ('Review note', row['review_note'])]
    table = Table([[p(k), p(v)] for k,v in fields], colWidths=[120, 365])
    table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#e7eef8')),
        ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#cbd5e1')),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    story.append(table)
    path = Path(destination)
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=55, leftMargin=55).build(story)
    return path

def send_gmail(number, actor_id, recipient, pdf_path):
    row = payments.get_transaction(number, actor_id)
    if row['payment_status'] != 'approved':
        raise ValueError('ส่งใบเสร็จได้เฉพาะรายการที่อนุมัติแล้ว')
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', recipient):
        raise ValueError('Email ไม่ถูกต้อง')
    sender = os.getenv('EXORA_GMAIL_USER', '').strip()
    password = os.getenv('EXORA_GMAIL_APP_PASSWORD', '').replace(' ', '')
    if not sender or not password:
        raise ValueError('กรุณาตั้ง EXORA_GMAIL_USER และ EXORA_GMAIL_APP_PASSWORD ก่อนส่ง')
    msg = EmailMessage()
    msg['From'], msg['To'], msg['Subject'] = sender, recipient, f'EXORA receipt {number}'
    msg.set_content(f'ใบเสร็จรายการ {number}\nสถานะ: approved\nโปรดดู PDF ที่แนบมา')
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
