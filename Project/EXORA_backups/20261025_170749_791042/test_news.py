import os,tempfile,unittest
from pathlib import Path
from PIL import Image
import EXORA_database as db
import EXORA_news as news

class Scheduler:
    def __init__(self):self.tasks={};self.number=0
    def after(self,delay,fn):self.number+=1;self.tasks[self.number]=fn;return self.number
    def after_cancel(self,key):self.tasks.pop(key,None)
    def tick(self):fn=self.tasks.pop(next(iter(self.tasks)));fn()

class NewsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=os.getenv('EXORA_TEST_TEMP'));self.base=Path(self.temp.name)
        self.old=db.BASE_DIR,db.DB_PATH;db.BASE_DIR=str(self.base);db.DB_PATH=str(self.base/'EXORA.db');db.createdb()
        self.admin=db.login('admin','admin123')['id'];db.adduser('reader','password','user');self.reader=db.login('reader','password')['id']
        self.image=self.base/'news.png';Image.new('RGBA',(800,450),(0,120,80,128)).save(self.image)
    def tearDown(self):db.BASE_DIR,db.DB_PATH=self.old;self.temp.cleanup()
    def test_news_saved_as_managed_image_survives_migration(self):
        news.add(self.admin,'Finance',self.image);self.image.unlink();db.createdb()
        row=news.slides()[0];self.assertTrue(news.image_path(row['image_path']).is_file())
        with Image.open(news.image_path(row['image_path'])) as image:self.assertEqual(image.size,(800,450));self.assertEqual(image.mode,'RGB')
    def test_user_cannot_add_or_manage(self):
        with self.assertRaises(PermissionError):news.add(self.reader,'Finance',self.image)
        ident=news.add(self.admin,'Finance',self.image)
        with self.assertRaises(PermissionError):news.manage(self.reader,ident,'delete')
        self.assertEqual(len(news.slides()),1)

    def test_news_links_and_old_news_migration(self):
        old=news.add(self.admin,'Old news',self.image)
        self.assertEqual(news.slides()[0]['url'],'')
        news.set_url(self.admin,old,'https://example.com/news?id=1');db.createdb()
        self.assertEqual(news.slides()[0]['url'],'https://example.com/news?id=1')
        with self.assertRaises(PermissionError):news.set_url(self.reader,old,'https://example.com')
        news.set_url(self.admin,old,'');self.assertEqual(news.slides()[0]['url'],'')
        with self.assertRaises(ValueError):news.set_url(self.admin,9999,'https://example.com')

    def test_unsafe_news_links_rejected(self):
        for url in ('javascript:alert(1)','file:///C:/test','https://user:password@example.com','https://','https://example.com:abc','https://example.com/with space'):
            with self.assertRaises(ValueError):news.add(self.admin,'Bad link',self.image,url)
        self.assertEqual(news.slides(),[])
        ident=news.add(self.admin,'Valid',self.image,'https://example.com/news')
        self.assertEqual(news.slides()[0]['id'],ident)
    def test_order_hide_and_delete_preserve_history(self):
        db.save_transaction('KEEP',self.reader,'SELL','THB',3500,'USD',100,1/35,'Test','')
        conn=db.getconnect();before=conn.execute('SELECT * FROM transactions').fetchall();conn.close()
        a=news.add(self.admin,'A',self.image);b=news.add(self.admin,'B',self.image)
        news.manage(self.admin,b,'up');self.assertEqual([r['id'] for r in news.slides()],[b,a])
        news.manage(self.admin,b,'toggle');self.assertEqual([r['id'] for r in news.slides()],[a]);self.assertEqual(len(news.slides(True)),2)
        news.manage(self.admin,b,'toggle');news.manage(self.admin,b,'down');self.assertEqual([r['id'] for r in news.slides()],[a,b])
        news.manage(self.admin,a,'delete');self.assertEqual([r['id'] for r in news.slides()],[b])
        conn=db.getconnect();self.assertEqual(conn.execute('SELECT * FROM transactions').fetchall(),before);conn.close()
    def test_invalid_file_title_and_path_are_rejected(self):
        fake=self.base/'fake.png';fake.write_text('not an image')
        with self.assertRaises(OSError):news.add(self.admin,'Bad',fake)
        for title in ('','x'*121):
            with self.assertRaises(ValueError):news.add(self.admin,title,self.image)
        with self.assertRaises(ValueError):news.image_path('../outside.jpg')
        self.assertEqual(news.slides(),[])

class PlaybackTests(unittest.TestCase):
    def test_loop_wraps_single_timer_manual_move_and_pause(self):
        scheduler=Scheduler();frames=[];player=news.AutoPlayer(scheduler,3,frames.append)
        player.start();player.start();self.assertEqual(len(scheduler.tasks),1)
        scheduler.tick();self.assertEqual(frames[-1],1);scheduler.tick();scheduler.tick();self.assertEqual(frames[-1],0)
        player.move(-1);self.assertEqual(frames[-1],2);self.assertEqual(len(scheduler.tasks),1)
        player.pause();self.assertFalse(scheduler.tasks);player.pause(False);self.assertEqual(len(scheduler.tasks),1)
        player.close();self.assertFalse(scheduler.tasks);player.move(1);self.assertEqual(frames[-1],2)
    def test_zero_or_one_slide_never_schedules(self):
        for count in (0,1):
            scheduler=Scheduler();player=news.AutoPlayer(scheduler,count,lambda index:None);player.start();player.move(1);self.assertFalse(scheduler.tasks)

if __name__=='__main__':unittest.main()
