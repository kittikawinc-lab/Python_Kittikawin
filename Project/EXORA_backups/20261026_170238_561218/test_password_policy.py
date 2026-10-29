import unittest,time
import EXORA_security as security
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_auth as auth
import test_exora as fixtures
class PasswordPolicyTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    def test_new_password_rules(self):
        for value in ('abc1234','abcdefgh','12345678','!!!!!!!!',' '*8,'A1'+'x'*255):
            with self.subTest(value=value),self.assertRaises(ValueError):security.validate_new_password(value)
        for value in ('abcde123','ภาษาไทย123','Ab12!@#$'):security.validate_new_password(value)
    def test_signup_and_change_cannot_bypass_policy(self):
        for value in ('abcdefgh','12345678','Ab12345'):
            ok,_=db.register_user('newbuyer','new@example.test',value,'0812345678');self.assertFalse(ok)
            with self.assertRaises(ValueError):db.adduser('newbuyer',value,'user')
            with self.assertRaises(ValueError):profiles.change_password(self.buyer,'test-password1',value)
        self.assertIsNotNone(db.login('buyer','test-password1'))
    def test_legacy_short_password_remains_valid(self):
        conn=db.getconnect();conn.execute('UPDATE users SET password=? WHERE id=?',(db.hashp('old'),self.buyer));conn.commit();conn.close()
        self.assertIsNotNone(db.login('buyer','old'))
        profiles.change_password(self.buyer,'old','newpass123');self.assertIsNotNone(db.login('buyer','newpass123'))
    def test_invalid_reset_preserves_otp_for_valid_password(self):
        conn=db.getconnect();auth.migrate(conn);conn.execute('UPDATE users SET email=? WHERE id=?',('buyer@example.test',self.buyer))
        salt='1234567890abcdef';code='123456';now=time.time()
        conn.execute('INSERT INTO password_reset_otp(challenge_id,user_id,email,salt,code_hash,expires_at,created_at) VALUES (?,?,?,?,?,?,?)',('challenge',self.buyer,'buyer@example.test',salt,auth.digest(code,salt),now+600,now));conn.commit();conn.close()
        with self.assertRaises(ValueError):auth.reset_with_otp('challenge',code,'abcdefgh')
        auth.reset_with_otp('challenge',code,'newpass123');self.assertIsNotNone(db.login('buyer','newpass123'))
