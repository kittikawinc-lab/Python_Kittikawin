import unittest
from types import SimpleNamespace
from test_effects import Widget
from EXORA_motion import MotionScene,button_spring

class Canvas(Widget):
    def __init__(self):super().__init__();self.positions={};self.number=0
    def create_oval(self,*args,**kwargs):self.number+=1;return self.number
    create_polygon=create_oval
    create_line=create_oval
    def winfo_width(self):return 800
    def winfo_height(self):return 500
    def coords(self,item,*values):self.positions[item]=values
    def tag_raise(self,tag):pass

class MotionTests(unittest.TestCase):
    def test_each_vehicle_theme_draws_and_cancels(self):
        for theme in ('plane','car','train','boat'):
            canvas=Canvas();scene=MotionScene(canvas,lambda:True,theme=theme)
            self.assertEqual(scene.theme,theme);self.assertTrue(scene.parts)
            self.assertTrue(all(item in canvas.positions for item,points in scene.parts))
            scene.destroy(SimpleNamespace(widget=canvas));self.assertFalse(canvas.pending)
    def test_scene_destroy_stops_timer(self):
        canvas=Canvas();scene=MotionScene(canvas,lambda:True,True)
        self.assertEqual(len(canvas.pending),1);canvas.tick();self.assertEqual(len(canvas.pending),1)
        canvas.bindings['<Destroy>'](SimpleNamespace(widget=canvas));self.assertFalse(canvas.pending);self.assertTrue(scene.closed)
    def test_motion_disabled_restores_login_position(self):
        canvas=Canvas();scene=MotionScene(canvas,lambda:False,True)
        self.assertEqual(canvas.positions['travel-image'],(0,0));before=dict(canvas.positions);canvas.tick();self.assertEqual(canvas.positions,before)
    def test_button_rapid_click_restores_original_padding(self):
        widget=Widget();widget.values['pady']=11;button_spring(widget,lambda:True);widget.tick();button_spring(widget,lambda:True)
        self.assertEqual(len(widget.pending),1)
        while widget.pending:widget.tick()
        self.assertEqual(widget.cget('pady'),11)
    def test_spring_reduced_motion_no_timer(self):
        widget=Widget();widget.values['pady']=11;button_spring(widget,lambda:False)
        self.assertFalse(widget.pending);self.assertEqual(widget.cget('pady'),11)

if __name__=='__main__':unittest.main()
