"""ข้อมูลการ์ดค่าเงิน: ราคาเดิมและรายการโปรดแยกตามบัญชี."""
# sqlite ใช้ผ่านโมดูลฐานข้อมูล ส่วน Decimal ใช้เปรียบเทียบราคาโดยไม่ปัดยอดก่อนคำนวณ
from decimal import Decimal
import EXORA_database as db

# เตรียมราคาอ้างอิงก่อนเปลี่ยนครั้งล่าสุดและรายการโปรด ไม่แก้ประวัติธุรกรรม
def migrate(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS currency_changes(code TEXT PRIMARY KEY,previous_buy REAL,previous_sell REAL,changed_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS currency_favorites(user_id INTEGER NOT NULL,code TEXT NOT NULL,PRIMARY KEY(user_id,code))')
    conn.execute('''CREATE TRIGGER IF NOT EXISTS track_currency_change AFTER UPDATE OF buy_rate,sell_rate ON currencies
        WHEN OLD.buy_rate IS NOT NEW.buy_rate OR OLD.sell_rate IS NOT NEW.sell_rate
        BEGIN INSERT INTO currency_changes VALUES(NEW.currency_code,OLD.buy_rate,OLD.sell_rate,datetime('now','localtime'))
        ON CONFLICT(code) DO UPDATE SET previous_buy=excluded.previous_buy,previous_sell=excluded.previous_sell,changed_at=excluded.changed_at; END''')

# ตรวจบัญชีจริงก่อนอ่านหรือแก้รายการโปรด
def active(conn,actor):
    if not conn.execute("SELECT 1 FROM users WHERE id=? AND status='active'",(actor,)).fetchone():raise PermissionError('บัญชีไม่พร้อมใช้งาน')

# อ่านราคาและสถานะดาวจากฐานข้อมูลชุดเดียว
def listing(actor):
    conn=db.getconnect()
    try:
        active(conn,actor)
        rows=conn.execute('''SELECT c.currency_code,c.currency_name,c.buy_rate,c.sell_rate,h.previous_buy,h.previous_sell,h.changed_at,
            EXISTS(SELECT 1 FROM currency_favorites f WHERE f.user_id=? AND f.code=c.currency_code)
            FROM currencies c LEFT JOIN currency_changes h ON h.code=c.currency_code WHERE c.currency_code!='THB' ORDER BY c.currency_code''',(actor,)).fetchall()
        return [dict(zip(('code','name','buy','sell','previous_buy','previous_sell','changed','favorite'),row)) for row in rows]
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

# บอกส่วนต่างเทียบราคาที่ร้านเปลี่ยนครั้งล่าสุด ไม่อ้างว่าเป็นผลตอบแทนรายวัน
def movement(current,previous):
    if previous is None or previous<=0 or current<=0:return 'ยังไม่มีฐานเปรียบเทียบ','#788478','#f1f3ee'
    delta=Decimal(str(current))-Decimal(str(previous));percent=delta/Decimal(str(previous))*100
    if delta==0:return '— คงที่ 0.0000 (0.00%)','#788478','#f1f3ee'
    return f"{'▲' if delta>0 else '▼'} {delta:+.4f} ({percent:+.2f}%)",('#167349' if delta>0 else '#b64040'),('#e9f6ef' if delta>0 else '#fff0ee')
