import sqlite3
import hashlib
import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "EXORA.db")

def getconnect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hashp(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

def createdb():
    conn = getconnect()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL)""")

    cursor.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cursor.fetchall()]

    if "email" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")

    if "created_at" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")

    if "last_login" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")

    if "status" not in user_columns:
        cursor.execute("""ALTER TABLE users
    ADD COLUMN status TEXT NOT NULL DEFAULT 'active'""")

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique
    ON users(email)
    WHERE email IS NOT NULL AND email != '' """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS currencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_code TEXT UNIQUE NOT NULL,
    currency_name TEXT NOT NULL,
    buy_rate REAL NOT NULL,
    sell_rate REAL NOT NULL,
    mid_rate REAL DEFAULT 0,
    api_date TEXT,
    updated_at TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_no TEXT UNIQUE NOT NULL,
    user_id INTEGER,
    transaction_type TEXT,
    from_currency TEXT,
    from_amount REAL,
    to_currency TEXT,
    to_amount REAL,
    exchange_rate REAL,
    transaction_date TEXT,
    FOREIGN KEY (user_id)
    REFERENCES users(id))""")

    cursor.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in cursor.fetchall()]

    if "customer_name" not in columns:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN customer_name TEXT")

    if "customer_phone" not in columns:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN customer_phone TEXT")

    cursor.execute("PRAGMA table_info(currencies)")
    columns = [column[1] for column in cursor.fetchall()]
    if "mid_rate" not in columns:
        cursor.execute("""ALTER TABLE currencies ADD COLUMN mid_rate REAL DEFAULT 0""")
    if "api_date" not in columns:
        cursor.execute("""ALTER TABLE currencies ADD COLUMN api_date TEXT""")
    if "updated_at" not in columns:
        cursor.execute("""ALTER TABLE currencies ADD COLUMN updated_at TEXT""")

    cursor.execute("SELECT id FROM users WHERE username = ?",("admin",))
    admin = cursor.fetchone()
    if admin is None:
        cursor.execute("""INSERT INTO users (username, password, role) VALUES (?, ?, ?)""",("admin",hashp("admin123"),"admin"))

    cursor.execute("SELECT COUNT(*) FROM currencies")
    currency_count = cursor.fetchone()[0]
    if currency_count == 0:
        default_currencies = [
            ("USD", "US Dollar", 0, 0, 0),

            ("EUR", "Euro", 0, 0, 0),

            ("GBP", "British Pound", 0, 0, 0),

            ("JPY", "Japanese Yen", 0, 0, 0),

            ("CNY", "Chinese Yuan", 0, 0, 0),

            ("KRW", "South Korean Won", 0, 0, 0),

            ("SGD", "Singapore Dollar", 0, 0, 0),

            ("AUD", "Australian Dollar", 0, 0, 0),

            ("CAD", "Canadian Dollar", 0, 0, 0),

            ("THB", "Thai Baht", 1, 1, 1)
        ]
        cursor.executemany("""INSERT INTO currencies (
        currency_code,
        currency_name,
        buy_rate,
        sell_rate,
        mid_rate) VALUES (?, ?, ?, ?, ?)""", default_currencies)
    conn.commit()
    conn.close()

def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "กรุณากรอกข้อมูลให้ครบทุกช่อง"

    if len(username) < 3:
        return False, "Username ต้องมีอย่างน้อย 3 ตัวอักษร"

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "รูปแบบ Email ไม่ถูกต้อง"

    if len(password) < 8:
        return False, "Password ต้องมีอย่างน้อย 8 ตัวอักษร"

    conn = getconnect()

    try:
        conn.execute("""
            INSERT INTO users
                (username, password, role, email, created_at, status)
            VALUES (?, ?, 'user', ?, ?, 'active')
        """, (
            username,
            hashp(password),
            email,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        return True, "สร้างบัญชีสำเร็จ สามารถเข้าสู่ระบบได้แล้ว"

    except sqlite3.IntegrityError:
        return False, "Username หรือ Email นี้ถูกใช้งานแล้ว"

    finally:
        conn.close()

def login(username, password):
    identifier = username.strip()
    conn = getconnect()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, role
            FROM users
            WHERE (
                LOWER(username) = LOWER(?)
                OR LOWER(COALESCE(email, '')) = LOWER(?)
            )
            AND password = ?
            AND status = 'active'
        """, (identifier, identifier, hashp(password)))

        result = cursor.fetchone()

        if result:
            cursor.execute("""
                UPDATE users
                SET last_login = ?
                WHERE id = ?
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                result[0]
            ))
            conn.commit()

            return {
                "id": result[0],
                "username": result[1],
                "role": result[2]
            }

        return None

    finally:
        conn.close()

def reset_password(identifier, email, new_password):
    identifier = identifier.strip()
    email = email.strip().lower()

    if len(new_password) < 8:
        return False, "Password ใหม่ต้องมีอย่างน้อย 8 ตัวอักษร"

    conn = getconnect()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id
            FROM users
            WHERE (
                LOWER(username) = LOWER(?)
                OR LOWER(COALESCE(email, '')) = LOWER(?)
            )
            AND LOWER(COALESCE(email, '')) = LOWER(?)
            AND status = 'active'
        """, (identifier, identifier, email))

        row = cursor.fetchone()

        if not row:
            return False, "ไม่พบบัญชีที่ตรงกับข้อมูลที่ระบุ"

        conn.execute("""
            UPDATE users
            SET password = ?
            WHERE id = ?
        """, (hashp(new_password), row[0]))

        conn.commit()
        return True, "เปลี่ยน Password แล้ว กรุณาเข้าสู่ระบบอีกครั้ง"

    finally:
        conn.close()

