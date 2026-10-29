import unittest
import test_bank_flow as fixtures
import EXORA_bank_flow as flow
class TrackingTests(unittest.TestCase):
    setUp=fixtures.BankFlowTests.setUp
    tearDown=fixtures.BankFlowTests.tearDown
    create=fixtures.BankFlowTests.create
    def test_review_requires_checks_and_admin(self):
        n=self.create()
        with self.assertRaises(ValueError):flow.review_choice(n,self.admin,'ผ่าน',flow.REVIEW_REASONS[0],{},'2027-01-01',-1)
        with self.assertRaises(PermissionError):flow.review_choice(n,self.buyer,'ไม่ผ่าน',flow.REVIEW_REASONS[0],{},None,None)
        self.assertEqual(flow.get(n,self.buyer)['status'],'identity_pending')
    def test_cached_identity_quotes_before_route_but_cannot_pay(self):
        n=self.create();flow.verify(n,self.admin,'Document reviewed manually','Route reviewed manually')
        other=self.create();self.assertEqual(flow.get(other,self.buyer)['status'],'identity_verified')
        flow.quote(other,self.buyer);self.assertEqual(flow.get(other,self.buyer)['status'],'quote_pending_route')
        with self.assertRaises(PermissionError):flow.submit_payment(other,self.buyer,{},self.slip)
        flow.review_choice(other,self.admin,'ผ่าน',flow.REVIEW_REASONS[0],{'route':True},None,None)
        self.assertEqual(flow.get(other,self.buyer)['status'],'quoted')
    def test_feedback_timeline_is_owner_scoped(self):
        n=self.create();flow.review_choice(n,self.admin,'ขอข้อมูลเพิ่มเติม',flow.REVIEW_REASONS[0],{},None,None)
        self.assertIn(flow.REVIEW_REASONS[0],flow.get(n,self.buyer)['feedback'])
        self.assertTrue(flow.timeline(n,self.buyer))
        with self.assertRaises(PermissionError):flow.timeline(n,self.other)
    def test_preexisting_pending_order_reuses_later_identity(self):
        pending=self.create();verified=self.create()
        flow.verify(verified,self.admin,'Document checked manually','Bank route checked manually')
        flow.quote(pending,self.buyer)
        self.assertEqual(flow.get(pending,self.buyer)['status'],'quote_pending_route')
