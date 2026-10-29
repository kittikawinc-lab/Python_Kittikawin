"""Workflow tests with isolated SQLite and mocked Gmail; no network or GUI."""
import unittest
import tempfile
import sqlite3
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
import EXORA_database as db
import EXORA_payments as payments
import EXORA_profiles as profiles
import EXORA_receipts as receipts

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
        self.old=(db.BASE_DIR,db.DB_PATH);db.BASE_DIR=str(self.base);db.DB_PATH=str(self.base/'EXORA.db')
        db.createdb();db.adduser('buyer','test-password','user');db.adduser('other','test-password','user')
        self.admin=db.login('admin','admin123')['id'];self.buyer=db.login('buyer','test-password')['id'];self.other=db.login('other','test-password')['id']
        profiles.set_rate(self.admin,'USD','US Dollar','34','35');profiles.set_rate(self.admin,'EUR','Euro','38','40')
        self.slip=self.base/'slip.png';Image.new('RGB',(300,400),'white').save(self.slip)
        self.data={**profiles.quote('THB','USD','3500'),'customer_name':'ทดสอบ ลูกค้า','customer_phone':'0812345678'}
    def tearDown(self):db.BASE_DIR,db.DB_PATH=self.old;self.temp.cleanup()
    def submit(self,number='TEST-01'):payments.submit(number,self.buyer,self.data,self.slip)
    def test_quote_direction_and_rounding(self):
        self.assertEqual(self.data['to_amount'],100)
        self.assertEqual(profiles.quote('USD','THB',100)['to_amount'],3400)
        self.assertEqual(profiles.quote('USD','EUR',100)['to_amount'],85)
        self.assertEqual(profiles.quote('THB','USD','35.175')['to_amount'],1.01)
    def test_invalid_amounts_and_zero_rates(self):
        for amount in ('nan','inf','-1','0','0.001'):
            with self.assertRaises(ValueError):profiles.quote('THB','USD',amount)
        with self.assertRaises(ValueError):profiles.quote('THB','THB',10)
        with self.assertRaises(ValueError):profiles.quote('THB','JPY',10)
    def test_history_survives_migration(self):
        db.save_transaction('OLD',self.buyer,'SELL','THB',3500,'USD',100,1/35,'เดิม','0812345678')
        conn=db.getconnect();before=conn.execute('SELECT transaction_no,from_amount,to_amount,exchange_rate,transaction_date FROM transactions').fetchall();conn.close()
        db.createdb();db.createdb()
        conn=db.getconnect();after=conn.execute('SELECT transaction_no,from_amount,to_amount,exchange_rate,transaction_date FROM transactions').fetchall();conn.close()
        self.assertEqual(before,after);self.assertEqual(payments.get_transaction('OLD',self.buyer)['payment_status'],'legacy')
    def test_submit_and_role_isolation(self):
        self.submit();row=payments.get_transaction('TEST-01',self.buyer)
        self.assertEqual(row['payment_status'],'pending');self.assertTrue(payments.slip_path(row).is_file())
        self.assertEqual(len(payments.list_transactions(self.other)),0)
        with self.assertRaises(PermissionError):payments.get_transaction('TEST-01',self.other)
        with self.assertRaises(PermissionError):payments.review('TEST-01',self.buyer,'approved')
    def test_approve_once(self):
        self.submit();payments.review('TEST-01',self.admin,'approved','ตรวจแล้ว')
        self.assertEqual(payments.get_transaction('TEST-01',self.buyer)['reviewed_by'],self.admin)
        with self.assertRaises(ValueError):payments.review('TEST-01',self.admin,'approved')
        self.assertEqual(len(payments.get_audit('TEST-01',self.buyer)),2)
    def test_reject_and_resubmit(self):
        self.submit()
        with self.assertRaises(ValueError):payments.review('TEST-01',self.admin,'rejected')
        payments.review('TEST-01',self.admin,'rejected','ยอดไม่ตรง')
        payments.replace_slip('TEST-01',self.buyer,self.slip)
        row=payments.get_transaction('TEST-01',self.buyer);self.assertEqual(row['payment_status'],'pending');self.assertIsNone(row['reviewed_by'])
        payments.review('TEST-01',self.admin,'approved');self.assertEqual(len(payments.get_audit('TEST-01',self.buyer)),4)
    def test_invalid_slip_and_duplicate_roll_back(self):
        wrong=self.base/'fake.png';wrong.write_text('not an image')
        with self.assertRaises(Exception):payments.submit('FAKE',self.buyer,self.data,wrong)
        self.submit();count=len(list((self.base/'EXORA_assets/slips').iterdir()))
        with self.assertRaises(sqlite3.IntegrityError):self.submit()
        self.assertEqual(len(list((self.base/'EXORA_assets/slips').iterdir())),count)
    def test_profile_and_password(self):
        profiles.save_profile(self.buyer,'ผู้ใช้ทดสอบ','buyer@example.test','0812345678','สวัสดี','#125b4a',self.slip)
        profile=profiles.get_profile(self.buyer);self.assertEqual(profile['display_name'],'ผู้ใช้ทดสอบ');self.assertTrue((self.base/profile['avatar_path']).is_file());self.assertNotIn('password',profile)
        with self.assertRaises(ValueError):profiles.change_password(self.buyer,'wrong','new-password')
        profiles.change_password(self.buyer,'test-password','new-password');self.assertIsNotNone(db.login('buyer','new-password'))
    def test_shop_and_admin_guards(self):
        shop=profiles.shop();shop['name']='ร้านทดสอบ';profiles.save_shop(self.admin,shop);self.assertEqual(profiles.shop()['name'],'ร้านทดสอบ')
        with self.assertRaises(PermissionError):profiles.save_shop(self.buyer,shop)
        with self.assertRaises(PermissionError):profiles.set_rate(self.buyer,'USD','US Dollar',1,2)
        with self.assertRaises(ValueError):profiles.update_user(self.admin,self.admin,'user','inactive')
        profiles.update_user(self.admin,self.other,'user','inactive')
        self.assertIsNone(db.login('other','test-password'))
    def test_pdf_and_gmail_mock(self):
        self.submit();payments.review('TEST-01',self.admin,'approved')
        pdf=receipts.export_pdf('TEST-01',self.buyer,self.base/'receipt.pdf');self.assertTrue(pdf.read_bytes().startswith(b'%PDF'))
        with patch.dict(os.environ,{'EXORA_GMAIL_USER':'sender@example.test','EXORA_GMAIL_APP_PASSWORD':'test-only-secret'}),patch('EXORA_receipts.smtplib.SMTP_SSL') as smtp:
            receipts.send_gmail('TEST-01',self.buyer,'recipient@example.test',pdf)
            msg=smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
            self.assertEqual(msg['To'],'recipient@example.test');self.assertEqual(len(list(msg.iter_attachments())),1)
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT status FROM email_log').fetchone()[0],'sent');conn.close()
    def test_email_failure_log_and_unapproved_guard(self):
        self.submit()
        with self.assertRaises(ValueError):receipts.send_gmail('TEST-01',self.buyer,'recipient@example.test',self.slip)
        payments.review('TEST-01',self.admin,'approved')
        with patch.dict(os.environ,{'EXORA_GMAIL_USER':'sender@example.test','EXORA_GMAIL_APP_PASSWORD':'test-only'}),patch('EXORA_receipts.smtplib.SMTP_SSL',side_effect=OSError('offline')):
            with self.assertRaises(OSError):receipts.send_gmail('TEST-01',self.buyer,'recipient@example.test',self.slip)
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT status FROM email_log').fetchone()[0],'failed');conn.close()

if __name__=='__main__':unittest.main(verbosity=2)
