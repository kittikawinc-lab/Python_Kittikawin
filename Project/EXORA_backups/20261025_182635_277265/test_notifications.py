import unittest,os
from unittest.mock import patch
from PIL import Image
import test_exora as fixtures
import EXORA_database as db
import EXORA_payments as payments
import EXORA_notifications as notifications

class NotificationTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    submit=fixtures.WorkflowTests.submit
    def rows(self):
        conn=db.getconnect()
        try:return conn.execute('SELECT status,attempts FROM admin_alerts ORDER BY event_id').fetchall()
        finally:conn.close()
    def test_atomic_event_and_authorized_counts(self):
        self.submit();self.assertEqual(self.rows(),[('pending',0)])
        self.assertEqual(notifications.pending(self.admin),1);self.assertEqual(notifications.pending(self.buyer),1);self.assertEqual(notifications.pending(self.other),0)
        with self.assertRaises(PermissionError):notifications.failures(self.buyer)
        with self.assertRaises(PermissionError):notifications.retry(self.buyer)
        with self.assertRaises(ValueError):self.submit('REPLAY')
        self.assertEqual(len(self.rows()),1)
    def test_admin_email_target_and_deduplication(self):
        self.submit()
        with patch.dict(os.environ,{'EXORA_GMAIL_APP_PASSWORD':'test-only'}),patch('EXORA_notifications.smtplib.SMTP_SSL') as smtp:
            notifications.process_one();notifications.process_one()
            sender=smtp.return_value.__enter__.return_value.send_message;sender.assert_called_once()
            msg=sender.call_args.args[0];self.assertEqual(msg['From'],'exoraadmin@gmail.com');self.assertEqual(msg['To'],'exoraadmin@gmail.com')
            self.assertIn('TEST-01',msg['Subject']);self.assertEqual(list(msg.iter_attachments()),[])
        self.assertEqual(self.rows(),[('sent',1)])
    def test_failed_mail_keeps_transaction_and_can_retry(self):
        self.submit()
        with patch('EXORA_notifications.send',side_effect=OSError('offline')):notifications.process_one()
        self.assertEqual(payments.get_transaction('TEST-01',self.admin)['payment_status'],'pending')
        self.assertEqual(notifications.failures(self.admin),1)
        notifications.retry(self.admin)
        with patch('EXORA_notifications.send') as send:notifications.process_one();send.assert_called_once()
        self.assertEqual(self.rows(),[('sent',1)])
    def test_resubmission_new_alert_and_closed_item_skipped(self):
        self.submit();payments.review('TEST-01',self.admin,'rejected','bad proof')
        with patch('EXORA_notifications.send') as send:notifications.process_one();send.assert_not_called()
        self.assertEqual(self.rows()[0][0],'obsolete')
        image=self.base/'new.png';Image.new('RGB',(200,200),'blue').save(image);payments.replace_slip('TEST-01',self.buyer,image)
        self.assertEqual(self.rows(),[('obsolete',0),('pending',0)])
        with patch('EXORA_notifications.send') as send:notifications.process_one();send.assert_called_once()
    def test_migration_does_not_email_old_pending_records(self):
        self.submit();conn=db.getconnect();conn.execute('DELETE FROM admin_alerts');notifications.migrate(conn);conn.commit();conn.close()
        self.assertEqual(self.rows(),[]);self.assertEqual(notifications.pending(self.admin),1)

if __name__=='__main__':unittest.main()
