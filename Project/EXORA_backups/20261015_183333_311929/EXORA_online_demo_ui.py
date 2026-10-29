"""หน้าทดลอง settlement ในโปรแกรมเดิม ไม่เปิดบริการเว็บหรือธนาคารจริง."""
import json
from EXORA_i18n import tk,ttk,filedialog
import EXORA_online_demo as demo
import EXORA_database as db

# แสดงรายการจำลองตามสิทธิ์ และสร้างฟอร์มด้วยส่วนประกอบธีมเดิม
def show(app):
    actor=app.current_user['id'];body=app.page('จำลองแลกเงินออนไลน์','ONLINE SETTLEMENT / SIMULATION')
    app.label(body,'SIMULATION · ไม่โอนเงินจริง ไม่ยืนยันตัวตนจริง ไม่ส่งอีเมลจริง',13,'#ab4b3c',bold=True,wraplength=1100).pack(anchor='w',pady=8)
    app.label(body,'บัญชีออมทรัพย์ร้านจำลอง: DEMO-STORE-0001',11,app.green).pack(anchor='w',pady=6)
    app.label(body,'บัญชีรับเงิน → ตรวจตัวตน → รับราคา → ชำระจำลอง → ตรวจรับชำระ → โอนจ่ายจำลอง → ใบเสร็จ',11,wraplength=1100).pack(anchor='w',pady=(0,15))
    controls=tk.Frame(body,bg=body.cget('bg'));controls.pack(fill='x')
    table=app.table(body,('number','owner','status','source','amount','target'),('เลขรายการ','ผู้ใช้','สถานะ','จาก','จำนวน','เป็น'),10,[250,90,240,100,150,100])

    # โหลดเฉพาะโหมดจำลองโดยไม่เปลี่ยนสถิติหรือคิวอีเมลร้าน
    def load():
        table.delete(*table.get_children())
        for row in demo.listing(actor,app.user_preview):table.insert('','end',iid=row['number'],values=(row['number'],row['user_id'],demo.STATES[row['status']],row['source'],row['amount'],row['target']))

    # ลงทะเบียนข้อมูลผู้รับตัวอย่าง ไม่รับเอกสารส่วนตัวจริง
    def create():
        app.ensure_not_preview();win=app.dialog('EXORA / SIMULATION',660,760);inner=app.scroll_dialog(win)
        app.label(inner,'ใช้ข้อมูลสมมติและบัญชี DEMO- เท่านั้น',12,'#ab4b3c',wraplength=550).pack(anchor='w')
        values={}
        for key,label,default in [('recipient','ชื่อผู้รับจำลอง','Demo Customer'),('bank','ธนาคารจำลอง','Demo Bank'),('account','เลขบัญชีจำลอง','DEMO-0001'),('country','ประเทศปลายทางจำลอง','Demo destination'),('amount','จำนวนเงินที่ต้องการแลก','1000')]:values[key],_=app.field(inner,label,default)
        codes=[row[1] for row in db.getcurs()]
        source=tk.StringVar(value='THB');target=tk.StringVar(value='USD')
        for label,var in [('จากสกุลเงิน',source),('เป็นสกุลเงิน',target)]:
            app.label(inner,label,10).pack(anchor='w',pady=5);ttk.Combobox(inner,textvariable=var,values=codes,state='readonly').pack(fill='x')
        def save():
            number=demo.create(actor,*(values[key].get() for key in ('recipient','bank','account','country')),source.get(),target.get(),values['amount'].get())
            win.destroy();load();detail(number)
        app.button(inner,'ส่งตรวจตัวตนจำลอง',save).pack(fill='x',pady=16)

    # ทุกปุ่มเรียก state machine เดียวกันและอ่านสิทธิ์จากฐานข้อมูล
    def detail(number=None):
        if number is None:
            selected=table.selection()
            if not selected:raise ValueError('กรุณาเลือกรายการ')
            number=selected[0]
        row=demo.get(number,actor);win=app.dialog('EXORA / SIMULATION',740,740);inner=app.scroll_dialog(win)
        app.label(inner,'SIMULATION · ไม่มีการเคลื่อนย้ายเงินจริง',15,'#ab4b3c',bold=True,wraplength=640).pack(anchor='w',pady=10)
        for label,value in [('เลขรายการ',number),('สถานะ',demo.STATES[row['status']]),('ชื่อผู้รับจำลอง',row['recipient']),('ธนาคารจำลอง',row['bank']),('เลขบัญชีจำลอง',row['account']),('ประเทศปลายทางจำลอง',row['country'])]:app.label(inner,label+': '+str(value),11,wraplength=620).pack(anchor='w',pady=5)
        if row['quote']:
            price=json.loads(row['quote']);app.label(inner,f"{price['from_amount']:,.2f} {row['source']} → {price['to_amount']:,.2f} {row['target']}\nDemo fee: 0.00 · SIMULATED RATE",15,app.green,bold=True,wraplength=620).pack(anchor='w',pady=15)
        # ไม่เขียนการเปลี่ยนสถานะในโหมดดูตัวอย่างผู้ใช้
        def action(command):
            app.ensure_not_preview()
            if command=='quote':demo.quote(number,actor)
            else:demo.act(number,actor,command)
            win.destroy();load();detail(number)
        if actor==row['user_id']:
            if row['status'] in ('identity_verified','quoted'):app.button(inner,'รับราคา / คำนวณใหม่',lambda:action('quote')).pack(fill='x',pady=6)
            if row['status']=='quoted':app.button(inner,'ยืนยันชำระเงินจำลอง',lambda:action('pay')).pack(fill='x',pady=6)
        if app.is_admin_view() and actor!=row['user_id']:
            actions={'identity_pending':('ยืนยันตัวตนจำลอง','verify_identity'),'payment_pending':('ยืนยันรับชำระจำลอง','verify_payment'),'payment_verified':('เริ่มโอนจ่ายจำลอง','start_payout'),'payout_processing':('ยืนยันโอนสำเร็จจำลอง','complete')}
            if row['status'] in actions:
                caption,command=actions[row['status']];app.button(inner,caption,lambda:action(command)).pack(fill='x',pady=6)
            if row['status'] in ('identity_pending','payment_pending'):app.button(inner,'ปฏิเสธจำลอง',lambda:action('reject'),'danger').pack(fill='x',pady=6)
        if row['status']=='completed':
            app.label(inner,'Email: SIMULATED ONLY · ไม่ได้ส่งอีเมลจริง',11,wraplength=620).pack(anchor='w',pady=10)
            def save_pdf():
                destination=filedialog.asksaveasfilename(parent=win,defaultextension='.pdf',initialfile=number+'.pdf',filetypes=[('PDF','*.pdf')])
                if destination:demo.receipt(number,actor,destination)
            app.button(inner,'บันทึก PDF จำลอง',save_pdf).pack(fill='x',pady=8)
    app.button(controls,'สร้างรายการจำลอง',create).pack(side='left',padx=(0,8))
    app.button(controls,'ดูรายละเอียด',detail,'secondary').pack(side='left')
    app.button(controls,'รีเฟรช',load,'secondary').pack(side='left',padx=8)
    table.bind('<Double-1>',lambda event:app.safe(detail));load()
