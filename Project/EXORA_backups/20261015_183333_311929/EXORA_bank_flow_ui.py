"""Bank-account checkout and manually recorded settlement; no bank automation."""
import json
from pathlib import Path
from datetime import datetime,timedelta
from EXORA_i18n import tk,ttk,filedialog,messagebox
import EXORA_bank_flow as flow
import EXORA_database as db
import EXORA_profiles as profiles
import EXORA_receipts as receipts
import EXORA_banks as banks

# รายการใหม่เริ่มจากบัญชีผู้รับ ไม่เปิด QR หรือช่องทางจำลอง
def create(app,price=None):
    app.ensure_not_preview();actor=app.current_user['id'];win=app.dialog('EXORA | โอนบัญชีธนาคาร',700,820);body=app.scroll_dialog(win)
    app.label(body,'บัญชีรับเงินของลูกค้า',19,bold=True).pack(anchor='w',pady=8)
    app.label(body,'ร้านตรวจข้อมูลและยืนยันช่องทางธนาคารก่อนเปิดให้ชำระเงิน',11,wraplength=620).pack(anchor='w')
    values={}
    for key,label in [('recipient','ชื่อบัญชีผู้รับเงิน'),('bank','ธนาคารผู้รับ / SWIFT'),('account','เลขบัญชีผู้รับ / IBAN'),('country','ประเทศปลายทาง')]:values[key],_=app.field(body,label)
    values['amount'],_=app.field(body,'จำนวนเงินที่ต้องการแลก',str(price['from_amount']) if price else '1000')
    target=tk.StringVar(value=price['to_currency'] if price and price['to_currency']!='THB' else 'USD')
    app.label(body,'จาก THB เป็นสกุลเงิน',11).pack(anchor='w',pady=8)
    ttk.Combobox(body,textvariable=target,values=[r[1] for r in db.getcurs() if r[1]!='THB'],state='readonly').pack(fill='x')
    if price and price['from_currency']!='THB':
        app.label(body,'บัญชีออมทรัพย์ร้านรับชำระเป็น THB ช่องทางอื่นต้องยืนยันกับธนาคารก่อน',11,'#ab4b3c',wraplength=620).pack(anchor='w',pady=12)
        values['amount'].set('1000')
    def save():
        number=flow.create(actor,*(values[k].get() for k in ('recipient','bank','account','country')),'THB',target.get(),values['amount'].get())
        win.destroy();app.bank_flow_page();detail(app,number)
    app.button(body,'ส่งข้อมูลให้เจ้าหน้าที่ตรวจ',save).pack(fill='x',pady=20)

# อ่านรายการตามสิทธิ์ เจ้าหน้าที่ตรวจรายการเริ่มต้นได้ก่อนมีการชำระ
def show(app):
    body=app.page('รายการโอนบัญชีธนาคาร','BANK SETTLEMENT')
    app.label(body,'ธนาคารดำเนินการรับ–โอนเงินจริงภายนอกโปรแกรม เจ้าหน้าที่บันทึกผลใน EXORA',11,wraplength=1100).pack(anchor='w',pady=8)
    controls=tk.Frame(body,bg=body.cget('bg'));controls.pack(fill='x')
    tree=app.table(body,('number','status','amount','target'),('เลขรายการ','สถานะ','จำนวน THB','เป็นสกุลเงิน'),12,[280,340,170,150])
    def load():
        tree.delete(*tree.get_children())
        for row in flow.listing(app.current_user['id'],app.user_preview):tree.insert('','end',iid=row['number'],values=(row['number'],flow.STATES[row['status']],row['amount'],row['target']))
    def selected():
        selection=tree.selection()
        if not selection:raise ValueError('กรุณาเลือกรายการ')
        detail(app,selection[0])
    app.button(controls,'สร้างรายการ',lambda:create(app)).pack(side='left',padx=5)
    app.button(controls,'ดูรายละเอียด',selected,'secondary').pack(side='left',padx=5)
    app.button(controls,'รีเฟรช',load,'secondary').pack(side='left',padx=5)
    tree.bind('<Double-1>',lambda event:app.safe(selected));load()

