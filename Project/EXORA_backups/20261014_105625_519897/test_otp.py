import os
import re
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import EXORA_database as db
import EXORA_auth as auth

class OtpTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=os.getenv('EXORA_TEST_TEMP'));self.old=(db.BASE_DIR,db.DB_PATH)
        db.BASE_DIR=self.tmp.name;db.DB_PATH=str(Path(self.tmp.name)/'EXORA.db');db.createdb()
        db.register_user('otp-user','otp@example.test','old-password')
        self.uid=db.login('otp-user','old-password')['id']
        self.env=patch.dict(os.environ,{'EXORA_GMAIL_USER':'sender@example.test','EXORA_GMAIL_APP_PASSWORD':'test-only'})
        self.env.start();self.smtp=patch('EXORA_auth.smtplib.SMTP_SSL');self.mock=self.smtp.start()
    def tearDown(self):
        self.smtp.stop();self.env.stop();db.BASE_DIR,db.DB_PATH=self.old;self.tmp.cleanup()
    def request(self):
        response=auth.request_otp('otp@example.test')
        message=self.mock.return_value.__enter__.return_value.send_message.call_args.args[0]
        code=re.search(r'\b[0-9]{6}\b',message.get_content()).group()
        return response,code
    def test_otp_changes_password_and_is_single_use(self):
        response,code=self.request()
        conn=db.getconnect();row=conn.execute('SELECT code_hash FROM password_reset_otp').fetchone();conn.close()
        self.assertNotEqual(row[0],code);self.assertNotIn(code,str(response))
        auth.reset_with_otp(response['challenge_id'],code,'new-password')
        self.assertIsNone(db.login('otp-user','old-password'));self.assertIsNotNone(db.login('otp-user','new-password'))
        with self.assertRaises(ValueError):auth.reset_with_otp(response['challenge_id'],code,'another-password')
    def test_five_wrong_attempts_lock_otp(self):
        response,code=self.request();wrong='000000' if code!='000000' else '111111'
        for i in range(5):
            with self.assertRaises(ValueError):auth.reset_with_otp(response['challenge_id'],wrong,'new-password')
        with self.assertRaises(ValueError):auth.reset_with_otp(response['challenge_id'],code,'new-password')
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT attempts,used FROM password_reset_otp').fetchone(),(5,1));conn.close()
    def test_expiry(self):
        response,code=self.request()
        with patch('EXORA_auth.time.time',return_value=__import__('time').time()+601):
            with self.assertRaises(ValueError):auth.reset_with_otp(response['challenge_id'],code,'new-password')
    def test_unknown_email_has_generic_response(self):
        response=auth.request_otp('missing@example.test')
        self.assertEqual(response['message'],auth.GENERIC_MESSAGE);self.mock.return_value.__enter__.return_value.send_message.assert_not_called()
        with self.assertRaises(ValueError):auth.reset_with_otp(response['challenge_id'],'123456','new-password')
    def test_resend_throttle_and_invalidates_old(self):
        first,code=self.request()
        with self.assertRaises(ValueError):auth.request_otp('otp@example.test')
        with patch('EXORA_auth.time.time',return_value=__import__('time').time()+61):second,_=self.request()
        with self.assertRaises(ValueError):auth.reset_with_otp(first['challenge_id'],code,'new-password')
        self.assertNotEqual(first['challenge_id'],second['challenge_id'])
    def test_no_email_change_or_inactive_account_bypass(self):
        response,code=self.request();conn=db.getconnect();conn.execute("UPDATE users SET email='changed@example.test' WHERE id=?",(self.uid,));conn.commit();conn.close()
        with self.assertRaises(ValueError):auth.reset_with_otp(response['challenge_id'],code,'new-password')
    def test_legacy_reset_disabled(self):
        ok,_=db.reset_password('otp-user','otp@example.test','new-password')
        self.assertFalse(ok);self.assertIsNotNone(db.login('otp-user','old-password'))
    def test_smtp_failure_invalidates_code(self):
        self.mock.side_effect=OSError('offline')
        response=auth.request_otp('otp@example.test');self.assertEqual(response['message'],auth.GENERIC_MESSAGE)
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT used FROM password_reset_otp').fetchone()[0],1);conn.close()
    def test_missing_sender_config(self):
        with patch.dict(os.environ,{'EXORA_GMAIL_APP_PASSWORD':''}):
            with self.assertRaises(ValueError):auth.request_otp('otp@example.test')

if __name__=='__main__':unittest.main(verbosity=2)
