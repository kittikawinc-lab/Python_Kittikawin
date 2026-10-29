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

    def test_previous_prices_survive_same_rate_refresh(self):
        old=self.usd();profiles.set_rate(self.admin,'USD','US Dollar',33,36)
        row=self.usd();self.assertEqual(row['previous_buy'],old['buy']);self.assertEqual(row['previous_sell'],old['sell'])
        profiles.set_rate(self.admin,'USD','US Dollar',33,36);self.assertEqual(self.usd(),row)
        profiles.set_rate(self.admin,'USD','US Dollar',32,37)
        self.assertEqual(self.usd()['previous_buy'],33);self.assertEqual(self.usd()['previous_sell'],36)

    def test_movement_up_down_flat_and_missing(self):
        self.assertIn('▲ +1.0000 (+10.00%)',cards.movement(11,10)[0])
        self.assertIn('▼ -1.0000 (-10.00%)',cards.movement(9,10)[0])
        self.assertIn('คงที่',cards.movement(10,10)[0])
        for previous in (None,0):self.assertIn('ไม่มีฐาน',cards.movement(10,previous)[0])

    def test_migration_repeat_preserves_favorites(self):
        cards.favorite(self.buyer,'USD',True);conn=db.getconnect();cards.migrate(conn);cards.migrate(conn);conn.commit();conn.close()
        self.assertTrue(self.usd()['favorite'])

if __name__=='__main__':unittest.main()
