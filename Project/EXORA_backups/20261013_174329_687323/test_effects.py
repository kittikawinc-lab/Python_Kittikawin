import unittest
from types import SimpleNamespace
import EXORA_effects as effects

class Widget:
    def __init__(self):self.values={'background':'#125b4a','text':''};self.bindings={};self.pending={};self.sequence=0
    def cget(self,key):return self.values[key]
    def configure(self,**values):self.values.update(values)
    def bind(self,event,callback,add=None):self.bindings[event]=callback
    def after(self,ms,callback):self.sequence+=1;key=str(self.sequence);self.pending[key]=callback;return key
    def after_cancel(self,key):self.pending.pop(key,None)
    def tick(self):key=next(iter(self.pending));fn=self.pending.pop(key);fn()

class EffectTests(unittest.TestCase):
    def test_color_blend_endpoints(self):
        self.assertEqual(effects.mix('#000000','#ffffff',0),'#000000')
        self.assertEqual(effects.mix('#000000','#ffffff',1),'#ffffff')
    def test_hover_finishes_at_requested_color(self):
        widget=Widget();effects.color_to(widget,'background','#ffffff',lambda:True)
        while widget.pending:widget.tick()
        self.assertEqual(widget.values['background'],'#ffffff')
    def test_disabling_motion_updates_without_timer(self):
        widget=Widget();effects.color_to(widget,'background','#ffffff',lambda:False)
        self.assertEqual(widget.values['background'],'#ffffff');self.assertFalse(widget.pending)
    def test_number_reveal_never_changes_final_amount(self):
        widget=Widget();effects.number_reveal(widget,1234.56,lambda value:f'{value:.2f}',lambda:True)
        while widget.pending:widget.tick()
        self.assertEqual(widget.values['text'],'1234.56')
    def test_new_value_and_destroy_cancel_old_animation(self):
        widget=Widget();effects.number_reveal(widget,100,lambda value:str(value),lambda:True)
        old=next(iter(widget.pending));effects.number_reveal(widget,500,lambda value:str(value),lambda:True)
        self.assertNotIn(old,widget.pending)
        widget.bindings['<Destroy>'](SimpleNamespace(widget=widget));self.assertFalse(widget.pending)

if __name__=='__main__':unittest.main(verbosity=2)
