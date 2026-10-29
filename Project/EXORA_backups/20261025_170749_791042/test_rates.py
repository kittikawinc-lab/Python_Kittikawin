import os, tempfile, unittest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import json
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_rates as rates

class RateTests(unittest.TestCase):
    def setUp(self):
        self.environment=patch.dict(os.environ,{'EXORA_TWELVE_DATA_API_KEY':''});self.environment.start()
        self.temp=tempfile.TemporaryDirectory(dir=os.getenv('EXORA_TEST_TEMP'))
        self.old=(db.BASE_DIR,db.DB_PATH);db.BASE_DIR=self.temp.name;db.DB_PATH=self.temp.name+'/EXORA.db';db.createdb()
        self.admin=db.login('admin','admin123')['id']
        profiles.set_rate(self.admin,'USD','US Dollar',34,35)
        self.response={'success':True,'rates':{r[1]:.025 for r in db.getcurs() if r[1]!='THB'},'date':date.today().isoformat()}
    def tearDown(self):
        db.BASE_DIR,db.DB_PATH=self.old;self.temp.cleanup();self.environment.stop()
    def refresh(self):
        with patch('EXORA_rates.getexr',return_value=self.response):return rates.refresh()
    def test_default_only_reference_changes(self):
        before=db.getcurs();self.assertTrue(self.refresh()['ok']);self.assertEqual(db.getcurs(),before)
        self.assertEqual(rates.snapshot()['USD']['mid'],40)
    def test_opt_in_applies_spread_preserves_transactions(self):
        db.save_transaction('OLD',self.admin,'SELL','THB',3500,'USD',100,1/35,'Test','')
        conn=db.getconnect();before=conn.execute('SELECT * FROM transactions').fetchall();conn.close()
        rates.settings(self.admin,True,2);self.assertTrue(self.refresh()['ok'])
        row=db.getcur('USD');self.assertAlmostEqual(row[3],39.2);self.assertAlmostEqual(row[4],40.8)
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT * FROM transactions').fetchall(),before);conn.close()
    def test_failure_keeps_cached_rates_and_shop(self):
        self.refresh();before=rates.snapshot();shop=db.getcurs();self.response={'success':False}
        self.assertFalse(self.refresh()['ok']);self.assertEqual(rates.snapshot(),before);self.assertEqual(db.getcurs(),shop)
    def test_invalid_partial_stale_do_not_write(self):
        for value in (0,-1,float('nan'),float('inf')):
            self.response['rates']['USD']=value;self.assertFalse(self.refresh()['ok']);self.assertEqual(rates.snapshot(),{})
        self.response['rates']['USD']=.025;self.response['date']=(date.today()-timedelta(days=8)).isoformat()
        self.assertFalse(self.refresh()['ok'])
        self.response['date']=date.today().isoformat();del self.response['rates']['USD'];self.assertFalse(self.refresh()['ok'])
    def test_permission_and_spread(self):
        db.adduser('buyer','password','user');uid=db.login('buyer','password')['id']
        with self.assertRaises(PermissionError):rates.settings(uid,True,2)
        for value in (-1,21,'nan','inf'):
            with self.assertRaises(ValueError):rates.settings(self.admin,True,value)
    def test_turn_off_retains_shop_prices(self):
        rates.settings(self.admin,True,2);self.refresh();before=db.getcurs()
        rates.settings(self.admin,False,2);self.response['rates']['USD']=.02;self.refresh()
        self.assertEqual(db.getcurs(),before);self.assertEqual(rates.snapshot()['USD']['mid'],50)

    def test_live_response_pair_and_timestamp(self):
        from datetime import datetime, timezone
        reply=MagicMock();reply.__enter__.return_value=reply
        data={'symbol':'USD/THB','rate':40,'timestamp':datetime.now(timezone.utc).timestamp()}
        reply.read.return_value=json.dumps(data).encode()
        with patch('EXORA_rates.urllib.request.urlopen',return_value=reply):
            result=rates.fetch_live(['USD']);self.assertTrue(result['success']);self.assertEqual(result['rates']['USD'],.025)
            data['symbol']='THB/USD';reply.read.return_value=json.dumps(data).encode()
            self.assertFalse(rates.fetch_live(['USD'])['success'])
            data['symbol']='USD/THB';data['timestamp']-=3600;reply.read.return_value=json.dumps(data).encode()
            self.assertFalse(rates.fetch_live(['USD'])['success'])

    def test_live_failure_never_exposes_key_or_uses_daily(self):
        with patch.dict(os.environ,{'EXORA_TWELVE_DATA_API_KEY':'SECRET'}),patch('EXORA_rates.urllib.request.urlopen',side_effect=Exception('URL contains SECRET')),patch('EXORA_rates.getexr') as daily:
            result=rates.refresh();self.assertFalse(result['ok']);self.assertNotIn('SECRET',str(result));daily.assert_not_called()

    def test_live_interval_bounds(self):
        with patch.dict(os.environ,{'EXORA_TWELVE_DATA_API_KEY':'test','EXORA_RATE_REFRESH_SECONDS':'1'}):self.assertEqual(rates.interval_ms(),60000)
        with patch.dict(os.environ,{'EXORA_TWELVE_DATA_API_KEY':'test','EXORA_RATE_REFRESH_SECONDS':'invalid'}):self.assertEqual(rates.interval_ms(),300000)

if __name__=='__main__':unittest.main()
