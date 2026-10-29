import unittest
from decimal import Decimal
import test_exora as fixtures
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_currency_cards as cards

class CurrencyCardTests(unittest.TestCase):
    setUp=fixtures.WorkflowTests.setUp
    tearDown=fixtures.WorkflowTests.tearDown

    def usd(self,actor=None):
        return next(row for row in cards.listing(actor or self.buyer) if row['code']=='USD')

    def test_favorites_persist_isolated_and_idempotent(self):
        cards.favorite(self.buyer,'USD',True);cards.favorite(self.buyer,'USD',True)
        self.assertTrue(self.usd()['favorite']);self.assertFalse(self.usd(self.other)['favorite'])
        cards.favorite(self.buyer,'USD',False);self.assertFalse(self.usd()['favorite'])
        with self.assertRaises(ValueError):cards.favorite(self.buyer,'THB',True)
        with self.assertRaises(ValueError):cards.favorite(self.buyer,"USD'",True)

    def test_blocked_account_cannot_access_favorites(self):
        conn=db.getconnect();conn.execute("UPDATE users SET status='banned' WHERE id=?",(self.buyer,));conn.commit();conn.close()
        with self.assertRaises(PermissionError):cards.listing(self.buyer)
        with self.assertRaises(PermissionError):cards.favorite(self.buyer,'USD',True)

    def test_migration_repeat_preserves_favorites(self):
        cards.favorite(self.buyer,'USD',True);conn=db.getconnect();cards.migrate(conn);cards.migrate(conn);conn.commit();conn.close()
        self.assertTrue(self.usd()['favorite'])

if __name__=='__main__':unittest.main()
