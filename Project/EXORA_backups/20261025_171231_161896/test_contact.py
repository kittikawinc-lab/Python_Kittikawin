import unittest
import test_exora as fixtures
import EXORA_contact as contact
import EXORA_profiles as profiles
import EXORA_email_settings as email_settings

class ContactTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    def test_save_contact_preserves_other_settings_and_sender(self):
        before=profiles.shop();sender=email_settings.SENDER
        contact.save(self.admin,{'phone':'0812345678','contact_email':'store@example.com','contact_map':'https://maps.google.com/','contact_line':'@exora'})
        after=profiles.shop();self.assertEqual(after['contact_email'],'store@example.com')
        for key,value in before.items():
            if key not in dict(contact.FIELDS):self.assertEqual(after[key],value)
        self.assertEqual(email_settings.SENDER,sender)
    def test_customer_cannot_edit_contact(self):
        with self.assertRaises(PermissionError):contact.save(self.buyer,{})
    def test_invalid_email_and_links_rejected_without_changes(self):
        before=profiles.shop()
        for values in ({'contact_email':'bad'},{'contact_map':'file:///C:/private'},{'contact_website':'javascript:alert(1)'},{'contact_website':'https://user:password@example.com'},{'contact_note':'x'*501}):
            with self.assertRaises(ValueError):contact.save(self.admin,values)
            self.assertEqual(profiles.shop(),before)
    def test_empty_optional_fields_can_be_cleared(self):
        contact.save(self.admin,{'contact_line':'@exora'});contact.save(self.admin,{})
        self.assertEqual(profiles.shop()['contact_line'],'')

if __name__=='__main__':unittest.main()
