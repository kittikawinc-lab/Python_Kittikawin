import unittest
from types import SimpleNamespace
import EXORA_effects as effects
from PIL import Image

class Widget:
    def __init__(self):self.values={'background':'#125b4a','text':''};self.bindings={};self.pending={};self.sequence=0
    def cget(self,key):return self.values[key]
    def configure(self,**values):self.values.update(values)
    def bind(self,event,callback,add=None):self.bindings[event]=callback
    def after(self,ms,callback):self.sequence+=1;key=str(self.sequence);self.pending[key]=callback;return key
    def after_cancel(self,key):self.pending.pop(key,None)
    def tick(self):key=next(iter(self.pending));fn=self.pending.pop(key);fn()

class EffectTests(unittest.TestCase):
    def test_page_accent_finishes_and_rapid_restart_cancels(self):
        widget=Widget();widget.items={};widget.counter=0
        def create(*args,**kwargs):widget.counter+=1;widget.items[widget.counter]=kwargs;return widget.counter
        widget.create_rectangle=create;widget.delete=lambda tag:widget.items.clear()
        widget.winfo_width=lambda:1000;widget.coords=lambda *args:None
        widget.itemconfigure=lambda ident,**values:widget.items[ident].update(values)
        effects.page_reveal(widget,lambda:True);widget.tick();effects.page_reveal(widget,lambda:True)
        self.assertEqual(len(widget.pending),1)
        while widget.pending:widget.tick()
        self.assertFalse(widget.items)
    def test_news_fade_destroy_cancels_frames(self):
        widget=Widget();effects.image_fade(widget,None,Image.new('RGB',(20,20),'red'),lambda frame:None,lambda:True)
        widget.bindings['<Destroy>'](SimpleNamespace(widget=widget));self.assertFalse(widget.pending)
    def test_news_fade_final_image_and_replacement_cancel(self):
        widget=Widget();frames=[];red=Image.new('RGB',(20,20),'red');green=Image.new('RGB',(20,20),'green')
        effects.image_fade(widget,None,red,frames.append,lambda:True)
        widget.tick();effects.image_fade(widget,frames[-1],green,frames.append,lambda:True)
        self.assertEqual(len(widget.pending),1)
        while widget.pending:widget.tick()
        self.assertEqual(frames[-1].tobytes(),green.tobytes())
    def test_news_reduced_motion_has_no_timer(self):
        widget=Widget();frames=[];image=Image.new('RGB',(20,20),'red')
        effects.image_fade(widget,None,image,frames.append,lambda:False)
        self.assertFalse(widget.pending);self.assertEqual(frames[-1].tobytes(),image.tobytes())
    def test_press_release_retains_selected_navigation(self):
        widget=Widget();widget.values['state']='normal';widget.values['pady']=10;widget.selected=True
        effects.button_feedback(widget,'#125b4a',lambda:True)
        widget.bindings['<ButtonPress-1>'](None)
        while widget.pending:widget.tick()
        self.assertEqual(widget.cget('relief'),'sunken')
        widget.bindings['<ButtonRelease-1>'](None)
        while widget.pending:widget.tick()
        self.assertEqual(widget.cget('background'),'#24725f');self.assertEqual(widget.cget('relief'),'flat')
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
