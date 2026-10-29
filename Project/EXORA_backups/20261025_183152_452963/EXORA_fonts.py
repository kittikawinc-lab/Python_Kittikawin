"""Shared Thai typeface; load supplied OTF privately for this EXORA process."""
import ctypes
import os
from pathlib import Path
FONT_PATH=Path(__file__).resolve().parent/'EXORA_assets'/'fonts'/'PK Chiang Mai Medium.otf'
THAI_FAMILY='PK Chiang Mai Medium'
UI_FAMILIES={THAI_FAMILY,'Leelawadee UI','Segoe UI','Microsoft YaHei UI','Tahoma'}
_font_buffer=None
_font_handle=None

def load():
    """Keep the Windows font resource and bytes alive until the process exits."""
    global _font_buffer,_font_handle
    if _font_handle or os.name!='nt':return
    data=FONT_PATH.read_bytes();_font_buffer=ctypes.create_string_buffer(data)
    api=ctypes.WinDLL('gdi32',use_last_error=True)
    api.AddFontMemResourceEx.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint)]
    api.AddFontMemResourceEx.restype=ctypes.c_void_p
    count=ctypes.c_uint()
    _font_handle=api.AddFontMemResourceEx(_font_buffer,len(data),None,ctypes.byref(count))
    if not _font_handle:raise RuntimeError('ไม่สามารถโหลดฟอนต์ PK Chiang Mai Medium ได้')

def family(language='th'):
    load()
    return THAI_FAMILY if language=='th' else 'Microsoft YaHei UI' if language=='zh' else 'Segoe UI'

def refresh(root,language):
    """Update existing inputs, labels and canvas text without losing form values."""
    import tkinter.font as fonts
    selected=family(language)
    for name in ('TkDefaultFont','TkTextFont','TkMenuFont','TkHeadingFont','TkCaptionFont','TkSmallCaptionFont','TkTooltipFont'):
        try:fonts.nametofont(name,root).configure(family=selected)
        except Exception:pass
    def visit(widget):
        try:
            value=widget.cget('font');parts=widget.tk.splitlist(value)
            if parts and parts[0] in UI_FAMILIES:widget.configure(font=(selected,*parts[1:]))
        except Exception:pass
        if widget.winfo_class()=='Canvas':
            for item in widget.find_all():
                if widget.type(item)!='text':continue
                parts=widget.tk.splitlist(widget.itemcget(item,'font'))
                if parts and parts[0] in UI_FAMILIES:widget.itemconfigure(item,font=(selected,*parts[1:]))
        for child in widget.winfo_children():visit(child)
    visit(root)
load()
