import unittest
import test_exora as fixtures
import EXORA_profiles as profiles
import EXORA_database as db
import EXORA_i18n as i18n

class LanguageTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    def test_language_is_per_account_and_survives_migration(self):
        profiles.save_language(self.buyer,'zh');db.createdb()
        self.assertEqual(profiles.get_profile(self.buyer)['language'],'zh')
        self.assertEqual(profiles.get_profile(self.other)['language'],'th')
        with self.assertRaises(ValueError):profiles.save_language(self.buyer,'xx')
        conn=db.getconnect();conn.execute("UPDATE users SET status='banned' WHERE id=?",(self.buyer,));conn.commit();conn.close()
        with self.assertRaises(PermissionError):profiles.save_language(self.buyer,'en')
    def test_catalog_and_technical_values(self):
        try:
            i18n.set_language('en');self.assertEqual(i18n.translate('คำนวณเงิน'),'Currency calculator')
            self.assertEqual(i18n.translate('exoraadmin@gmail.com'),'exoraadmin@gmail.com')
            i18n.set_language('zh');self.assertEqual(i18n.translate('คำนวณเงิน'),'兑换计算器')
            self.assertEqual(i18n.translate('USD / THB 1,000.00'),'USD / THB 1,000.00')
        finally:i18n.set_language('th')
if __name__=='__main__':unittest.main()
