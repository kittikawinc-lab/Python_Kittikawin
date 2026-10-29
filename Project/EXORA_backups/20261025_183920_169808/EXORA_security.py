"""Local application security boundaries; filesystem/OS access remains trusted."""
import hashlib,hmac,secrets,time,json,re
from decimal import Decimal,ROUND_HALF_UP,InvalidOperation

# เก็บรหัสผ่านแบบ PBKDF2 พร้อม salt สุ่ม ไม่เก็บรหัสผ่านจริง
def password_hash(password):
    salt=secrets.token_hex(16);iterations=600000
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),iterations).hex()
    return f'pbkdf2_sha256${iterations}${salt}${digest}'

# ตรวจรหัสผ่านใหม่และรองรับ SHA-256 เดิม เพื่ออัปเกรดหลังล็อกอินสำเร็จ
def password_matches(password,stored):
    try:
        if stored.startswith('pbkdf2_sha256$'):
            _,count,salt,digest=stored.split('$');count=int(count)
            if not 100000<=count<=2000000 or len(salt)!=32 or len(digest)!=64:return False
            actual=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),count).hex()
            expected=digest
        else:actual=hashlib.sha256(password.encode()).hexdigest();expected=stored
        return hmac.compare_digest(actual,expected)
    except (TypeError,ValueError,AttributeError):return False

