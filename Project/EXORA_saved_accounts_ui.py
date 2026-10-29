"""Saved account selectors and owner-only profile controls."""
import re
from EXORA_i18n import tk,ttk,messagebox
import EXORA_saved_accounts as accounts

def selector(app,parent,kind,values):
    rows=accounts.listing(app.current_user['id'],kind)
    choices={accounts.caption(r):r for r in rows}
    if kind=='payer':
        for row in accounts.listing(app.current_user['id'],'recipient'):
            if re.fullmatch(r'[0-9]{6,20}',row['account']):choices['ใช้บัญชีรับเงิน: '+accounts.caption(row)]=row
    app.label(parent,'บัญชีรับเงินที่บันทึกไว้' if kind=='recipient' else 'บัญชีผู้โอนที่บันทึกไว้',11).pack(anchor='w',pady=(12,6))
    selected=tk.StringVar(value='บัญชีใหม่')
    combo=ttk.Combobox(parent,textvariable=selected,values=['บัญชีใหม่',*choices],preserve_values=list(choices),state='readonly');combo.pack(fill='x',pady=6)
    mapping={'recipient':'name','bank':'bank','account':'account','country':'country'} if kind=='recipient' else {'payer_name':'name','payer_bank':'bank','payer_account':'account'}
    def apply(*args):
        row=choices.get(selected.get())
        for key,field in mapping.items():
            fallback=accounts.customer_name(app.current_user['id']) if field=='name' else ''
            values[key].set(row[field] if row else fallback)
    selected.trace_add('write',apply)
    default=next((accounts.caption(row) for row in rows if row['is_default']),None)
    if default:selected.set(default)
    else:apply()
    return combo

def remember_options(app,parent):
    remember=tk.BooleanVar(value=True);default=tk.BooleanVar(value=False)
    ttk.Checkbutton(parent,text='บันทึกบัญชีนี้เพื่อใช้ครั้งถัดไป',variable=remember).pack(anchor='w',pady=4)
    ttk.Checkbutton(parent,text='ตั้งเป็นบัญชีเริ่มต้น',variable=default).pack(anchor='w',pady=4)
    return remember,default

def manage(app,parent):
    actor=app.current_user['id'];card=app.card(parent);card.pack(fill='x',pady=(0,20))
    app.label(card,'บัญชีที่บันทึกไว้',17,bold=True).pack(anchor='w',padx=20,pady=14)
    tree=app.table(card,('kind','bank','account','name','default'),('ประเภท','ธนาคาร','เลขบัญชี','ชื่อบัญชี','เริ่มต้น'),4,[150,220,160,240,110])
    def load():
        tree.delete(*tree.get_children())
        for row in accounts.listing(actor):tree.insert('','end',iid=str(row['id']),values=('บัญชีรับเงิน' if row['kind']=='recipient' else 'บัญชีผู้โอน',row['bank'],'••••'+row['account'][-4:],row['name'],'✓' if row['is_default'] else ''))
    def act(delete=False):
        selection=tree.selection()
        if not selection:raise ValueError('กรุณาเลือกบัญชีที่บันทึกไว้')
        if delete and not messagebox.askyesno('EXORA','ลบบัญชีที่บันทึกไว้? ประวัติรายการเดิมยังคงอยู่',parent=app.root):return
        accounts.change(actor,int(selection[0]),delete);load()
    controls=tk.Frame(card,bg=card.cget('bg'));controls.pack(fill='x',padx=16,pady=12)
    app.button(controls,'ตั้งเป็นบัญชีเริ่มต้น',act,'secondary').pack(side='left',padx=5)
    app.button(controls,'ลบบัญชีที่บันทึกไว้',lambda:act(True),'danger').pack(side='left',padx=5)
    load()