# รายละเอียดเปิดเฉพาะคำสั่งที่ตรงสถานะจริง ไม่อนุมัติการโอนจากสลิปเพียงอย่างเดียว
def detail(app,number):
    actor=app.current_user['id'];row=flow.get(number,actor);win=app.dialog('EXORA | โอนบัญชีธนาคาร',850,850);body=app.scroll_dialog(win)
    app.label(body,flow.STATES[row['status']],20,bold=True,wraplength=740).pack(anchor='w',pady=8)
    verified=flow.identity_status(number,actor)
    app.label(body,'ยืนยันตัวตนบัญชีแล้ว ใช้ผลเดิมได้' if verified else 'ยังไม่มีผลยืนยันตัวตนที่ใช้ได้',11,app.green if verified else '#ab4b3c',wraplength=740).pack(anchor='w',pady=8)
    for label,value in [('เลขรายการ',number),('ชื่อบัญชีผู้รับเงิน',row['recipient']),('ธนาคารผู้รับ / SWIFT',row['bank']),('เลขบัญชีผู้รับ / IBAN',row['account']),('ประเทศปลายทาง',row['country'])]:app.label(body,label+': '+str(value),11,wraplength=740).pack(anchor='w',pady=5)
    if row['quote']:
        quote=json.loads(row['quote']);app.label(body,f"{quote['from_amount']:,.2f} THB → {quote['to_amount']:,.2f} {row['target']}",18,app.green,bold=True).pack(anchor='w',pady=15)
        app.label(body,'ราคานี้ใช้ได้ถึง '+datetime.fromtimestamp(quote['quote_expires']).strftime('%Y-%m-%d %H:%M'),10).pack(anchor='w')
    def reload():win.destroy();app.bank_flow_page();detail(app,number)
    def invoke(job):app.ensure_not_preview();job();reload()
    if verified and actor==row['user_id'] and row['status'] in ('identity_verified','quoted'):
        app.button(body,'รับราคา / คำนวณใหม่',lambda:invoke(lambda:flow.quote(number,actor))).pack(fill='x',pady=10)
    if verified and actor==row['user_id'] and row['status']=='quoted':
        store=profiles.shop();app.label(body,'บัญชีร้านที่รับเงิน',14,bold=True).pack(anchor='w',pady=10)
        app.label(body,' / '.join(store.get(k,'') for k in ('bank_name','bank_account_name','bank_account_number')),12,app.green,wraplength=740).pack(anchor='w')
        app.label(body,'โอนยอด THB ตามราคา แล้วกรอกข้อมูลผู้โอนและแนบหลักฐาน',11,wraplength=740).pack(anchor='w',pady=8)
        payment={'payer_bank':banks.selector(body)}
        for key,label,default in [('payer_name','ชื่อบัญชีผู้โอน',''),('payer_account','เลขบัญชีผู้โอน',''),('transfer_amount','ยอดโอน (THB)',str(json.loads(row['quote'])['from_amount'])),('transfer_at','วันเวลาโอน (YYYY-MM-DD HH:MM)',datetime.now().strftime('%Y-%m-%d %H:%M')),('transfer_reference','เลขอ้างอิงการชำระ','')]:payment[key],_=app.field(body,label,default)
        def submit():
            path=filedialog.askopenfilename(parent=win,title='เลือกหลักฐาน',filetypes=[('JPG / PNG','*.jpg *.jpeg *.png')])
            if path:invoke(lambda:flow.submit_payment(number,actor,{k:v.get() for k,v in payment.items()},path))
        app.button(body,'ส่งหลักฐานให้เจ้าหน้าที่ตรวจสอบ',submit).pack(fill='x',pady=15)
    if app.is_admin_view() and actor!=row['user_id']:
        # บันทึกเฉพาะผลและเลขอ้างอิง ไม่ให้เก็บภาพบัตรหรือเลขบัตรเต็มในฐานข้อมูลทั่วไป
        if not verified:
            app.label(body,'ตรวจเอกสารที่ยังไม่หมดอายุ เทียบใบหน้าผ่านวิดีโอคอล และชื่อเจ้าของบัญชี หรือใช้ผลจากผู้ให้บริการที่รองรับ',11,wraplength=740).pack(anchor='w',pady=10)
            methods={'เอกสารและวิดีโอคอล':'document_video','เลขอ้างอิงผู้ให้บริการยืนยันตัวตน':'provider_reference'}
            method=tk.StringVar(value=next(iter(methods)));ttk.Combobox(body,textvariable=method,values=list(methods),state='readonly').pack(fill='x')
            identity,_=app.field(body,'ผลตรวจ / ประเภทเอกสาร / เลขท้าย / เลขอ้างอิง (ไม่กรอกเลขบัตรเต็ม)')
            expiry,_=app.field(body,'ใช้ผลได้ถึง YYYY-MM-DD (ไม่เกินวันหมดอายุเอกสารหรือวันทบทวน)',(datetime.now()+timedelta(days=365)).date().isoformat())
        if row['status'] in ('identity_pending','route_pending'):
            route,_=app.field(body,'ยืนยันธนาคารรองรับประเทศ สกุลเงิน บัญชี และยอดรับสุทธิรวมค่าธรรมเนียม')
            app.label(body,'บันทึกหลังตรวจจริงภายนอกระบบเท่านั้น ไม่ใช่ eKYC อัตโนมัติ',10,'#ab4b3c',wraplength=740).pack(anchor='w',pady=8)
            app.button(body,'ยืนยันผลตรวจและช่องทางธนาคาร',lambda:invoke(lambda:flow.verify(number,actor,identity.get() if not verified else '',route.get(),methods[method.get()] if not verified else 'document_video',expiry.get() if not verified else None))).pack(fill='x',pady=10)
            app.button(body,'ปฏิเสธข้อมูลผู้รับ',lambda:invoke(lambda:flow.reject(number,actor)),'danger').pack(fill='x')
        elif not verified:
            app.button(body,'บันทึกผลยืนยันตัวตนใหม่',lambda:invoke(lambda:flow.renew_identity(number,actor,identity.get(),methods[method.get()],expiry.get()))).pack(fill='x',pady=10)
        if verified:app.button(body,'ถอนผลยืนยันตัวตน',lambda:invoke(lambda:flow.revoke_identity(number,actor)),'danger').pack(anchor='w',pady=8)
        if row['status']=='payment_pending':
            import EXORA_payments as payments
            transaction=payments.get_transaction(number,actor)
            app.button(body,'เปิดสลิปขนาดเต็ม',lambda:__import__('os').startfile(str(payments.slip_path(transaction))),'secondary').pack(anchor='w',pady=8)
            reference,_=app.field(body,'เลขอ้างอิงเงินเข้าที่ตรวจจากธนาคาร')
            app.button(body,'ยืนยันรับเงินจริงเข้าบัญชีร้าน',lambda:invoke(lambda:flow.verify_payment(number,actor,reference.get()))).pack(fill='x',pady=10)
        if row['status']=='payment_verified':app.button(body,'เริ่มดำเนินการโอนจ่าย',lambda:invoke(lambda:flow.start_payout(number,actor))).pack(fill='x',pady=15)
        if row['status']=='payout_processing':
            app.label(body,'โอนผ่านธนาคารของร้าน ตรวจชื่อผู้รับ ยอดและสกุลเงินก่อนยืนยัน ห้ามโอนซ้ำหากยังไม่ทราบผล',11,'#ab4b3c',wraplength=740).pack(anchor='w',pady=10)
            reference,_=app.field(body,'เลขอ้างอิงการโอนจ่ายจากธนาคาร')
            def complete():
                app.ensure_not_preview()
                path=filedialog.askopenfilename(parent=win,title='หลักฐานการโอนจ่าย',filetypes=[('JPG / PNG','*.jpg *.jpeg *.png')])
                if not path:return
                if not messagebox.askyesno('EXORA','ยืนยันว่าตรวจผลโอนสำเร็จจากธนาคารแล้ว?',parent=win):return
                flow.complete(number,actor,reference.get(),path);reload()
                def sent(result):
                    if result.get('status')!='sent':messagebox.showwarning('EXORA',result.get('message','ส่งไม่สำเร็จ'),parent=app.root)
                app.background(lambda:receipts.send_to_user(number,actor),sent)
            app.button(body,'บันทึกผลโอนสำเร็จและส่งใบเสร็จ',complete).pack(fill='x',pady=15)
    if row['status']=='completed':
        app.label(body,'เลขอ้างอิงการโอนจ่าย: '+row['payout_ref'],11,wraplength=740).pack(anchor='w',pady=12)
        app.button(body,'บันทึก PDF',lambda:app.export_pdf(number)).pack(fill='x',pady=8)
        app.button(body,'ส่งใบเสร็จทางอีเมล',lambda:app.background(lambda:receipts.send_to_user(number,actor),lambda result:messagebox.showinfo('EXORA',result['message'],parent=app.root)),'secondary').pack(fill='x')
