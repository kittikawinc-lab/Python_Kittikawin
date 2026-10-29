"""Isolated online settlement simulation. No bank, identity provider or SMTP calls."""
import json,time,secrets,sqlite3,re
from pathlib import Path
import EXORA_database as db

STATES={'identity_pending':'รอตรวจตัวตนจำลอง','identity_verified':'ผ่านตรวจตัวตนจำลอง','quoted':'รอชำระจำลอง','payment_pending':'รอตรวจรับชำระจำลอง','payment_verified':'รับชำระจำลองแล้ว','payout_processing':'กำลังโอนจ่ายจำลอง','completed':'สำเร็จจำลอง','rejected':'ปฏิเสธจำลอง'}

# แยกทุกตารางจากรายการเงินจริง และเก็บลำดับผู้ดำเนินการไว้ตรวจย้อนหลัง
def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS online_demo_orders(number TEXT PRIMARY KEY,user_id INTEGER NOT NULL,
        recipient TEXT NOT NULL,bank TEXT NOT NULL,account TEXT NOT NULL,country TEXT NOT NULL,
        source TEXT NOT NULL,target TEXT NOT NULL,amount TEXT NOT NULL,status TEXT NOT NULL,
        quote TEXT,payout_reference TEXT,email_status TEXT,created_at REAL NOT NULL)''')
    conn.execute('CREATE TABLE IF NOT EXISTS online_demo_audit(id INTEGER PRIMARY KEY,number TEXT,actor INTEGER,action TEXT,created_at REAL)')

# ตรวจสิทธิ์จากฐานข้อมูลจริง ไม่เชื่อข้อมูล role จากหน้าจอ
def role(conn,actor):
    row=conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()
    if not row:raise PermissionError('บัญชีไม่พร้อมใช้งาน')
    return row[0]

# เจ้าของเห็นรายการตนเอง แอดมินเห็นรายการเพื่อตรวจได้
def get(number,actor):
    conn=db.getconnect()
    try:
        access=role(conn,actor);conn.row_factory=sqlite3.Row
        row=conn.execute('SELECT * FROM online_demo_orders WHERE number=?',(number,)).fetchone()
        if not row:raise ValueError('ไม่พบรายการ')
        row=dict(row)
        if access!='admin' and row['user_id']!=actor:raise PermissionError('เฉพาะเจ้าของรายการ')
        return row
    finally:conn.close()

# อ่านรายการจำลองโดยไม่รวมในยอดขาย สถิติ หรือคิวอีเมลเงินจริง
def listing(actor,own_only=False):
    conn=db.getconnect()
    try:
        access=role(conn,actor);conn.row_factory=sqlite3.Row
        return [dict(row) for row in conn.execute('SELECT * FROM online_demo_orders'+(' WHERE user_id=?' if access!='admin' or own_only else '')+' ORDER BY created_at DESC',(actor,) if access!='admin' or own_only else ())]
    finally:conn.close()

# สร้างรายการด้วยบัญชีตัวอย่างเท่านั้น ไม่เก็บเลขบัตรหรือเอกสารระบุตัวตนจริง
def create(actor,recipient,bank,account,country,source,target,amount):
    values=[str(value).strip() for value in (recipient,bank,account,country,source,target,amount)]
    if any(not value or len(value)>100 for value in values):raise ValueError('กรุณากรอกข้อมูลให้ครบทุกช่อง')
    if not re.fullmatch(r'DEMO-[A-Za-z0-9-]{1,32}',account):raise ValueError('ใช้เลขบัญชีจำลองที่ขึ้นต้น DEMO- เท่านั้น')
    from decimal import Decimal,InvalidOperation
    try:quantity=Decimal(amount)
    except InvalidOperation:raise ValueError('จำนวนเงินไม่ถูกต้อง') from None
    if not quantity.is_finite() or not 0<quantity<=1000000000:raise ValueError('จำนวนเงินไม่ถูกต้อง')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');role(conn,actor)
        codes={row[0] for row in conn.execute('SELECT currency_code FROM currencies')}
        if source not in codes or target not in codes or source==target:raise ValueError('กรุณาเลือกสกุลเงินต่างกัน')
        number='DEMO-'+secrets.token_hex(6).upper()
        conn.execute('INSERT INTO online_demo_orders VALUES (?,?,?,?,?,?,?,?,?,?,NULL,NULL,NULL,?)',(number,actor,*values[:4],source,target,str(quantity),'identity_pending',time.time()))
        conn.execute('INSERT INTO online_demo_audit(number,actor,action,created_at) VALUES (?,?,?,?)',(number,actor,'created',time.time()));conn.commit();return number
    finally:conn.close()

# คำนวณจากราคาที่ร้านบันทึก แต่ไม่สร้างหรือใช้รายการชำระเงินจริง
def quote(number,actor):
    row=get(number,actor)
    if row['user_id']!=actor:raise PermissionError('เฉพาะเจ้าของรายการ')
    if row['status'] not in ('identity_verified','quoted'):raise ValueError('สถานะไม่ถูกต้อง')
    from EXORA_profiles import quote as calculate
    price=calculate(row['source'],row['target'],row['amount'],actor_id=actor)
    update(number,actor,'quote',('identity_verified','quoted'),'quoted',quote=json.dumps(price))
    return price

# เปลี่ยนสถานะแบบ atomic และกันแอดมินตรวจรายการตัวเอง
def update(number,actor,action,allowed,next_state,**fields):
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');access=role(conn,actor)
        conn.row_factory=sqlite3.Row;row=conn.execute('SELECT * FROM online_demo_orders WHERE number=?',(number,)).fetchone()
        if not row:raise ValueError('ไม่พบรายการ')
        if action in ('quote','pay'):
            if row['user_id']!=actor:raise PermissionError('เฉพาะเจ้าของรายการ')
        elif access!='admin' or row['user_id']==actor:raise PermissionError('ให้แอดมินอีกบัญชีตรวจรายการนี้')
        if row['status'] not in allowed:raise ValueError('สถานะไม่ถูกต้อง')
        if action=='pay' and json.loads(row['quote'])['quote_expires']<time.time():raise ValueError('ใบเสนอราคาหมดอายุ กรุณาคำนวณใหม่')
        if any(key not in ('quote','payout_reference','email_status') for key in fields):raise ValueError('สถานะไม่ถูกต้อง')
        assignments=['status=?']+[key+'=?' for key in fields]
        conn.execute('UPDATE online_demo_orders SET '+','.join(assignments)+' WHERE number=?',(next_state,*fields.values(),number))
        conn.execute('INSERT INTO online_demo_audit(number,actor,action,created_at) VALUES (?,?,?,?)',(number,actor,action,time.time()));conn.commit()
    except Exception:conn.rollback();raise
    finally:conn.close()

# คำสั่งชัดเจนตามลำดับ ไม่มีการเรียก API ธนาคารหรือส่งอีเมลจริง
def act(number,actor,action):
    transitions={'verify_identity':(('identity_pending',),'identity_verified'),
        'pay':(('quoted',),'payment_pending'),'verify_payment':(('payment_pending',),'payment_verified'),
        'start_payout':(('payment_verified',),'payout_processing'),'complete':(('payout_processing',),'completed'),
        'reject':(('identity_pending','payment_pending'),'rejected')}
    if action not in transitions:raise ValueError('สถานะไม่ถูกต้อง')
    allowed,next_state=transitions[action];fields={}
    if action=='complete':fields={'payout_reference':'DEMO-TRANSFER-'+secrets.token_hex(6).upper(),'email_status':'simulated_only'}
    update(number,actor,action,allowed,next_state,**fields)

# สร้างใบเสร็จตัวอย่างเฉพาะรายการจบแล้วและติดป้ายจำลองทุกหน้า
def receipt(number,actor,destination):
    row=get(number,actor)
    if row['status']!='completed':raise ValueError('รายการยังไม่สำเร็จจำลอง')
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    price=json.loads(row['quote']);path=Path(destination)
    document=canvas.Canvas(str(path),pagesize=A4);width,height=A4
    document.setFillColorRGB(.07,.36,.29);document.rect(0,height-130,width,130,fill=1,stroke=0)
    document.setFillColorRGB(1,1,1);document.setFont('Helvetica-Bold',28);document.drawString(45,height-55,'EXORA / SIMULATION')
    document.setFont('Helvetica',12);document.drawString(45,height-83,'DEMO RECEIPT - NO REAL PAYMENT OR TRANSFER')
    document.setFillColorRGB(.09,.23,.19);document.setFont('Helvetica',12)
    rows=[('Order',number),('Account',row['account']),('From',f"{price['from_amount']:,.2f} {row['source']}"),('To (simulated)',f"{price['to_amount']:,.2f} {row['target']}"),('Demo fee','0.00 - actual bank fees are not represented'),('Reference',row['payout_reference']),('Email delivery','SIMULATED ONLY - no email sent')]
    for index,(label,value) in enumerate(rows):document.drawString(45,height-175-index*35,label+': '+value)
    document.setFont('Helvetica-Bold',10);document.drawString(45,55,'TRAINING ONLY. NOT A BANK CONFIRMATION OR A REAL RECEIPT.');document.save();return path
