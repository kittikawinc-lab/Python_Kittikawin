import unittest
import EXORA_saved_accounts as accounts
import EXORA_bank_flow as flow
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_payments as payments
import test_bank_flow as fixtures
class SavedAccountTests(unittest.TestCase):
    setUp=fixtures.BankFlowTests.setUp
    tearDown=fixtures.BankFlowTests.tearDown
    create=fixtures.BankFlowTests.create
    def test_owner_defaults_and_masking(self):
        a=accounts.save(self.buyer,'recipient','Buyer','Bank','123456789','Thailand')
        b=accounts.save(self.buyer,'recipient','Buyer','Bank','987654321','Thailand',True)
        self.assertEqual([r['id'] for r in accounts.listing(self.buyer,'recipient') if r['is_default']],[b])
        self.assertEqual(accounts.listing(self.other),[])
        with self.assertRaises(PermissionError):accounts.change(self.other,a)
        with self.assertRaises(PermissionError):accounts.change(self.admin,a,True)
        self.assertNotIn('987654321',accounts.caption(accounts.listing(self.buyer)[0]))
        self.assertEqual(accounts.save(self.buyer,'recipient','Buyer','Bank','987654321','Thailand'),b)
        accounts.change(self.buyer,a);self.assertEqual([r['id'] for r in accounts.listing(self.buyer) if r['is_default']],[a])
    def test_transaction_snapshot_survives_saved_account_deletion(self):
        n=flow.create(self.buyer,'Beneficiary','Bank','123456789','Thailand','THB','USD','700',save_account=True)
        a=accounts.listing(self.buyer)[0]['id'];accounts.change(self.buyer,a,True)
        self.assertEqual(flow.get(n,self.buyer)['account'],'123456789')
        self.assertEqual(accounts.listing(self.buyer),[])
    def test_saved_accounts_validate_and_disabled_user_blocked(self):
        with self.assertRaises(ValueError):accounts.save(self.buyer,'payer','Buyer','Bank','GB123456')
        with self.assertRaises(ValueError):accounts.save(self.buyer,'unknown','Buyer','Bank','123456789')
        conn=db.getconnect();conn.execute("UPDATE users SET status='banned' WHERE id=?",(self.buyer,));conn.commit();conn.close()
        with self.assertRaises(PermissionError):accounts.listing(self.buyer)
    def test_payer_saved_atomically_on_submission(self):
        n=self.create();flow.verify(n,self.admin,'Document checked manually','Route checked manually');flow.quote(n,self.buyer)
        payment={'payer_bank':'Bank','payer_name':'Buyer','payer_account':'123456789','transfer_amount':700,'transfer_at':'2026-10-26 12:00','transfer_reference':'IN-REMEMBER','remember_payer':True,'default_payer':True}
        flow.submit_payment(n,self.buyer,payment,self.slip)
        self.assertEqual(accounts.listing(self.buyer,'payer')[0]['account'],'123456789')
        self.assertEqual(flow.get(n,self.buyer)['status'],'payment_pending')
    def test_invalid_account_rolls_back_order(self):
        with self.assertRaises(ValueError):flow.create(self.buyer,'X'*81,'Bank','123456789','Thailand','THB','USD','700',save_account=True)
        self.assertEqual(flow.listing(self.buyer),[])
    def test_defaults_survive_migration(self):
        a=accounts.save(self.buyer,'payer','Buyer','Bank','123456789')
        db.createdb();self.assertEqual(accounts.listing(self.buyer)[0]['id'],a)
    def test_failed_payer_save_does_not_consume_quote_or_store_payment(self):
        n=self.create();flow.verify(n,self.admin,'Document checked manually','Route checked manually');flow.quote(n,self.buyer)
        payment={'payer_bank':'Bank','payer_name':'X'*81,'payer_account':'123456789','transfer_amount':700,'transfer_at':'2026-10-26 12:00','transfer_reference':'IN-ROLLBACK','remember_payer':True}
        with self.assertRaises(ValueError):flow.submit_payment(n,self.buyer,payment,self.slip)
        self.assertEqual(flow.get(n,self.buyer)['status'],'quoted')
        self.assertEqual(payments.list_transactions(self.buyer),[])
        self.assertEqual(accounts.listing(self.buyer,'payer'),[])
        conn=db.getconnect();self.assertIsNone(conn.execute('SELECT used_transaction FROM secure_quotes WHERE id=?',(__import__('json').loads(flow.get(n,self.buyer)['quote'])['quote_id'],)).fetchone()[0]);conn.close()
