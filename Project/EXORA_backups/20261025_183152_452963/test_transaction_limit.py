import unittest,json,time
from decimal import Decimal
import EXORA_security as security
import EXORA_profiles as profiles
import EXORA_bank_flow as flow
import EXORA_database as db
import EXORA_payments as payments
import test_exora as fixtures
class TransactionLimitTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown
    def test_boundary_and_invalid_values(self):
        self.assertEqual(security.validate_transaction_amount('1000'),Decimal('1000.00'))
        self.assertEqual(security.validate_transaction_amount('0.01'),Decimal('0.01'))
        for value in ('1000.001',1001,-1,'-0','0','0.00001','NaN','sNaN','Infinity','-Infinity',float('nan'),float('inf'),'1e3','1e999999','1_000','1,000',True,None,'9'*10000,'١٠٠'):
            with self.subTest(value=str(value)[:30]),self.assertRaises(ValueError):security.validate_transaction_amount(value)
    def test_create_and_quote_reject_without_writes(self):
        for value in ('1000.01','-1','NaN','1e9'):
            with self.assertRaises(ValueError):flow.create(self.buyer,'Buyer','Bank','123456789','Thailand','THB','USD',value)
            with self.assertRaises(ValueError):profiles.quote('THB','USD',value,self.buyer)
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT COUNT(*) FROM bank_flow').fetchone()[0],0);conn.close()
        self.assertEqual(profiles.quote('THB','USD','1000',self.buyer)['from_amount'],1000)
        self.assertGreater(profiles.quote('USD','THB','100',self.buyer)['to_amount'],1000)
    def test_old_quote_over_limit_cannot_be_consumed(self):
        conn=db.getconnect();security.migrate(conn)
        payload={'from_currency':'THB','to_currency':'USD','from_amount':1001,'to_amount':28.6,'exchange_rate':1/35,'thb_value':1001,'transaction_type':'SELL'}
        conn.execute('INSERT INTO secure_quotes VALUES (?,?,?,?,NULL)',('oldquote',self.buyer,json.dumps(payload),time.time()+600));conn.commit()
        with self.assertRaises(ValueError):security.consume_quote(conn,self.buyer,'BYPASS',{**payload,'quote_id':'oldquote'})
        self.assertIsNone(conn.execute('SELECT used_transaction FROM secure_quotes WHERE id=?',('oldquote',)).fetchone()[0]);conn.close()
    def test_tampered_payment_and_legacy_write_rejected(self):
        with self.assertRaises(ValueError):payments.submit('BAD',self.buyer,{**self.data,'from_amount':1001},self.slip)
        with self.assertRaises(ValueError):db.save_transaction('BAD',self.buyer,'SELL','THB',1001,'USD',30,1/35,'Buyer','')
        self.assertEqual(payments.list_transactions(self.buyer),[])
