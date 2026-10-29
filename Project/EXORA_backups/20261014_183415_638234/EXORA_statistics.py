"""Administrator statistics: count transactions; never add unlike currencies."""
# คำอธิบาย import: ตัวนับและโครงสร้างรวบรวมข้อมูล
from collections import defaultdict,Counter
# คำอธิบาย import: คำนวณยอดทศนิยมโดยไม่บวกต่างสกุลเงินตรง ๆ
from decimal import Decimal
# คำอธิบาย import: จัดการช่วงวันและข้อมูลวันเวลา
from datetime import date,timedelta
# คำอธิบาย import: เชื่อมฐานข้อมูล EXORA
import EXORA_database as db

# อ่านและรวมประวัติตามวันที่และสถานะ โดยคงยอดเดิมและจำกัดสิทธิ์ admin
def report(actor,start='',end='',status='approved',period='day'):
    if period not in ('day','month','year'):raise ValueError('ช่วงสรุปไม่ถูกต้อง')
    if status not in ('approved','pending','rejected','legacy','all'):raise ValueError('สถานะไม่ถูกต้อง')
    for value in (start,end):
        if value:date.fromisoformat(value)
    if start and end and start>end:raise ValueError('วันที่เริ่มต้องไม่เกินวันที่สิ้นสุด')
    conn=db.getconnect()
    try:
        if conn.execute("SELECT role FROM users WHERE id=? AND status='active'",(actor,)).fetchone()!=('admin',):raise PermissionError('เฉพาะ admin')
        conn.row_factory=__import__('sqlite3').Row
        rows=conn.execute('SELECT t.*,u.username FROM transactions t LEFT JOIN users u ON t.user_id=u.id ORDER BY t.transaction_date').fetchall()
    finally:conn.close()
    users={};daily={};currencies={};states=Counter();unknown=0;total=Decimal('0');count=0
    for raw in rows:
        row=dict(raw);day=str(row['transaction_date'])[:10]
        if start and day<start or end and day>end:continue
        states[row['payment_status']]+=1
        if status!='all' and row['payment_status']!=status:continue
        count+=1;amount=None
        if row['from_currency']=='THB':amount=Decimal(str(row['from_amount']))
        elif row['to_currency']=='THB':amount=Decimal(str(row['to_amount']))
        elif row.get('thb_value') is not None:amount=Decimal(str(row['thb_value']))
        # เก็บสถิติแยกสกุลเงินทั้งฝั่งรับและจ่าย ไม่ใช้ราคาปัจจุบันคำนวณย้อนหลัง
        seen=set()
        for side in ('from','to'):
            code=row[side+'_currency']
            if code=='THB':continue
            bucket=currencies.setdefault(code,{'code':code,'count':0,'received':Decimal('0'),'paid':Decimal('0'),'thb':Decimal('0')})
            if code not in seen:
                bucket['count']+=1
                if amount is not None:bucket['thb']+=amount
                seen.add(code)
            bucket['received' if side=='from' else 'paid']+=Decimal(str(row[side+'_amount']))
        uid=row['user_id'];user=users.setdefault(uid,{'id':uid,'name':row['username'] or 'บัญชีเดิม','count':0,'thb':Decimal('0')})
        entry=daily.setdefault(day,{'day':day,'count':0,'thb':Decimal('0'),'unknown':0});user['count']+=1;entry['count']+=1
        if amount is None:unknown+=1;entry['unknown']+=1
        else:user['thb']+=amount;entry['thb']+=amount;total+=amount
    if start and end and (date.fromisoformat(end)-date.fromisoformat(start)).days<=366:
        day=date.fromisoformat(start)
        while day<=date.fromisoformat(end):
            text=day.isoformat();daily.setdefault(text,{'day':text,'count':0,'thb':Decimal('0'),'unknown':0});day+=timedelta(days=1)
    return {'count':count,'thb':total,'unknown':unknown,'states':dict(states),'users':sorted(users.values(),key=lambda x:(-x['count'],x['id'])),'currencies':sorted(currencies.values(),key=lambda x:(-x['thb'],-x['count'],x['code'])),'daily':sorted(daily.values(),key=lambda x:x['day'],reverse=True),'periods':group_periods(daily.values(),period)}

# รวมยอดประวัติเดิมตามวัน เดือน หรือปี โดยไม่ใช้ราคาใหม่คำนวณย้อนหลัง
def group_periods(rows,period):
    lengths={'day':10,'month':7,'year':4}
    if period not in lengths:raise ValueError('ช่วงสรุปไม่ถูกต้อง')
    grouped={}
    for row in rows:
        key=row['day'][:lengths[period]]
        bucket=grouped.setdefault(key,{'day':key,'count':0,'thb':Decimal('0'),'unknown':0})
        for field in ('count','thb','unknown'):bucket[field]+=row[field]
    return sorted(grouped.values(),key=lambda row:row['day'],reverse=True)
