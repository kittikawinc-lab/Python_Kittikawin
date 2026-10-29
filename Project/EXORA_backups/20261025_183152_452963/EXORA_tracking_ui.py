"""Owner-only order tracking and stage progression."""
from EXORA_i18n import tk
import EXORA_bank_flow as flow
import EXORA_payments as payments
STAGES=('ยืนยันตัวตน','คำนวณและตรวจบัญชี','ชำระเงิน','ตรวจเงินเข้า','โอนให้ลูกค้า','สำเร็จ')
POSITION={'identity_pending':0,'identity_verified':1,'route_pending':1,'quote_pending_route':1,'quoted':2,'payment_pending':3,'payment_verified':4,'payout_processing':4,'completed':5}
NEXT={'identity_pending':'แนบเอกสารแล้วรอเจ้าหน้าที่ตรวจ','identity_verified':'ขอคำนวณยอดชำระได้ทันที','route_pending':'ขอคำนวณได้ รอตรวจบัญชีรับเงิน','quote_pending_route':'ได้รับราคาแล้ว รอตรวจช่องทางโอนก่อนชำระ','quoted':'ชำระและแนบหลักฐานภายในอายุราคา','payment_pending':'รอตรวจยอดเงินจริงเข้าบัญชีร้าน','payment_verified':'รับชำระแล้ว รอโอนให้คุณ','payout_processing':'กำลังดำเนินการโอนให้คุณ','completed':'ดาวน์โหลดใบเสร็จได้','rejected':'เปิดรายละเอียดเพื่อดูผลตรวจ'}
def show(app):
    actor=app.current_user['id'];body=app.page('ติดตามรายการ','ORDER TRACKING')
    tree=app.table(body,('number','status','next'),('เลขรายการ','สถานะปัจจุบัน','ขั้นตอนถัดไป'),8,[260,320,650])
    panel=tk.Frame(body,bg=body.cget('bg'));panel.pack(fill='both',expand=True,pady=12)
    def render(event=None):
        for child in panel.winfo_children():child.destroy()
        selected=tree.selection()
        if not selected:return
        key=selected[0]
        if key.startswith('legacy:'):
            app.button(panel,'เปิดรายละเอียดรายการเดิม',lambda:app.detail(key[7:])).pack(anchor='w');return
        row=flow.get(key,actor);index=POSITION.get(row['status'],-1)
        app.label(panel,flow.STATES[row['status']],18,bold=True).pack(anchor='w',pady=8)
        steps='  →  '.join(('✓ ' if n<index or row['status']=='completed' else '● ' if n==index else '○ ')+title for n,title in enumerate(STAGES))
        app.label(panel,steps,12,wraplength=1400).pack(anchor='w',pady=8)
        app.label(panel,row.get('feedback') or NEXT[row['status']],12,wraplength=1300).pack(anchor='w',pady=8)
        app.button(panel,'เปิดรายละเอียด / ดำเนินการต่อ',lambda:__import__('EXORA_bank_flow_ui').detail(app,key)).pack(anchor='w',pady=8)
        labels={'created':'สร้างรายการ','route_and_identity_verified':'ตรวจตัวตนและช่องทางโอนแล้ว','quote_pending_route':'คำนวณราคา รอตรวจช่องทางโอน','quoted':'ออกยอดชำระ','payment_submitted':'ส่งหลักฐานชำระ','payment_verified':'ตรวจรับเงินจริงแล้ว','payout_processing':'เริ่มโอนจ่าย','completed':'โอนจ่ายสำเร็จ','review_feedback':'ผลตรวจจากเจ้าหน้าที่','rejected':'ไม่ผ่านการตรวจ'}
        for action,note,when in flow.timeline(key,actor)[-6:]:app.label(panel,when.replace('T',' ')+' · '+labels.get(action,'อัปเดตสถานะรายการ'),10,wraplength=1300).pack(anchor='w',pady=2)
    def load():
        selection=tree.selection();tree.delete(*tree.get_children());rows=flow.listing(actor,own_only=True);known={r['number'] for r in rows}
        for row in rows:tree.insert('','end',iid=row['number'],values=(row['number'],flow.STATES[row['status']],row.get('feedback') or NEXT[row['status']]))
        for row in payments.list_transactions(actor,own_only=True):
            if row[0] not in known:tree.insert('','end',iid='legacy:'+row[0],values=(row[0],{'pending':'รอตรวจสอบ','approved':'อนุมัติแล้ว','rejected':'ปฏิเสธ'}.get(row[9],row[9]),'เปิดรายละเอียดรายการเดิม'))
        if selection and tree.exists(selection[0]):tree.selection_set(selection)
        elif tree.get_children():tree.selection_set(tree.get_children()[0])
        render()
    tree.bind('<<TreeviewSelect>>',render)
    app.button(body,'รีเฟรช',load,'secondary').pack(anchor='w',pady=6)
    load();timer={'id':None}
    def refresh():
        if not body.winfo_exists():return
        app.safe(load);timer['id']=body.after(3000,refresh)
    def cleanup(event):
        if event.widget is body and timer['id']:
            try:body.after_cancel(timer['id'])
            except tk.TclError:pass
    body.bind('<Destroy>',cleanup,add='+');timer['id']=body.after(3000,refresh)
