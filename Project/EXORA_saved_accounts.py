"""Owner-only saved accounts; transaction records remain immutable snapshots."""
import re,sqlite3
import EXORA_database as db

def migrate(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS saved_accounts(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,kind TEXT NOT NULL CHECK(kind IN ('recipient','payer')),name TEXT NOT NULL,bank TEXT NOT NULL,account TEXT NOT NULL,country TEXT NOT NULL DEFAULT '',is_default INTEGER NOT NULL DEFAULT 0,UNIQUE(user_id,kind,bank,account,country))''')
    conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS saved_account_default ON saved_accounts(user_id,kind) WHERE is_default=1')

def owner(conn,actor):
    if not conn.execute("SELECT 1 FROM users WHERE id=? AND status='active'",(actor,)).fetchone():raise PermissionError('บัญชีไม่พร้อมใช้งาน')

def clean(kind,name,bank,account,country=''):
    if kind not in ('recipient','payer'):raise ValueError('ประเภทบัญชีไม่ถูกต้อง')
    name=str(name).strip();bank=str(bank).strip();account=re.sub(r'[ -]','',str(account)).upper();country=str(country).strip() if kind=='recipient' else ''
    if not 1<=len(name)<=80 or not 1<=len(bank)<=120 or len(country)>120 or (kind=='recipient' and not country):raise ValueError('กรุณากรอกข้อมูลบัญชีให้ครบถ้วน')
    if not re.fullmatch(r'[A-Z0-9]{6,34}' if kind=='recipient' else r'[0-9]{6,20}',account):raise ValueError('เลขบัญชีไม่ถูกต้อง')
    return name,bank,account,country

def save_on(conn,actor,kind,name,bank,account,country='',default=False):
    owner(conn,actor);name,bank,account,country=clean(kind,name,bank,account,country)
    existing=conn.execute('SELECT id FROM saved_accounts WHERE user_id=? AND kind=? AND bank=? AND account=? AND country=?',(actor,kind,bank,account,country)).fetchone()
    count=conn.execute('SELECT COUNT(*) FROM saved_accounts WHERE user_id=? AND kind=?',(actor,kind)).fetchone()[0]
    if not existing and count>=20:raise ValueError('บันทึกบัญชีได้ไม่เกิน 20 บัญชีต่อประเภท กรุณาลบบัญชีที่ไม่ใช้')
    default=bool(default) or count==0
    if default:conn.execute('UPDATE saved_accounts SET is_default=0 WHERE user_id=? AND kind=?',(actor,kind))
    if existing:
        conn.execute('UPDATE saved_accounts SET name=?,is_default=CASE WHEN ? THEN 1 ELSE is_default END WHERE id=?',(name,default,existing[0]));return existing[0]
    return conn.execute('INSERT INTO saved_accounts(user_id,kind,name,bank,account,country,is_default) VALUES (?,?,?,?,?,?,?)',(actor,kind,name,bank,account,country,int(default))).lastrowid

def save(actor,kind,name,bank,account,country='',default=False):
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');result=save_on(conn,actor,kind,name,bank,account,country,default);conn.commit();return result
    except Exception:conn.rollback();raise
    finally:conn.close()

def listing(actor,kind=None):
    conn=db.getconnect()
    try:
        owner(conn,actor);conn.row_factory=sqlite3.Row
        return [dict(r) for r in conn.execute('SELECT * FROM saved_accounts WHERE user_id=?'+(' AND kind=?' if kind else '')+' ORDER BY kind,is_default DESC,id DESC',(actor,kind) if kind else (actor,))]
    finally:conn.close()

def change(actor,identifier,delete=False):
    conn=db.getconnect()
    try:
        conn.execute('BEGIN IMMEDIATE');owner(conn,actor)
        row=conn.execute('SELECT kind FROM saved_accounts WHERE id=? AND user_id=?',(identifier,actor)).fetchone()
        if not row:raise PermissionError('ไม่พบบัญชีที่บันทึกไว้ของคุณ')
        if delete:conn.execute('DELETE FROM saved_accounts WHERE id=? AND user_id=?',(identifier,actor))
        else:
            conn.execute('UPDATE saved_accounts SET is_default=0 WHERE user_id=? AND kind=?',(actor,row[0]));conn.execute('UPDATE saved_accounts SET is_default=1 WHERE id=? AND user_id=?',(identifier,actor))
        conn.commit()
    except Exception:conn.rollback();raise
    finally:conn.close()

def caption(row):return row['bank']+' · ••••'+row['account'][-4:]+' · '+row['name']+' (#'+str(row['id'])+')'

def customer_name(actor):
    conn=db.getconnect()
    try:
        owner(conn,actor)
        row=conn.execute('SELECT legal_name FROM verified_identities WHERE user_id=?',(actor,)).fetchone()
        if row:
            from EXORA_identity import valid
            if valid(conn,actor,row[0]):return row[0]
        return conn.execute('SELECT COALESCE(display_name,\'\') FROM users WHERE id=?',(actor,)).fetchone()[0]
    finally:conn.close()
