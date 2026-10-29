"""แปลข้อความหน้าจอโดยคงค่าตัวแปรและข้อมูลธุรกรรมต้นฉบับไว้."""
import tkinter as native
from tkinter import ttk as native_ttk, messagebox as native_messages, filedialog as native_files
import weakref
import re
from types import SimpleNamespace
from EXORA_translations import CATALOG
import EXORA_fonts as typefaces

LANGUAGES={'th':'ไทย','en':'English','zh':'中文'}
language='th'
widgets=weakref.WeakSet()
phrases=sorted(CATALOG,key=len,reverse=True)

# แปลวลีที่ตรงกับพจนานุกรม รวมข้อความที่ประกอบกับจำนวนเงินหรือวันเวลา
def translate(value):
    if language=='th' or not isinstance(value,str):return value
    result=value
    for source in phrases:
        if source in result:
            replacement=CATALOG[source][0 if language=='en' else 1]
            if source.isascii():result=re.sub(r'(?<![\w@./-])'+re.escape(source)+r'(?![\w@./-])',lambda match:replacement,result)
            else:result=result.replace(source,replacement)
    return result

# เปลี่ยนข้อความของ widget ที่ยังอยู่ โดยไม่สร้างหน้าใหม่หรือทำช่องกรอกสูญหาย
def set_language(code):
    global language
    if code not in LANGUAGES:raise ValueError('Unsupported language')
    language=code
    for widget in list(widgets):
        try:
            if widget.winfo_exists():widget.retranslate()
        except native.TclError:pass
    if native._default_root is not None:typefaces.refresh(native._default_root,language)

# เก็บข้อความต้นฉบับสำหรับ Label/Button/Checkbutton เพื่อสลับภาษาได้หลายครั้ง
class TextMixin:
    def __init__(self,master=None,cnf=None,**kwargs):
        options=dict(cnf or {});options.update(kwargs);self.raw_text=options.get('text','');self.base_font=options.get('font')
        if 'text' in options:options['text']=translate(self.raw_text)
        super().__init__(master,**options);widgets.add(self)
    def configure(self,cnf=None,**kwargs):
        if isinstance(cnf,str):return super().configure(cnf)
        options=dict(cnf or {});options.update(kwargs)
        if 'text' in options:self.raw_text=options['text'];options['text']=translate(self.raw_text)
        return super().configure(options) if options else super().configure()
    config=configure
    def retranslate(self):
        options={'text':translate(self.raw_text)}
        if isinstance(self.base_font,(tuple,list)):
            options['font']=((typefaces.family(language) if self.base_font[0] in typefaces.UI_FAMILIES else self.base_font[0]),*self.base_font[1:])
        super().configure(**options)

class Label(TextMixin,native.Label):pass
class Button(TextMixin,native.Button):pass
class Checkbutton(TextMixin,native.Checkbutton):pass
class TCheckbutton(TextMixin,native_ttk.Checkbutton):pass

# หัวข้อหน้าต่างย่อยเปลี่ยนภาษาได้พร้อมหน้าหลัก
class Toplevel(native.Toplevel):
    def __init__(self,*args,**kwargs):self.raw_title='EXORA';super().__init__(*args,**kwargs);widgets.add(self)
    def title(self,value=None):
        if value is None:return super().title()
        self.raw_title=value;return super().title(translate(value))
    wm_title=title
    def retranslate(self):super().title(translate(self.raw_title))

# แสดงคำแปลในตัวเลือก แต่ textvariable ที่โค้ดธุรกิจอ่านยังเป็นค่าต้นฉบับ
class Combobox(native_ttk.Combobox):
    def __init__(self,master=None,**kwargs):
        self.raw_values=tuple(kwargs.pop('values',()))
        original=kwargs.pop('textvariable',None)
        self.semantic=original if isinstance(original,native.Variable) else native.StringVar(master,name=original) if original else native.StringVar(master)
        self.display=native.StringVar(master,value=translate(self.semantic.get()));self.syncing=False
        super().__init__(master,textvariable=self.display,values=[translate(v) for v in self.raw_values],**kwargs)
        self.original_trace=self.semantic.trace_add('write',self.from_original);self.display_trace=self.display.trace_add('write',self.from_display)
        widgets.add(self);self.bind('<Destroy>',self.cleanup,add='+')
    def from_original(self,*args):
        if self.syncing:return
        self.syncing=True
        try:self.display.set(translate(self.semantic.get()))
        finally:self.syncing=False
    def from_display(self,*args):
        if self.syncing:return
        value=self.display.get()
        for original in self.raw_values:
            if translate(original)==value:value=original;break
        self.syncing=True
        try:self.semantic.set(value)
        finally:self.syncing=False
    def configure(self,cnf=None,**kwargs):
        if isinstance(cnf,str):return super().configure(cnf)
        options=dict(cnf or {});options.update(kwargs)
        if 'values' in options:self.raw_values=tuple(options['values']);options['values']=[translate(v) for v in self.raw_values]
        return super().configure(options) if options else super().configure()
    config=configure
    def get(self):return self.semantic.get()
    def set(self,value):self.semantic.set(value)
    def retranslate(self):super().configure(values=[translate(v) for v in self.raw_values]);self.from_original()
    def cleanup(self,event):
        if event.widget is self:
            self.semantic.trace_remove('write',self.original_trace);self.display.trace_remove('write',self.display_trace)

