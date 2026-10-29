"""Bank labels and application-drawn badges, not official bank logos."""
# รายชื่ออ้างอิง ธปท.: https://www.bot.or.th/th/fi-branch.html
BANKS=[('KTB','กรุงไทย','#087bbd'),('KBANK','กสิกรไทย','#16874b'),('SCB','ไทยพาณิชย์','#634185'),('BBL','กรุงเทพ','#235c9d'),('BAY','กรุงศรีอยุธยา','#c49d26'),('TTB','ทหารไทยธนชาต','#ec7039'),('GSB','ออมสิน','#d64b94'),('UOB','ยูโอบี','#25457d'),('OTHER','ธนาคารอื่น','#617c66')]

# คืนรายละเอียดธนาคารจากชื่อหรือรหัสที่เลือก โดยรองรับค่าธนาคารเดิม
def lookup(value):
    value=str(value or '')
    return next((bank for bank in BANKS if bank[0]!='OTHER' and (bank[0]==value.upper() or bank[1] in value)),BANKS[-1])

# สร้างตัวเลือกธนาคารพร้อมไอคอนตัวอักษรย่อ เปลี่ยนไอคอนตามที่เลือก
def selector(parent,initial=''):
    from EXORA_i18n import tk,ttk
    # คำอธิบาย import: กำหนดฟอนต์และขนาดของหน้าจอ
    from EXORA_layout import font
    frame=tk.Frame(parent,bg=parent.cget('bg'));frame.pack(fill='x')
    badge=tk.Label(frame,width=6,font=font(10,True),fg='white',padx=6,pady=10);badge.pack(side='left',padx=(0,10))
    var=tk.StringVar(value=initial or 'เลือกธนาคาร')
    combo=ttk.Combobox(frame,textvariable=var,values=[b[1] for b in BANKS],state='readonly',font=font(10));combo.pack(side='left',fill='x',expand=True)
    combo.bind('<MouseWheel>',lambda event:'break')
    # คำอธิบาย def update: เปลี่ยนไอคอนให้ตรงกับธนาคารที่เลือก
    def update(*args):
        code,name,color=lookup(var.get());badge.configure(text=code,bg=color)
    var.trace_add('write',update);update();return var
