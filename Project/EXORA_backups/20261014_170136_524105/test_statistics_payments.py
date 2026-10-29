import unittest
from decimal import Decimal
import test_exora as fixtures
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_payments as payments
import EXORA_statistics as stats
import EXORA_receipts as receipts
import EXORA_banks as banks

class StatisticsPaymentTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    submit=fixtures.WorkflowTests.submit
    def cash(self,number,user,source='USD',amount=100):
        data={**profiles.quote(source,'THB',amount),'customer_name':'Test','customer_phone':'0812345678','payment_method':'in_store'}
        payments.submit(number,user,data,None);return data
    def test_registration_stores_phone_atomically(self):
        ok,message=db.register_user('newbuyer','new@example.com','password123','0812345678');self.assertTrue(ok,message)
        user=db.login('newbuyer','password123');self.assertEqual(profiles.get_profile(user['id'])['phone'],'0812345678')
        for index,phone in enumerate(('','+++++++','123','()()()()')):
            ok,_=db.register_user('bad'+str(index),'bad'+str(index)+'@example.com','password123',phone);self.assertFalse(ok)
    def test_payment_phone_taken_from_registered_profile(self):
        conn=db.getconnect();conn.execute('UPDATE users SET phone=? WHERE id=?',('0899999999',self.buyer));conn.commit();conn.close()
        self.submit();self.assertEqual(payments.get_transaction('TEST-01',self.admin)['customer_phone'],'0899999999')
    def test_foreign_cash_can_be_reviewed_without_fake_slip(self):
        self.cash('CASH',self.buyer);row=payments.get_transaction('CASH',self.admin);self.assertIsNone(row['slip_path'])
        payments.review('CASH',self.admin,'approved','ตรวจรับเงินต่างประเทศที่ร้านแล้ว')
        self.assertEqual(payments.get_transaction('CASH',self.admin)['payment_status'],'approved')
        pdf=receipts.ensure_receipt('CASH',self.admin)
        from pypdf import PdfReader
        self.assertIn('Foreign currency handed over at store',' '.join(page.extract_text() for page in PdfReader(pdf).pages))
    def test_card_disabled_and_wrong_cash_direction_rejected(self):
        with self.assertRaisesRegex(ValueError,'ยังไม่เปิด'):payments.validate_payment({**self.data,'payment_method':'card'})
        with self.assertRaises(ValueError):payments.validate_payment({**self.data,'payment_method':'in_store'})
    def test_stats_ranking_status_and_currency_units(self):
        self.submit();payments.review('TEST-01',self.admin,'approved','verified')
        self.cash('USD',self.buyer);payments.review('USD',self.admin,'approved','received')
        self.cash('EUR',self.other,'EUR');payments.review('EUR',self.admin,'approved','received')
        self.cash('PENDING',self.other,'EUR')
        report=stats.report(self.admin)
        self.assertEqual(report['count'],3);self.assertEqual(report['thb'],Decimal('10700.0'))
        self.assertEqual(report['users'][0]['id'],self.buyer);self.assertEqual(report['users'][0]['count'],2)
        self.assertEqual(report['currencies'][0]['code'],'USD')
        self.assertEqual(report['currencies'][0]['received'],Decimal('100.0'));self.assertEqual(report['currencies'][0]['paid'],Decimal('100.0'))
        self.assertEqual(report['states']['pending'],1)
        with self.assertRaises(PermissionError):stats.report(self.buyer)
    def test_daily_dates_zero_days_and_old_unknown_amount(self):
        db.save_transaction('LEGACY',self.buyer,'BUY','USD',100,'EUR',85,.85,'Test','0812345678')
        conn=db.getconnect();conn.execute("UPDATE transactions SET transaction_date='2026-10-10 12:00:00' WHERE transaction_no='LEGACY'");conn.commit();conn.close()
        report=stats.report(self.admin,'2026-10-09','2026-10-11','legacy')
        self.assertEqual(report['count'],1);self.assertEqual(report['unknown'],1);self.assertEqual(report['thb'],0)
        self.assertEqual(len(report['daily']),3);self.assertEqual(report['daily'][0]['count'],0)
        with self.assertRaises(ValueError):stats.report(self.admin,'2026-10-11','2026-10-09')
    def test_old_cross_currency_not_repriced_and_new_value_frozen(self):
        quote={**profiles.quote('USD','EUR',100),'customer_name':'Test','customer_phone':'0812345678','payment_method':'in_store'}
        payments.submit('CROSS',self.buyer,quote,None);payments.review('CROSS',self.admin,'approved','received')
        before=stats.report(self.admin)['thb'];profiles.set_rate(self.admin,'USD','USD',10,11)
        self.assertEqual(stats.report(self.admin)['thb'],before);self.assertEqual(before,Decimal('3400.0'))
    def test_bank_badge_matches_existing_full_name(self):
        self.assertEqual(banks.lookup('ธนาคารกรุงไทย')[0],'KTB');self.assertEqual(banks.lookup('ธนาคารไทยพาณิชย์')[0],'SCB')
        self.assertEqual(banks.lookup('Unknown')[0],'OTHER')

if __name__=='__main__':unittest.main()
