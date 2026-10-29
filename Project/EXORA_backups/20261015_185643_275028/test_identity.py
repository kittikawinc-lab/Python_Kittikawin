import unittest
from datetime import date,timedelta
import test_bank_flow as fixtures
import EXORA_bank_flow as flow
import EXORA_database as db
import EXORA_identity as identity

class IdentityTests(unittest.TestCase):
    setUp=fixtures.BankFlowTests.setUp
    tearDown=fixtures.BankFlowTests.tearDown
    create=fixtures.BankFlowTests.create
    def verify(self):
        number=self.create();flow.verify(number,self.admin,'Passport checked via video REF-0001','Bank route independently checked')
        return number
    def test_verified_account_skips_identity_next_order_but_checks_route(self):
        first=self.verify();second=self.create()
        self.assertEqual(flow.get(second,self.buyer)['status'],'route_pending')
        flow.verify(second,self.admin,'','Destination bank and account reviewed')
        self.assertTrue(flow.identity_status(second,self.buyer))
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT COUNT(*) FROM identity_audit').fetchone()[0],1);conn.close()
    def test_profile_change_or_other_recipient_requires_new_review(self):
        first=self.verify();conn=db.getconnect();conn.execute("UPDATE users SET phone='0899999999' WHERE id=?",(self.buyer,));conn.commit();conn.close()
        self.assertFalse(flow.identity_status(first,self.buyer))
        self.assertEqual(flow.get(self.create(),self.buyer)['status'],'identity_pending')
    def test_revoked_identity_blocks_payment_and_payout(self):
        first=self.verify();flow.quote(first,self.buyer);flow.revoke_identity(first,self.admin)
        with self.assertRaises(ValueError):flow.quote(first,self.buyer)
        payment={'payer_bank':'Bank','payer_name':'Buyer','payer_account':'123456789','transfer_amount':3500,'transfer_at':'2026-10-15 12:00','transfer_reference':'IN-001'}
        with self.assertRaises(ValueError):flow.submit_payment(first,self.buyer,payment,self.slip)
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0],0);conn.close()
        self.assertEqual(flow.get(self.create(),self.buyer)['status'],'identity_pending')
    def test_expired_review_and_permission(self):
        first=self.verify();conn=db.getconnect();conn.execute('UPDATE verified_identities SET valid_until=?',((date.today()-timedelta(days=1)).isoformat(),));conn.commit();conn.close()
        self.assertFalse(flow.identity_status(first,self.buyer))
        with self.assertRaises(PermissionError):flow.revoke_identity(first,self.buyer)
        with self.assertRaises(ValueError):flow.renew_identity(first,self.admin,'Valid document and face reviewed','document_video','2000-01-01')
    def test_different_beneficiary_is_not_auto_verified(self):
        self.verify()
        number=flow.create(self.buyer,'Another Person','Receiving bank','123456789012','Destination','THB','USD','1000')
        self.assertEqual(flow.get(number,self.buyer)['status'],'identity_pending')

if __name__=='__main__':unittest.main()
