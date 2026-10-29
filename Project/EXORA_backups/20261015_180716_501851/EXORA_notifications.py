"""คิวแจ้งแอดมินแบบถาวร บันทึกพร้อมรายการ และส่ง SMTP นอก transaction."""
import time
import ssl
import smtplib
from email.message import EmailMessage
import EXORA_database as db
import EXORA_email_settings as settings

# สร้างคิวโดยไม่ส่งอีเมลย้อนหลังสำหรับประวัติเดิม
def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS admin_alerts(event_id INTEGER PRIMARY KEY,transaction_no TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',attempts INTEGER NOT NULL DEFAULT 0,next_try REAL NOT NULL DEFAULT 0,error TEXT)''')

# ลงคิวภายใน transaction ของการส่งรายการ/ส่งสลิปใหม่ จึง rollback พร้อมกัน
def enqueue(conn,event_id,number):
    conn.execute('INSERT OR IGNORE INTO admin_alerts(event_id,transaction_no) VALUES (?,?)',(event_id,number))

# จำนวนรอตรวจจากฐานข้อมูลจริง ตรวจสิทธิ์ทุกครั้งและจำกัดข้อมูลของผู้ใช้ทั่วไป
def pending(actor,own_only=False):
    conn=db.getconnect()
    try:
        role=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()
        if not role:raise PermissionError('บัญชีไม่พร้อมใช้งาน')
        where="payment_status='pending'";params=[]
        if role[0]!='admin' or own_only:where+=' AND user_id=?';params=[actor]
        return conn.execute('SELECT COUNT(*) FROM transactions WHERE '+where,params).fetchone()[0]
    finally:conn.close()

# อ่านสถานะคิวให้ admin เท่านั้น เพื่อทราบหาก Gmail ยังไม่ได้ตั้งค่าหรือส่งล้มเหลว
def failures(actor):
    conn=db.getconnect()
    try:
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()!=('admin',):raise PermissionError('เฉพาะ admin')
        return conn.execute("SELECT COUNT(*) FROM admin_alerts WHERE status='failed'").fetchone()[0]
    finally:conn.close()

# ให้ admin ขอส่งซ้ำเฉพาะอีเมลที่ล้มเหลว ไม่แตะสถานะ sent/sending
def retry(actor):
    conn=db.getconnect()
    try:
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()!=('admin',):raise PermissionError('เฉพาะ admin')
        conn.execute("UPDATE admin_alerts SET status='pending',attempts=0,next_try=0 WHERE status='failed'");conn.commit()
    finally:conn.close()

# ส่งสรุปเท่านั้น ไม่แนบภาพสลิปหรือข้อมูลบัญชีเต็ม เปิดตรวจในโปรแกรม
def send(row):
    password=settings.password()
    if not password:raise ValueError('Gmail App Password not configured')
    msg=EmailMessage();msg['From']=settings.SENDER;msg['To']=settings.SENDER
    msg['Subject']='EXORA | Pending review '+row['transaction_no']
    msg['Message-ID']=f"<exora-alert-{row['event_id']}@exora.local>"
    msg.set_content(f"EXORA: มีรายการรอตรวจสอบ / Transaction awaiting review\n\nTransaction: {row['transaction_no']}\nCustomer: {row['customer_name']}\nAmount: {row['from_amount']:,.2f} {row['from_currency']} → {row['to_amount']:,.2f} {row['to_currency']}\nEvent: {row['action']}\n\nเปิด EXORA > ตรวจสอบรายการ เพื่อตรวจสลิปและอนุมัติ\nOpen EXORA > Review transactions. Verify actual payment before approval.\nThis email does not approve the transaction.")
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=ssl.create_default_context(),timeout=20) as smtp:
        smtp.login(settings.SENDER,password);smtp.send_message(msg)

# ผู้ส่งหนึ่งงานต่อรอบ ใช้การจองคิวใน SQLite ป้องกันหลายหน้าต่างส่งชนกัน
def process_one():
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        # งานที่ไม่ต้องตรวจแล้วไม่จำเป็นต้องส่งแจ้งอนุมัติอีก
        conn.execute("UPDATE admin_alerts SET status='obsolete' WHERE status IN ('pending','failed') AND transaction_no IN (SELECT transaction_no FROM transactions WHERE payment_status!='pending')")
        conn.row_factory=__import__('sqlite3').Row
        row=conn.execute("""SELECT a.*,t.customer_name,t.from_amount,t.from_currency,t.to_amount,t.to_currency,p.action
            FROM admin_alerts a JOIN transactions t ON t.transaction_no=a.transaction_no JOIN payment_audit p ON p.id=a.event_id
            WHERE a.status IN ('pending','failed') AND a.attempts<5 AND a.next_try<=? ORDER BY a.event_id LIMIT 1""",(time.time(),)).fetchone()
        if not row:conn.commit();return
        row=dict(row)
        conn.execute("UPDATE admin_alerts SET status='sending',attempts=attempts+1,error=NULL WHERE event_id=?",(row['event_id'],));conn.commit()
    finally:conn.close()
    try:send(row);status,error='sent',None
    except Exception:
        # ไม่แสดง SMTP credentials หรือรายละเอียดระบบจาก exception ในหน้าผู้ใช้
        status,error='failed','Gmail notification failed; check connection and App Password'
    conn=db.getconnect()
    try:
        conn.execute('UPDATE admin_alerts SET status=?,error=?,next_try=? WHERE event_id=?',(status,error,time.time()+300,row['event_id']));conn.commit()
    finally:conn.close()
