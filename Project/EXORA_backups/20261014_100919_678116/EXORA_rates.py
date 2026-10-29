"""Online reference rates; shop pricing changes only with administrator opt-in."""
import math
import os
import json
import time
import urllib.request
from urllib.parse import urlencode
from datetime import date, datetime, timezone
import EXORA_database as db
from EXORA_api import getexr

INTERVAL_MS = 300000

def live_enabled():return bool(os.getenv('EXORA_TWELVE_DATA_API_KEY','').strip())

def interval_ms():
    if not live_enabled():return INTERVAL_MS
    try:return max(60,min(3600,int(os.getenv('EXORA_RATE_REFRESH_SECONDS','300'))))*1000
    except ValueError:return INTERVAL_MS

def source_label():
    return 'Twelve Data · ตรวจสอบทุก '+str(interval_ms()//1000)+' วินาที' if live_enabled() else 'Frankfurter (ข้อมูลรายวัน) · ตรวจสอบทุก 5 นาที'

def fetch_live(codes):
    key=os.getenv('EXORA_TWELVE_DATA_API_KEY','').strip();values={};dates={};timestamps={};deadline=time.monotonic()+25
    try:
        for code in codes:
            if time.monotonic()>=deadline:raise TimeoutError()
            symbol=code+'/THB'
            url='https://api.twelvedata.com/currency_conversion?'+urlencode({'symbol':symbol,'amount':1,'apikey':key,'dp':10})
            request=urllib.request.Request(url,headers={'User-Agent':'EXORA/1.0'})
            with urllib.request.urlopen(request,timeout=max(1,min(10,deadline-time.monotonic()))) as response:data=json.loads(response.read(1048576).decode('utf-8'))
            stamp=float(data['timestamp']);now=datetime.now(timezone.utc).timestamp()
            if data.get('symbol')!=symbol or not math.isfinite(stamp) or not -60<=now-stamp<=900:raise ValueError('invalid or stale data')
            mid=float(data['rate'])
            if not math.isfinite(mid) or mid<=0:raise ValueError('invalid rate')
            values[code]=1/mid;dates[code]=datetime.fromtimestamp(stamp,timezone.utc).date().isoformat();timestamps[code]=stamp
        return {'success':True,'rates':values,'dates':dates,'timestamps':timestamps}
    except Exception:
        # HTTP errors may contain the credential URL: never return their text.
        return {'success':False}

def migrate(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS market_rates(code TEXT PRIMARY KEY,mid REAL NOT NULL,source_date TEXT NOT NULL,checked_at TEXT NOT NULL)')
    columns={r[1] for r in conn.execute('PRAGMA table_info(market_rates)')}
    for name in ('source','source_time'):
        if name not in columns:conn.execute('ALTER TABLE market_rates ADD COLUMN '+name+' TEXT')
    conn.execute("INSERT OR IGNORE INTO shop_settings VALUES ('online_pricing','0')")
    conn.execute("INSERT OR IGNORE INTO shop_settings VALUES ('online_spread','2')")

def snapshot():
    conn=db.getconnect()
    try:
        migrate(conn);conn.commit()
        return {r[0]:{'mid':r[1],'date':r[2],'checked':r[3],'source':r[4],'time':r[5]} for r in conn.execute('SELECT code,mid,source_date,checked_at,source,source_time FROM market_rates')}
    finally:conn.close()

def settings(actor_id,enabled,spread):
    value=float(spread)
    if not math.isfinite(value) or not 0<=value<=20:raise ValueError('ส่วนต่างต้องอยู่ระหว่าง 0–20%')
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE')
        row=conn.execute("SELECT role,status FROM users WHERE id=?",(actor_id,)).fetchone()
        if not row or row!=('admin','active'):raise PermissionError('เฉพาะ admin')
        migrate(conn)
        conn.executemany('UPDATE shop_settings SET value=? WHERE key=?',[(str(int(bool(enabled))),'online_pricing'),(str(value),'online_spread')]);conn.commit()
    finally:conn.close()

def refresh():
    codes=[r[1] for r in db.getcurs() if r[1]!='THB']
    live=live_enabled();response=fetch_live(codes) if live else getexr('THB',codes)
    if not response.get('success'):return {'ok':False,'message':'ออฟไลน์ / ดึงข้อมูลไม่สำเร็จ · ใช้ราคาที่บันทึกไว้'}
    try:
        rates=response['rates'];dates=response.get('dates',{})
        parsed={}
        for code in codes:
            rate=float(rates[code]);day=dates.get(code,response.get('date'))
            age=(date.today()-date.fromisoformat(day)).days
            if not math.isfinite(rate) or rate<=0 or not 0<=age<=7:raise ValueError('invalid or stale rate')
            mid=1/rate
            if not math.isfinite(mid):raise ValueError('invalid rate')
            parsed[code]=(mid,day)
        if not parsed:raise ValueError('no currencies')
    except (KeyError,ValueError,TypeError,OverflowError):
        return {'ok':False,'message':'ข้อมูลไม่ครบหรือเก่าเกิน 7 วัน · ใช้ราคาที่บันทึกไว้'}
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');migrate(conn)
        config=dict(conn.execute('SELECT key,value FROM shop_settings'))
        enabled=config.get('online_pricing')=='1';spread=float(config.get('online_spread','2'))/100
        if not math.isfinite(spread) or not 0<=spread<=.2:raise ValueError('ส่วนต่างไม่ถูกต้อง')
        checked=datetime.now(timezone.utc).isoformat()
        for code,(mid,day) in parsed.items():
            source_time=datetime.fromtimestamp(response['timestamps'][code],timezone.utc).astimezone().isoformat(timespec='seconds') if live else day
            conn.execute('INSERT OR REPLACE INTO market_rates(code,mid,source_date,checked_at,source,source_time) VALUES (?,?,?,?,?,?)',(code,mid,day,checked,'Twelve Data' if live else 'Frankfurter',source_time))
            if enabled:
                conn.execute('UPDATE currencies SET mid_rate=?,buy_rate=?,sell_rate=?,api_date=?,updated_at=? WHERE currency_code=?',(mid,mid*(1-spread),mid*(1+spread),day,datetime.now().isoformat(timespec='seconds'),code))
        conn.commit()
        data_time=min(datetime.fromtimestamp(t,timezone.utc).astimezone().isoformat(timespec='seconds') for t in response['timestamps'].values()) if live else min(d for _,d in parsed.values())
        return {'ok':True,'message':'ออนไลน์ · ตรวจสอบ '+datetime.now().strftime('%H:%M:%S')+' · ข้อมูล '+data_time+' · '+('ราคาซื้อ–ขายอัตโนมัติ' if enabled else 'ราคาซื้อ–ขายที่ร้านตั้ง'),'pricing':enabled}
    except Exception:
        conn.rollback();raise
    finally:conn.close()
