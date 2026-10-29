import unittest,json,time
from unittest.mock import patch
import test_exora as fixtures
import EXORA_online_demo as demo
import EXORA_database as db

class OnlineDemoTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    def create(self):return demo.create(self.buyer,'Demo Customer','Demo Savings Bank','DEMO-0001','Demo country','THB','USD','3500')
    def ready(self):
        number=self.create();demo.act(number,self.admin,'verify_identity');demo.quote(number,self.buyer);return number
    def test_complete_simulation_isolated_from_real_records(self):
        number=self.ready()
        for actor,action in ((self.buyer,'pay'),(self.admin,'verify_payment'),(self.admin,'start_payout'),(self.admin,'complete')):demo.act(number,actor,action)
        row=demo.get(number,self.buyer);self.assertEqual(row['status'],'completed');self.assertEqual(row['email_status'],'simulated_only');self.assertTrue(row['payout_reference'].startswith('DEMO-'))
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0],0);self.assertEqual(conn.execute('SELECT COUNT(*) FROM admin_alerts').fetchone()[0],0);conn.close()
        with self.assertRaises(ValueError):demo.act(number,self.admin,'complete')
    def test_no_skipped_steps_or_cross_account_access(self):
        number=self.create()
        with self.assertRaises(ValueError):demo.act(number,self.admin,'complete')
        with self.assertRaises(ValueError):demo.quote(number,self.buyer)
        with self.assertRaises(PermissionError):demo.act(number,self.buyer,'verify_identity')
        with self.assertRaises(PermissionError):demo.get(number,self.other)
        self.assertEqual(demo.listing(self.other),[])
    def test_expired_quote_and_no_real_account(self):
        with self.assertRaises(ValueError):demo.create(self.buyer,'Demo','Bank','1234567890','Country','THB','USD','1000')
        number=self.ready();row=demo.get(number,self.buyer);quote=json.loads(row['quote']);quote['quote_expires']=time.time()-1
        conn=db.getconnect();conn.execute('UPDATE online_demo_orders SET quote=? WHERE number=?',(json.dumps(quote),number));conn.commit();conn.close()
        with self.assertRaises(ValueError):demo.act(number,self.buyer,'pay')
        demo.quote(number,self.buyer);demo.act(number,self.buyer,'pay')
    def test_pdf_only_after_completion(self):
        number=self.create()
        with self.assertRaises(ValueError):demo.receipt(number,self.buyer,self.base/'not-created.pdf')
    def test_admin_cannot_verify_own_demo(self):
        number=demo.create(self.admin,'Demo','Demo Bank','DEMO-0002','Country','THB','USD','3500')
        with self.assertRaises(PermissionError):demo.act(number,self.admin,'verify_identity')

if __name__=='__main__':unittest.main()