def user():
    conn = getconnect()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, username, role FROM users ORDER BY id""")
    data = cursor.fetchall()
    conn.close()
    return data

def adduser(username, password, role):
    conn = getconnect()
    try:
        conn.execute("""INSERT INTO users (username, password, role) VALUES (?, ?, ?)""",(username, hashp(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def deluser(user_id):
    conn = getconnect()
    conn.execute("""DELETE FROM users WHERE id = ?""",(user_id,))
    conn.commit()
    conn.close()

def getcurs():
    conn = getconnect()
    cursor = conn.cursor()
    cursor.execute(""" SELECT
            id,
            currency_code,
            currency_name,
            buy_rate,
            sell_rate,
            mid_rate,
            api_date,
            updated_at FROM currencies ORDER BY CASE
                WHEN currency_code = 'THB'
                THEN 0
                ELSE 1
            END,
            currency_code""")
    data = cursor.fetchall()
    conn.close()
    return data

def getcur(code):
    conn = getconnect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            currency_code,
            currency_name,
            buy_rate,
            sell_rate,
            mid_rate,
            api_date,
            updated_at
        FROM currencies WHERE currency_code = ?""", (code,))
    data = cursor.fetchone()
    conn.close()
    return data

def upcur_api(currency_code, mid_rate, buy_rate, sell_rate, api_date):
    conn = getconnect()
    cursor = conn.cursor()

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ตรวจว่ามีสกุลเงินนี้อยู่แล้วหรือไม่
    cursor.execute(
        "SELECT id FROM currencies WHERE currency_code = ?",
        (currency_code,)
    )

    existing = cursor.fetchone()

    if existing:
        # มีข้อมูลแล้ว → UPDATE
        cursor.execute("""
            UPDATE currencies
            SET
                mid_rate = ?,
                buy_rate = ?,
                sell_rate = ?,
                api_date = ?,
                updated_at = ?
            WHERE currency_code = ?
        """, (
            mid_rate,
            buy_rate,
            sell_rate,
            api_date,
            updated_at,
            currency_code
        ))

    else:
        # ยังไม่มี → INSERT
        currency_names = {
            "USD": "US Dollar",
            "EUR": "Euro",
            "GBP": "British Pound",
            "JPY": "Japanese Yen",
            "CNY": "Chinese Yuan",
            "KRW": "South Korean Won",
            "SGD": "Singapore Dollar",
            "AUD": "Australian Dollar",
            "CAD": "Canadian Dollar",
            "THB": "Thai Baht"
        }

        currency_name = currency_names.get(
            currency_code,
            currency_code
        )

        cursor.execute("""
            INSERT INTO currencies (
                currency_code,
                currency_name,
                buy_rate,
                sell_rate,
                mid_rate,
                api_date,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            currency_code,
            currency_name,
            buy_rate,
            sell_rate,
            mid_rate,
            api_date,
            updated_at
        ))

    conn.commit()
    conn.close()

def addcur(code, name, buy_rate, sell_rate):
    conn = getconnect()
    try:
        conn.execute(""" INSERT INTO currencies (
                currency_code,
                currency_name,
                buy_rate,
                sell_rate,
                mid_rate
            ) VALUES (?, ?, ?, ?, ?)""",(code,name,buy_rate,sell_rate,0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def upcur(currency_id, code, name, buy_rate, sell_rate):
    conn = getconnect()
    conn.execute("""UPDATE currencies SET
        currency_code = ?,
        currency_name = ?,
        buy_rate = ?,
        sell_rate = ? WHERE id = ?""", ( code, name, buy_rate, sell_rate, currency_id))
    conn.commit()
    conn.close()

def delcur(currency_id):
    conn = getconnect()
    conn.execute("""DELETE FROM currencies WHERE id = ?""",(currency_id,))
    conn.commit()
    conn.close()


def save_transaction(
    transaction_no,
    user_id,
    transaction_type,
    from_currency,
    from_amount,
    to_currency,
    to_amount,
    exchange_rate,
    customer_name=None,
    customer_phone=None
):
    conn = getconnect()

    try:
        transaction_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        conn.execute("""
            INSERT INTO transactions (
                transaction_no,
                user_id,
                transaction_type,
                from_currency,
                from_amount,
                to_currency,
                to_amount,
                exchange_rate,
                transaction_date,
                customer_name,
                customer_phone
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_no,
            user_id,
            transaction_type,
            from_currency,
            from_amount,
            to_currency,
            to_amount,
            exchange_rate,
            transaction_date,
            customer_name,
            customer_phone
        ))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_transactions(search=""):
    conn = getconnect()
    cursor = conn.cursor()

    try:
        sql = """
            SELECT
                t.transaction_no,
                u.username,
                t.transaction_type,
                t.from_currency,
                t.from_amount,
                t.to_currency,
                t.to_amount,
                t.exchange_rate,
                t.transaction_date
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.id
            WHERE COALESCE(u.role, '') != 'admin'
        """

        params = []

        if search:
            sql += """
                AND (
                    t.transaction_no LIKE ?
                    OR u.username LIKE ?
                    OR t.from_currency LIKE ?
                    OR t.to_currency LIKE ?
                )
            """
            keyword = f"%{search}%"
            params = [keyword, keyword, keyword, keyword]

        sql += " ORDER BY t.id DESC"

        cursor.execute(sql, params)
        return cursor.fetchall()

    finally:
        conn.close()

def get_currencies():
    return getcurs()


def get_currency(code):
    return getcur(code)


def update_currency_api(
    currency_code, mid_rate, buy_rate, sell_rate, api_date
):
    return upcur_api(
        currency_code, mid_rate, buy_rate, sell_rate, api_date
    )

