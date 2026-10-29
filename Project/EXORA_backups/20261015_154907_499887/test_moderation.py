import unittest
from pathlib import Path
from PIL import Image,PngImagePlugin
import test_exora as fixtures
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_payments as payments

class ModerationTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    submit=fixtures.WorkflowTests.submit
    def fresh(self):return {**self.data,**profiles.quote('THB','USD',3500,actor_id=self.other)}
    # Reuse fixture only; test methods below exercise the new features.
    def test_ban_restore_and_soft_delete_preserve_history(self):
        self.submit();profiles.update_user(self.admin,self.buyer,'user','banned')
        self.assertIsNone(db.login('buyer','test-password'))
        with self.assertRaises(PermissionError):payments.list_transactions(self.buyer)
        profiles.update_user(self.admin,self.buyer,'user','active');self.assertIsNotNone(db.login('buyer','test-password'))
        before=payments.get_transaction('TEST-01',self.admin)
        profiles.delete_user(self.admin,self.buyer);self.assertIsNone(db.login('buyer','test-password'))
        self.assertEqual(payments.get_transaction('TEST-01',self.admin),before)
        with self.assertRaises(ValueError):profiles.update_user(self.admin,self.buyer,'user','active')
    def test_cannot_delete_or_ban_self_or_as_customer(self):
        with self.assertRaises(ValueError):profiles.delete_user(self.admin,self.admin)
        with self.assertRaises(ValueError):profiles.update_user(self.admin,self.admin,'admin','banned')
        with self.assertRaises(PermissionError):profiles.delete_user(self.buyer,self.other)
        with self.assertRaises(PermissionError):profiles.update_user(self.buyer,self.other,'user','banned')
    def test_duplicate_renamed_image_rejected_and_rolled_back(self):
        self.submit();renamed=self.base/'renamed.png';renamed.write_bytes(self.slip.read_bytes())
        with self.assertRaisesRegex(ValueError,'รายการอื่น'):payments.submit('DUPLICATE',self.other,self.fresh(),renamed)
        self.assertEqual(len(list((self.base/'EXORA_assets/slips').iterdir())),1)
        self.assertEqual(len(payments.list_transactions(self.admin)),1)
    def test_image_same_pixels_different_metadata_rejected(self):
        self.submit();metadata=PngImagePlugin.PngInfo();metadata.add_text('note','different file metadata')
        changed=self.base/'metadata.png'
        with Image.open(self.slip) as image:image.save(changed,pnginfo=metadata)
        self.assertNotEqual(changed.read_bytes(),self.slip.read_bytes())
        with self.assertRaisesRegex(ValueError,'รายการอื่น'):payments.submit('DUP',self.other,self.fresh(),changed)
    def test_different_image_allowed_but_duplicate_resubmission_blocked(self):
        self.submit();new=self.base/'different.png';Image.new('RGB',(300,400),'green').save(new)
        payments.submit('OTHER',self.other,self.fresh(),new)
        payments.review('TEST-01',self.admin,'rejected','ยอดผิด')
        with self.assertRaisesRegex(ValueError,'รายการอื่น'):payments.replace_slip('TEST-01',self.buyer,new)
        self.assertEqual(payments.get_transaction('TEST-01',self.admin)['payment_status'],'rejected')
        payments.replace_slip('TEST-01',self.buyer,self.slip)
        self.assertEqual(payments.get_transaction('TEST-01',self.admin)['payment_status'],'pending')
    def test_old_slips_are_indexed_without_changing_transactions(self):
        self.submit();conn=db.getconnect();conn.execute('DELETE FROM slip_fingerprints');conn.commit();conn.close()
        before=payments.get_transaction('TEST-01',self.admin)
        with self.assertRaisesRegex(ValueError,'รายการอื่น'):payments.submit('OLD-DUP',self.other,self.fresh(),self.slip)
        self.assertEqual(payments.get_transaction('TEST-01',self.admin),before)

if __name__=='__main__':unittest.main()