# สร้างตารางสำหรับใบเสนอราคาที่เชื่อถือได้และการจำกัดล็อกอิน
def migrate(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS secure_quotes(id TEXT PRIMARY KEY,actor_id INTEGER,payload TEXT NOT NULL,expires REAL NOT NULL,used_transaction TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS login_limits(identifier TEXT PRIMARY KEY,failures INTEGER NOT NULL,blocked_until REAL NOT NULL,last_attempt REAL NOT NULL)')

# หลังยืนยันตัวตนและเปลี่ยนรหัสสำเร็จ ให้ปลดตัวนับล็อกอินของบัญชีเดียวกัน
def clear_login_limit(conn,user_id):
    migrate(conn);key=hashlib.sha256(('account:'+str(user_id)).encode()).hexdigest()
    conn.execute('DELETE FROM login_limits WHERE identifier=?',(key,))

# ตรวจยอดต้นทางก่อนปัดเศษ ใช้ร่วมกันทุกทางเข้ารายการ
MAX_TRANSACTION_AMOUNT=Decimal('1000')
def validate_transaction_amount(value):
    text=str(value).strip()
    if len(text)>64 or not re.fullmatch(r'[0-9]+(?:\.[0-9]{1,8})?',text):raise ValueError('กรอกจำนวนเงินเป็นตัวเลขบวกเท่านั้น')
    try:amount=Decimal(text)
    except InvalidOperation:raise ValueError('จำนวนเงินไม่ถูกต้อง') from None
    if not amount.is_finite() or not 0<amount<=MAX_TRANSACTION_AMOUNT:raise ValueError('ยอดต่อรายการต้องมากกว่า 0 และไม่เกิน 1,000 ของสกุลเงินต้นทาง')
    rounded=amount.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    if rounded<=0:raise ValueError('จำนวนเงินน้อยเกินไป')
    return rounded

# คำนวณราคาจาก snapshot ฐานข้อมูลเดียวและเก็บข้อมูลที่ใช้ตรวจตอนส่งรายการ
def issue_quote(conn,source,target,value,actor=None):
    migrate(conn)
    if actor is not None and not conn.execute("SELECT 1 FROM users WHERE id=? AND status='active'",(actor,)).fetchone():raise PermissionError('บัญชีไม่พร้อมใช้งาน')
    amount=validate_transaction_amount(value)
    if source==target:raise ValueError('กรุณาเลือกสกุลเงินต่างกัน')
    rows={r[0]:r for r in conn.execute('SELECT currency_code,buy_rate,sell_rate FROM currencies WHERE currency_code IN (?,?)',(source,target))}
    if source not in rows or target not in rows:raise ValueError('ไม่พบสกุลเงิน')
    buy=Decimal('1') if source=='THB' else Decimal(str(rows[source][1]));sell=Decimal('1') if target=='THB' else Decimal(str(rows[target][2]))
    if not buy.is_finite() or not sell.is_finite() or buy<=0 or sell<=0:raise ValueError('ร้านยังไม่ได้ตั้งอัตราสำหรับสกุลเงินนี้')
    try:amount=amount.quantize(Decimal('.01'),rounding=ROUND_HALF_UP);result=(amount*buy/sell).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    except InvalidOperation:raise ValueError('ยอดเงินหรืออัตราเกินขอบเขตที่ระบบรองรับ')
    if amount<=0 or result<=0:raise ValueError('จำนวนเงินน้อยเกินไป')
    if result>Decimal('1000000000000') or amount*buy>Decimal('1000000000000'):raise ValueError('มูลค่ารายการเกินขอบเขตที่ระบบรองรับ')
    payload={'from_currency':source,'to_currency':target,'from_amount':float(amount),'to_amount':float(result),'exchange_rate':float(buy/sell),'thb_value':float((amount*buy).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)),'transaction_type':'SELL' if source=='THB' else 'BUY'}
    identifier=secrets.token_hex(24);expires=time.time()+1800
    conn.execute('DELETE FROM secure_quotes WHERE used_transaction IS NULL AND expires<?',(time.time()-86400,))
    conn.execute('INSERT INTO secure_quotes VALUES (?,?,?,?,NULL)',(identifier,actor,json.dumps(payload),expires));conn.commit()
    return {**payload,'quote_id':identifier,'quote_expires':expires}

# ตรวจเจ้าของ อายุ และทุกค่าของใบเสนอราคา ก่อนใช้หนึ่งครั้งใน transaction เดียวกัน
def consume_quote(conn,actor,number,data):
    migrate(conn);row=conn.execute('SELECT actor_id,payload,expires,used_transaction FROM secure_quotes WHERE id=?',(data.get('quote_id',''),)).fetchone()
    if not row:raise ValueError('กรุณาคำนวณใบเสนอราคาใหม่ก่อนส่งรายการ')
    owner,payload,expires,used=row
    if owner is not None and owner!=actor:raise PermissionError('ใบเสนอราคาเป็นของบัญชีอื่น')
    if used:raise ValueError('ใบเสนอราคานี้ถูกใช้แล้ว กรุณาสร้างรายการใหม่')
    if expires<time.time():raise ValueError('ใบเสนอราคาหมดอายุ กรุณาคำนวณใหม่')
    canonical=json.loads(payload)
    validate_transaction_amount(canonical.get('from_amount'))
    for key,value in canonical.items():
        given=data.get(key)
        if isinstance(value,(int,float)):
            try:equal=Decimal(str(given))==Decimal(str(value))
            except InvalidOperation:equal=False
        else:equal=given==value
        if not equal:raise ValueError('ยอดหรือข้อมูลใบเสนอราคาถูกเปลี่ยน กรุณาคำนวณใหม่')
    conn.execute('UPDATE secure_quotes SET used_transaction=? WHERE id=? AND used_transaction IS NULL',(number,data['quote_id']))
    return canonical

# กันเลขอ้างอิงโอนเดิมถูกใช้ในรายการอื่น แม้ภาพสลิปถูกเปลี่ยน
def reserve_bank_reference(conn,number,payment):
    if payment.get('payment_method')!='bank' or not payment.get('transfer_reference'):return
    from EXORA_banks import lookup
    def fingerprint(bank,account,reference):
        code=lookup(bank)[0];bank=code if code!='OTHER' else str(bank).strip().casefold()
        value='|'.join((bank,re.sub(r'\D','',account),re.sub(r'\s','',reference).casefold()))
        return hashlib.sha256(value.encode()).hexdigest()
    conn.execute('CREATE TABLE IF NOT EXISTS bank_reference_ledger(fingerprint TEXT PRIMARY KEY,transaction_no TEXT NOT NULL)')
    for old,bank,account,reference in conn.execute("SELECT transaction_no,payer_bank,payer_account,transfer_reference FROM transactions WHERE payment_method='bank' AND COALESCE(transfer_reference,'')<>''").fetchall():
        conn.execute('INSERT OR IGNORE INTO bank_reference_ledger VALUES (?,?)',(fingerprint(bank or '',account or '',reference),old))
    key=fingerprint(payment['payer_bank'],payment['payer_account'],payment['transfer_reference'])
    old=conn.execute('SELECT transaction_no FROM bank_reference_ledger WHERE fingerprint=?',(key,)).fetchone()
    if old and old[0]!=number:raise ValueError('เลขอ้างอิงการโอนนี้ถูกใช้ในรายการอื่นแล้ว')
    conn.execute('INSERT OR IGNORE INTO bank_reference_ledger VALUES (?,?)',(key,number))

# ตรวจเฉพาะรหัสผ่านที่ตั้งใหม่ ไม่ใช้กฎนี้ขณะเข้าสู่ระบบด้วยรหัสเดิม
PASSWORD_RULE='รหัสผ่านต้องมี 8–256 ตัว และมีทั้งตัวอักษรกับตัวเลข'
def validate_new_password(value):
    if not isinstance(value,str) or not 8<=len(value)<=256 or not any(c.isalpha() for c in value) or not any(c.isdecimal() for c in value):
        raise ValueError(PASSWORD_RULE)
