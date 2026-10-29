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
        self.app=Application.__new__(Application);self.app.current_user={'id':self.admin,'role':'admin'};self.app.user_preview=False
    def tearDown(self):db.BASE_DIR,db.DB_PATH=self.old;self.temp.cleanup()
    def test_preview_history_only_own_records(self):
        self.assertEqual(len(payments.list_transactions(self.admin)),2)
        self.assertEqual([row[0] for row in payments.list_transactions(self.admin,own_only=True)],['ADMIN'])
        self.assertEqual([row[0] for row in payments.list_transactions(self.buyer)],['BUYER'])
    def test_preview_restricts_admin_view_and_mutations_without_changing_role(self):
        self.assertTrue(self.app.is_admin_view());self.app.user_preview=True
        self.assertFalse(self.app.is_admin_view())
        with self.assertRaises(ValueError):self.app.ensure_not_preview()
        self.assertEqual(self.app.current_user['role'],'admin')
        self.app.user_preview=False;self.app.ensure_not_preview();self.assertTrue(self.app.is_admin_view())
    def test_preview_toggle_rebuilds_ui_without_database_changes(self):
        with patch.object(self.app,'shell') as shell,patch.object(self.app,'home') as home:
            self.app.toggle_user_view();self.assertTrue(self.app.user_preview)
            self.app.toggle_user_view();self.assertFalse(self.app.user_preview)
            self.assertEqual(shell.call_count,2);self.assertEqual(home.call_count,2)
        self.assertEqual(db.login('admin','admin123')['role'],'admin')
    def test_non_admin_cannot_toggle(self):
        self.app.current_user={'id':self.buyer,'role':'user'}
        with self.assertRaises(PermissionError):self.app.toggle_user_view()
    def test_preview_detail_rejects_another_users_record_before_dialog(self):
        self.app.user_preview=True
        with patch.object(self.app,'dialog') as dialog:
            with self.assertRaises(PermissionError):self.app.detail('BUYER')
            dialog.assert_not_called()

if __name__=='__main__':unittest.main()
