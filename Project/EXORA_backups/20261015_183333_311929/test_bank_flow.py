import unittest,json
from unittest.mock import patch
import test_exora as fixtures
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_bank_flow as flow
import EXORA_payments as payments
import EXORA_receipts as receipts

class BankFlowTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    def create(self):
        store=profiles.shop();store.update(bank_name='Bank',bank_account_name='Store',bank_account_number='1234567890');profiles.save_shop(self.admin,store)
        return flow.create(self.buyer,'Beneficiary','Receiving bank SWIFT','123456789012','Destination','THB','USD','3500')
    def paid(self):
        number=self.create();flow.verify(number,self.admin,'Identity manually checked','Bank route and net payout amount verified');flow.quote(number,self.buyer)
        payment={'payer_bank':'Bank','payer_name':'Buyer','payer_account':'123456789','transfer_amount':3500,'transfer_at':'2026-10-15 12:00','transfer_reference':'IN-001'}
        flow.submit_payment(number,self.buyer,payment,self.slip);return number
    def test_full_settlement_no_fake_transfer_or_early_receipt(self):
        number=self.paid();self.assertEqual(flow.get(number,self.buyer)['status'],'payment_pending')
        with self.assertRaises(ValueError):payments.review(number,self.admin,'approved')
        with self.assertRaises(ValueError):receipts.ensure_receipt(number,self.admin)
        flow.verify_payment(number,self.admin,'BANK-IN-001');flow.start_payout(number,self.admin)
        with self.assertRaises(ValueError):flow.complete(number,self.admin,'',self.slip)
        flow.complete(number,self.admin,'BANK-OUT-001',self.slip)
        self.assertEqual(payments.get_transaction(number,self.buyer)['payment_status'],'approved')
        self.assertEqual(flow.get(number,self.buyer)['payout_ref'],'BANK-OUT-001')
        self.assertTrue((self.base/flow.get(number,self.buyer)['payout_proof']).is_file())
        with self.assertRaises(ValueError):flow.complete(number,self.admin,'BANK-OUT-002',self.slip)
    def test_no_bypass_or_wrong_owner(self):
        number=self.create()
        with self.assertRaises(PermissionError):flow.get(number,self.other)
        with self.assertRaises(ValueError):flow.quote(number,self.buyer)
        with self.assertRaises(PermissionError):flow.verify(number,self.buyer,'Verified identity','Bank route verified')
        with self.assertRaises(ValueError):flow.start_payout(number,self.admin)
    def test_failed_submission_rolls_back_order_and_quote(self):
        number=self.create();flow.verify(number,self.admin,'Identity checked manually','Supported route checked manually');price=flow.quote(number,self.buyer)
        with self.assertRaises(ValueError):flow.submit_payment(number,self.buyer,{'transfer_reference':''},self.slip)
        self.assertEqual(flow.get(number,self.buyer)['status'],'quoted')
    def test_bank_savings_accepts_thb_only(self):
        with self.assertRaises(ValueError):flow.create(self.buyer,'A','Bank','1234567890','Country','USD','THB','100')

if __name__=='__main__':unittest.main()
