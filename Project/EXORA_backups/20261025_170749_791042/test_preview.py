import os,tempfile,unittest
from unittest.mock import patch
from types import SimpleNamespace
import EXORA_database as db
import EXORA_payments as payments
from EXORA_gui import Application

class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=os.getenv('EXORA_TEST_TEMP'));self.old=db.BASE_DIR,db.DB_PATH
        db.BASE_DIR=self.temp.name;db.DB_PATH=self.temp.name+'/EXORA.db';db.createdb()
        self.admin=db.login('admin','admin123')['id'];db.adduser('buyer','password','user');self.buyer=db.login('buyer','password')['id']
        for number,user in [('ADMIN',self.admin),('BUYER',self.buyer)]:db.save_transaction(number,user,'SELL','THB',3500,'USD',100,1/35,'Test','')
        self.app=Application.__new__(Application);self.app.current_user={'id':self.admin,'role':'admin'}
    def tearDown(self):db.BASE_DIR,db.DB_PATH=self.old;self.temp.cleanup()
    def test_preview_history_only_own_records(self):
        self.assertEqual(len(payments.list_transactions(self.admin)),2)
        self.assertEqual([row[0] for row in payments.list_transactions(self.admin,own_only=True)],['ADMIN'])
        self.assertEqual([row[0] for row in payments.list_transactions(self.buyer)],['BUYER'])
    def test_preview_feature_removed(self):
        self.assertFalse(hasattr(self.app,'toggle_user_view'))
        self.app.ensure_not_preview();self.assertTrue(self.app.is_admin_view())
    def test_user_cannot_launch_window_or_gain_admin_view(self):
        self.app.current_user={'id':self.buyer,'role':'admin'}
        self.assertFalse(self.app.is_admin_view())
        with self.assertRaises(PermissionError):self.app.open_new_window()
    def test_inactive_account_cannot_mutate(self):
        conn=db.getconnect();conn.execute("UPDATE users SET status='banned' WHERE id=?",(self.admin,));conn.commit();conn.close()
        self.assertFalse(self.app.is_admin_view())
        with self.assertRaises(ValueError):self.app.ensure_not_preview()

if __name__=='__main__':unittest.main()
