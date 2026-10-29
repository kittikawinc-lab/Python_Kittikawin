import unittest
from types import SimpleNamespace
import EXORA_layout as layout

class Canvas:
    def __init__(self):self.callbacks={};self.bindings={};self.pos=None;self.count=0
    def bind(self,name,fn,add=None):self.bindings[name]=fn
    def winfo_width(self):return 1672
    def coords(self,item,*coords):self.pos=coords
    def after(self,ms,fn):self.count+=1;key=str(self.count);self.callbacks[key]=fn;return key
    def after_cancel(self,key):self.callbacks.pop(key,None)
    def run(self):
        key=next(iter(self.callbacks));fn=self.callbacks.pop(key);fn()

class LayoutTests(unittest.TestCase):
    def test_fixed_pixels_do_not_double_scale(self):
        self.assertEqual(layout.font(11)[1],-15)
        self.assertEqual(layout.font(26,True)[2],'bold')
    def test_fhd_dialog_fits_and_centers(self):
        w,h,x,y=layout.dialog_geometry(1920,1080,0,30,1920,1010,900,850)
        self.assertEqual((w,h,x),(900,850,510));self.assertLessEqual(y+h,1030)
    def test_large_dialog_clamped_on_small_display(self):
        w,h,x,y=layout.dialog_geometry(1366,768,0,30,1366,700,1600,1000)
        self.assertLessEqual(w,1286);self.assertLessEqual(h,658);self.assertGreaterEqual(x,0);self.assertGreaterEqual(y,0)
    def test_page_transition_finishes_without_offset(self):
        canvas=Canvas();transition=layout.PageTransition(canvas,1,lambda:True);transition.start()
        while canvas.callbacks:canvas.run()
        self.assertEqual(canvas.pos,(0.0,0.0));self.assertIsNone(transition.timer)
    def test_rapid_navigation_cancels_previous_callback(self):
        canvas=Canvas();transition=layout.PageTransition(canvas,1,lambda:True);transition.start();old=transition.timer
        transition.start();self.assertNotIn(old,canvas.callbacks);self.assertEqual(len(canvas.callbacks),1)
        canvas.bindings['<Destroy>'](SimpleNamespace(widget=canvas));self.assertFalse(canvas.callbacks)
    def test_disabled_motion_has_no_timer(self):
        canvas=Canvas();layout.PageTransition(canvas,1,lambda:False).start()
        self.assertEqual(canvas.pos,(0,0));self.assertFalse(canvas.callbacks)

if __name__=='__main__':unittest.main(verbosity=2)
