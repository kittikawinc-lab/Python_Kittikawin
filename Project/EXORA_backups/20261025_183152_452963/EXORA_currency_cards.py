"""ข้อมูลการ์ดค่าเงิน: รายการโปรดแยกตามบัญชี."""
# sqlite ใช้ผ่านโมดูลฐานข้อมูล ส่วน Decimal ใช้เปรียบเทียบราคาโดยไม่ปัดยอดก่อนคำนวณ
import EXORA_database as db

# เตรียมรายการโปรดโดยไม่แก้ประวัติธุรกรรม
def migrate(conn):
    # เลิกเก็บฐานเปรียบเทียบใหม่ แต่คงข้อมูลเก่าไว้เพื่อไม่ลบข้อมูลผู้ใช้
    conn.execute('DROP TRIGGER IF EXISTS track_currency_change')
    conn.execute('CREATE TABLE IF NOT EXISTS currency_favorites(user_id INTEGER NOT NULL,code TEXT NOT NULL,PRIMARY KEY(user_id,code))')

# ตรวจบัญชีจริงก่อนอ่านหรือแก้รายการโปรด
def active(conn,actor):
    if not conn.execute("SELECT 1 FROM users WHERE id=? AND status='active'",(actor,)).fetchone():raise PermissionError('บัญชีไม่พร้อมใช้งาน')

# อ่านราคาและสถานะดาวจากฐานข้อมูลชุดเดียว
def listing(actor):
    conn=db.getconnect()
    try:
        active(conn,actor)
        rows=conn.execute('''SELECT c.currency_code,c.currency_name,c.buy_rate,c.sell_rate,
            EXISTS(SELECT 1 FROM currency_favorites f WHERE f.user_id=? AND f.code=c.currency_code)
            FROM currencies c WHERE c.currency_code!='THB' ORDER BY c.currency_code''',(actor,)).fetchall()
        return [dict(zip(('code','name','buy','sell','favorite'),row)) for row in rows]
    finally:conn.close()

# เพิ่มหรือลบดาวแบบตั้งค่าสถานะชัดเจน ไม่มีผลกับบัญชีอื่น
def favorite(actor,code,enabled):
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');active(conn,actor)
        if not conn.execute("SELECT 1 FROM currencies WHERE currency_code=? AND currency_code!='THB'",(code,)).fetchone():raise ValueError('ไม่พบสกุลเงิน')
        if enabled:conn.execute('INSERT OR IGNORE INTO currency_favorites VALUES(?,?)',(actor,code))
        else:conn.execute('DELETE FROM currency_favorites WHERE user_id=? AND code=?',(actor,code))
        conn.commit()
    finally:conn.close()

