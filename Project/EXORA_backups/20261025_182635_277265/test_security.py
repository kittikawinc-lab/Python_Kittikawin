import unittest,time,hashlib
import test_exora as fixtures
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_payments as payments
from EXORA_security import password_matches

class SecurityTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    bank_data=fixtures.WorkflowTests.bank_data
    def make_data(self,actor=None):return {**profiles.quote('THB','USD',700,actor_id=actor or self.buyer),'customer_name':'Test','customer_phone':'0812345678'}
    def test_tampered_amount_rate_or_stat_value_rejected(self):
        for key,value in [('to_amount',9999),('exchange_rate',999),('thb_value',9999),('transaction_type','BUY')]:
            data=self.make_data();data[key]=value
            with self.assertRaises(ValueError):payments.submit('BAD-'+key,self.buyer,data,self.slip)
        self.assertEqual(payments.list_transactions(self.admin),[])
    def test_quote_one_use_and_rollback_after_invalid_slip(self):
        data=self.make_data();bad=self.base/'bad.png';bad.write_text('not a picture')
        with self.assertRaises(Exception):payments.submit('BAD',self.buyer,data,bad)
        payments.submit('GOOD',self.buyer,data,self.slip)
        with self.assertRaisesRegex(ValueError,'ถูกใช้แล้ว'):payments.submit('REPLAY',self.buyer,data,self.slip)
    def test_expired_or_other_owner_quote_rejected(self):
        data=self.make_data()
        with self.assertRaises(PermissionError):payments.submit('OTHER',self.other,data,self.slip)
        conn=db.getconnect();conn.execute('UPDATE secure_quotes SET expires=? WHERE id=?',(time.time()-1,data['quote_id']));conn.commit();conn.close()
        with self.assertRaisesRegex(ValueError,'หมดอายุ'):payments.submit('EXPIRED',self.buyer,data,self.slip)
    def test_frozen_quote_survives_rate_update(self):
        data=self.make_data();profiles.set_rate(self.admin,'USD','USD',39,40)
        payments.submit('FROZEN',self.buyer,data,self.slip)
        self.assertEqual(payments.get_transaction('FROZEN',self.admin)['to_amount'],20)
    def test_admin_cannot_approve_own_transaction(self):
        payments.submit('SELF',self.admin,self.make_data(self.admin),self.slip)
        with self.assertRaises(PermissionError):payments.review('SELF',self.admin,'approved','test')
    def test_modern_passwords_salted_legacy_login_upgrades(self):
        first=db.hashp('same-password');second=db.hashp('same-password')
        self.assertNotEqual(first,second);self.assertTrue(password_matches('same-password',first));self.assertFalse(password_matches('bad',first))
        conn=db.getconnect();conn.execute('UPDATE users SET password=? WHERE id=?',(hashlib.sha256(b'legacy-password').hexdigest(),self.buyer));conn.commit();conn.close()
        self.assertIsNotNone(db.login('buyer','legacy-password'))
        conn=db.getconnect();self.assertTrue(conn.execute('SELECT password FROM users WHERE id=?',(self.buyer,)).fetchone()[0].startswith('pbkdf2_sha256$'));conn.close()
    def test_login_rate_limit_counts_email_alias(self):
        conn=db.getconnect();conn.execute('UPDATE users SET email=? WHERE id=?',('buyer@example.com',self.buyer));conn.commit();conn.close()
        for index in range(5):self.assertIsNone(db.login('buyer' if index%2==0 else 'buyer@example.com','wrong-password'))
        self.assertIsNone(db.login('buyer','test-password1'))
    def test_default_admin_password_cannot_be_kept(self):
        self.assertTrue(db.login('admin','admin123')['password_change_required'])
        with self.assertRaises(ValueError):profiles.change_password(self.admin,'admin123','admin123')
    def test_verified_password_change_clears_login_lock(self):
        for index in range(5):self.assertIsNone(db.login('buyer','wrong-password'))
        self.assertIsNone(db.login('buyer','test-password1'))
        profiles.change_password(self.buyer,'test-password1','replacement-password1')
        self.assertIsNotNone(db.login('buyer','replacement-password1'))
    def test_registration_cannot_shadow_an_existing_account_case(self):
        ok,message=db.register_user('BUYER','different@example.com','replacement-password1','0812345678')
        self.assertFalse(ok)
    def test_bank_reference_reuse_blocked_even_with_different_image(self):
        from PIL import Image
        data=self.bank_data();payments.submit('BANK',self.buyer,data,self.slip)
        other=self.base/'different.png';Image.new('RGB',(300,400),'green').save(other)
        data={**data,**self.make_data(self.other)}
        with self.assertRaisesRegex(ValueError,'เลขอ้างอิง'):payments.submit('DUP-BANK',self.other,data,other)
        self.assertEqual(len(payments.list_transactions(self.admin)),1)

if __name__=='__main__':unittest.main()
