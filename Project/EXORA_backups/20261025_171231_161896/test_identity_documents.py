import unittest
import test_bank_flow as fixtures
import EXORA_identity_docs as docs
import EXORA_bank_flow as flow
import EXORA_notifications as notifications
from pathlib import Path

class DocumentTests(unittest.TestCase):
    setUp=fixtures.BankFlowTests.setUp
    tearDown=fixtures.BankFlowTests.tearDown
    create=fixtures.BankFlowTests.create
    def test_encryption_and_access_control(self):
        self.create();document=docs.current(self.buyer);data=(self.base/document['path']).read_bytes()
        self.assertFalse(data.startswith(b'\x89PNG'))
        self.assertEqual(docs.image(self.admin,self.buyer).size,(300,400))
        self.assertEqual(docs.image(self.buyer,self.buyer).size,(300,400))
        with self.assertRaises(PermissionError):docs.image(self.other,self.buyer)
    def test_replacement_invalidates_identity_and_requires_image(self):
        number=self.create();flow.verify(number,self.admin,'Document reviewed manually','Bank route independently checked')
        self.assertTrue(flow.identity_status(number,self.buyer))
        docs.upload(self.buyer,'id_card',self.slip)
        self.assertFalse(flow.identity_status(number,self.buyer))
        with self.assertRaises(ValueError):docs.upload(self.buyer,'unsupported',self.slip)
    def test_pending_count_includes_pre_payment_once(self):
        self.create();self.assertEqual(notifications.pending(self.admin),1)
        self.assertEqual(notifications.pending(self.buyer),1);self.assertEqual(notifications.pending(self.other),0)
    def test_cannot_verify_without_uploaded_document(self):
        number=flow.create(self.buyer,'Beneficiary','Bank','1234567890','Country','THB','USD','1000')
        with self.assertRaises(ValueError):flow.verify(number,self.admin,'Document checked manually','Bank route checked manually')
    def test_document_replaced_during_admin_review(self):
        number=self.create();old=docs.current(self.buyer)['id'];docs.upload(self.buyer,'id_card',self.slip)
        with self.assertRaises(ValueError):flow.verify(number,self.admin,'Document checked manually','Bank route checked manually',expected_document_id=old)
        self.assertFalse(flow.identity_status(number,self.buyer))
    def test_multiple_windows_cannot_start_same_payout_twice(self):
        number=fixtures.BankFlowTests.paid(self);flow.verify_payment(number,self.admin,'BANK-IN-001')
        from concurrent.futures import ThreadPoolExecutor
        def start():
            try:flow.start_payout(number,self.admin);return True
            except ValueError:return False
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:start(),range(2)))
        self.assertEqual(sorted(results),[False,True])

if __name__=='__main__':unittest.main()