# แปลชื่อหัวตารางและค่าที่แสดง โดย item(...,'values') ยังคงให้ค่าดิบ
class Treeview(native_ttk.Treeview):
    def __init__(self,*args,**kwargs):
        self.raw_headings={};self.raw_rows={};super().__init__(*args,**kwargs);widgets.add(self)
    def heading(self,column,option=None,**kwargs):
        if 'text' in kwargs:self.raw_headings[column]=kwargs['text'];kwargs['text']=translate(kwargs['text'])
        return super().heading(column,option,**kwargs)
    def insert(self,parent,index,iid=None,**kwargs):
        raw=kwargs.get('values',())
        if 'values' in kwargs:kwargs['values']=self.display_values(raw)
        item=super().insert(parent,index,iid,**kwargs);self.raw_rows[item]=tuple(raw);return item
    def item(self,item,option=None,**kwargs):
        if 'values' in kwargs:self.raw_rows[item]=tuple(kwargs['values']);kwargs['values']=self.display_values(kwargs['values'])
        result=super().item(item,option,**kwargs)
        if not kwargs and option=='values' and item in self.raw_rows:return self.raw_rows[item]
        if not kwargs and option is None and item in self.raw_rows:result['values']=self.raw_rows[item]
        return result
    def delete(self,*items):
        for item in items:self.raw_rows.pop(item,None)
        return super().delete(*items)
    def retranslate(self):
        for key,text in self.raw_headings.items():super().heading(key,text=translate(text))
        for item,values in self.raw_rows.items():
            if self.exists(item):super().item(item,values=self.display_values(values))
    # ชื่อผู้ใช้ อีเมล หัวข้อข่าว และข้อมูลที่ผู้ใช้กรอกคงภาษาต้นฉบับไว้
    def display_values(self,values):
        columns=self.cget('columns');preserve={'user','username','email','title','url','name','no','date','id'}
        return [value if index<len(columns) and columns[index] in preserve else translate(value) for index,value in enumerate(values)]

# ชื่อแท็บแปลได้โดยไม่เปลี่ยน widget หรือแท็บที่เลือก
class Notebook(native_ttk.Notebook):
    def __init__(self,*args,**kwargs):self.raw_tabs={};super().__init__(*args,**kwargs);widgets.add(self)
    def add(self,child,**kwargs):
        if 'text' in kwargs:self.raw_tabs[str(child)]=kwargs['text'];kwargs['text']=translate(kwargs['text'])
        return super().add(child,**kwargs)
    def tab(self,tab_id,option=None,**kwargs):
        if 'text' in kwargs:
            key=str(tab_id) if str(tab_id) in self.raw_tabs else self.tabs()[self.index(tab_id)]
            self.raw_tabs[key]=kwargs['text'];kwargs['text']=translate(kwargs['text'])
        return super().tab(tab_id,option,**kwargs)
    def retranslate(self):
        for key,text in self.raw_tabs.items():super().tab(key,text=translate(text))

# แปลข้อความบนกราฟหรือ Canvas โดยเก็บต้นฉบับแยกจากเลข item
class Canvas(native.Canvas):
    def __init__(self,*args,**kwargs):self.raw_items={};super().__init__(*args,**kwargs);widgets.add(self)
    def create_text(self,*args,**kwargs):
        raw=kwargs.get('text','');kwargs['text']=translate(raw);item=super().create_text(*args,**kwargs);self.raw_items[item]=raw;return item
    def delete(self,*args):
        result=super().delete(*args)
        for item in list(self.raw_items):
            if not self.type(item):self.raw_items.pop(item,None)
        return result
    def retranslate(self):
        for item,text in self.raw_items.items():
            if self.type(item):super().itemconfigure(item,text=translate(text))

# ตัวแทน module ใช้เฉพาะหน้าจอ EXORA ไม่แก้ tkinter ส่วนกลาง
tk=SimpleNamespace(**{name:getattr(native,name) for name in dir(native) if not name.startswith('_')})
for name,value in {'Label':Label,'Button':Button,'Checkbutton':Checkbutton,'Canvas':Canvas,'Toplevel':Toplevel}.items():setattr(tk,name,value)
ttk=SimpleNamespace(**{name:getattr(native_ttk,name) for name in dir(native_ttk) if not name.startswith('_')})
for name,value in {'Combobox':Combobox,'Treeview':Treeview,'Notebook':Notebook,'Checkbutton':TCheckbutton}.items():setattr(ttk,name,value)

# แปลกล่องข้อความและหัวข้อเลือกไฟล์ โดยไม่เปลี่ยนข้อมูลผลลัพธ์
class DialogProxy:
    def __init__(self,module):self.module=module
    def __getattr__(self,name):
        target=getattr(self.module,name)
        def call(*args,**kwargs):
            args=tuple(translate(value) for value in args)
            for key in ('title','message','detail','initialfile'):
                if key in kwargs:kwargs[key]=translate(kwargs[key])
            return target(*args,**kwargs)
        return call
messagebox=DialogProxy(native_messages)
filedialog=DialogProxy(native_files)
