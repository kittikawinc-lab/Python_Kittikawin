'''
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import EXORA_database
import EXORA_calculator
from EXORA_currency_page import CurrencyPage


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "Currency Exchange System")

        self.root.geometry("1200x750")

        self.root.minsize(1000,650)

        self.current_user = None

        self.currency_page = None

        self.login_page()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.currency_page = None

    def login_page(self):
        self.clear_window()
        frame = tk.Frame(self.root,bg="#020617")
        frame.pack(fill="both",expand=True)

        tk.Label(frame,text="💱",font=("Arial", 50),bg="#020617",fg="white").pack(pady=(80, 10))

        tk.Label(frame,text="Currency Exchange",font=("Arial", 28, "bold"),bg="#020617",fg="white").pack()

        tk.Label(frame,text="ระบบร้านแลกเปลี่ยนเงินตราต่างประเทศ",font=("Arial", 12),bg="#020617",fg="#94a3b8").pack( pady=10)

        form = tk.Frame(frame,bg="#020617")
        form.pack(pady=30)

        tk.Label(form,text="Username",bg="#020617",fg="white").grid(row=0,column=0,sticky="w",pady=8)

        self.username_entry = tk.Entry(form,width=30)

        self.username_entry.grid(row=1,column=0,pady=5)

        tk.Label(form,text="Password",bg="#020617",fg="white").grid(row=2,column=0,sticky="w",pady=8)

        self.password_entry = tk.Entry(form,width=30,show="*")

        self.password_entry.grid(row=3,column=0,pady=5)

        tk.Button(form,text="เข้าสู่ระบบ",width=25,bg="#2563eb",fg="white",relief="flat",command=self.login).grid(row=4,column=0,pady=25)

        self.password_entry.bind("<Return>",lambda event: self.login())

    def login_page(self):
     self.clear_window()

     frame = tk.Frame(self.root, bg="#020617")
     frame.pack(fill="both", expand=True)

     tk.Label(
        frame,
        text="💱",
        font=("Arial", 46),
        bg="#020617",
        fg="white"
     ).pack(pady=(45, 5))

     tk.Label(
        frame,
        text="EXORA | Currency Exchange",
        font=("Arial", 25, "bold"),
        bg="#020617",
        fg="white"
     ).pack()

     tk.Label(
        frame,
        text="ระบบร้านแลกเปลี่ยนเงินตราต่างประเทศ",
        bg="#020617",
        fg="#94a3b8"
     ).pack(pady=(5, 20))

     form = tk.Frame(frame, bg="#0f172a", padx=32, pady=24)
     form.pack()

     tk.Label(
        form, text="Username หรือ Email",
        bg="#0f172a", fg="white"
     ).grid(row=0, column=0, sticky="w", pady=(0, 5))

     self.username_entry = tk.Entry(form, width=32, font=("Arial", 11))
     self.username_entry.grid(row=1, column=0, pady=(0, 12), ipady=5)

     tk.Label(
        form, text="Password",
        bg="#0f172a", fg="white"
     ).grid(row=2, column=0, sticky="w", pady=(0, 5))

     self.password_entry = tk.Entry(
        form, width=32, show="*", font=("Arial", 11)
     )
     self.password_entry.grid(row=3, column=0, ipady=5)

     self.show_password_var = tk.BooleanVar(value=False)

     tk.Checkbutton(
        form,
        text="แสดงรหัสผ่าน",
        variable=self.show_password_var,
        command=self.toggle_password,
        bg="#0f172a",
        fg="white",
        selectcolor="#0f172a",
        activebackground="#0f172a",
        activeforeground="white"
     ).grid(row=4, column=0, sticky="w", pady=5)

     self.remember_var = tk.BooleanVar(value=False)

     remembered = self._read_remembered_username()
     if remembered:
        self.username_entry.insert(0, remembered)
        self.remember_var.set(True)

     tk.Checkbutton(
        form,
        text="จดจำ Username",
        variable=self.remember_var,
        bg="#0f172a",
        fg="white",
        selectcolor="#0f172a",
        activebackground="#0f172a",
        activeforeground="white"
     ).grid(row=5, column=0, sticky="w")

     tk.Button(
        form,
        text="SIGN IN / เข้าสู่ระบบ",
        width=30,
        bg="#2563eb",
        fg="white",
        relief="flat",
        command=self.login
     ).grid(row=6, column=0, pady=(18, 8), ipady=6)

     tk.Button(
        form,
        text="Forgot Password? / ลืมรหัสผ่าน",
        bg="#0f172a",
        fg="#93c5fd",
        relief="flat",
        command=self.forgot_password_page
     ).grid(row=7, column=0, pady=2)

     tk.Label(
        form, text="ยังไม่มีบัญชี?",
        bg="#0f172a", fg="#cbd5e1"
     ).grid(row=8, column=0, pady=(12, 2))

     tk.Button(
        form,
        text="CREATE ACCOUNT / สมัครสมาชิก",
        width=30,
        bg="#334155",
        fg="white",
        relief="flat",
        command=self.signup_page
     ).grid(row=9, column=0, pady=(2, 0), ipady=5)

     self.password_entry.bind("<Return>", lambda event: self.login())
     self.username_entry.focus_set()

    def toggle_password(self):
     self.password_entry.config(
        show="" if self.show_password_var.get() else "*")

    def _read_remembered_username(self):
        try:
            with open("EXORA_remember.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except (OSError, UnicodeError):
            return ""


    def _save_remembered_username(self, username):
        try:
            if self.remember_var.get():
                with open("EXORA_remember.txt", "w", encoding="utf-8") as f:
                    f.write(username)
            else:
                try:
                    os.remove("EXORA_remember.txt")
                except FileNotFoundError:
                    pass
        except OSError as exc:
            messagebox.showwarning(
            "Remember Username",
            f"ไม่สามารถบันทึก Username ได้: {exc}"
        )

    def signup_page(self):
            self.clear_window()
            frame = tk.Frame(self.root, bg="#020617")
            frame.pack(fill="both", expand=True)
            tk.Label(frame, text="CREATE ACCOUNT", font=("Arial", 25, "bold"), bg="#020617", fg="white").pack(pady=(35, 5))
            tk.Label(frame, text="สมัครบัญชี EXORA", font=("Arial", 12), bg="#020617", fg="#94a3b8").pack(pady=(0, 18))
            form = tk.Frame(frame, bg="#0f172a", padx=30, pady=22)
            form.pack()
            self.signup_username = tk.Entry(form, width=34, font=("Arial", 11))
            self.signup_email = tk.Entry(form, width=34, font=("Arial", 11))
            self.signup_password = tk.Entry(form, width=34, show="*", font=("Arial", 11))
            self.signup_confirm = tk.Entry(form, width=34, show="*", font=("Arial", 11))
            fields = [("Username (อย่างน้อย 3 ตัว)", self.signup_username), ("Email", self.signup_email),
                      ("Password (อย่างน้อย 8 ตัว)", self.signup_password), ("Confirm Password", self.signup_confirm)]
            for row, (label, entry) in enumerate(fields):
                tk.Label(form, text=label, bg="#0f172a", fg="white").grid(row=row*2, column=0, sticky="w", pady=(5, 3))
                entry.grid(row=row*2+1, column=0, pady=(0, 6), ipady=4)
            self.signup_show_var = tk.BooleanVar(value=False)
            tk.Checkbutton(form, text="แสดงรหัสผ่าน", variable=self.signup_show_var, command=self.toggle_signup_password,
                           bg="#0f172a", fg="white", selectcolor="#0f172a", activebackground="#0f172a", activeforeground="white").grid(row=8, column=0, sticky="w", pady=4)
            tk.Label(form, text="โปรดตรวจสอบข้อมูลให้ครบถ้วนก่อนสมัครสมาชิก", bg="#0f172a", fg="#fbbf24").grid(row=9, column=0, pady=4)
            tk.Button(form, text="CREATE ACCOUNT / สมัครสมาชิก", width=30, bg="#2563eb", fg="white", relief="flat",
                      command=self.register_account).grid(row=10, column=0, pady=(10, 6), ipady=5)
            tk.Button(form, text="กลับไปหน้า Sign In", bg="#0f172a", fg="#93c5fd", relief="flat", command=self.login_page).grid(row=11, column=0)
            self.signup_username.focus_set()
    
    def toggle_signup_password(self):
        show = "" if self.signup_show_var.get() else "*"
        self.signup_password.config(show=show)
        self.signup_confirm.config(show=show)
    
    def register_account(self):
        username = self.signup_username.get().strip()
        email = self.signup_email.get().strip()
        password = self.signup_password.get()
        confirm = self.signup_confirm.get()
        if not username or not email or not password or not confirm:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลทุกช่อง")
            return
        if password != confirm:
            messagebox.showerror("Password ไม่ตรงกัน", "Password และ Confirm Password ต้องตรงกัน")
            return
        success, message = EXORA_database.register_user(username, email, password)
        if success:
            messagebox.showinfo("สมัครสมาชิกสำเร็จ", message)
            self.login_page()
            self.username_entry.insert(0, username)
            self.password_entry.focus_set()
        else:
            messagebox.showerror("สมัครสมาชิกไม่สำเร็จ", message)

    def forgot_password_page(self):
            self.clear_window()
            frame = tk.Frame(self.root, bg="#020617")
            frame.pack(fill="both", expand=True)
            tk.Label(frame, text="RESET PASSWORD", font=("Arial", 24, "bold"), bg="#020617", fg="white").pack(pady=(45, 8))
            tk.Label(frame, text="สำหรับโปรแกรมเดสก์ท็อปตัวอย่าง: ยืนยันด้วย Username และ Email ที่ลงทะเบียนไว้", wraplength=480,
                     bg="#020617", fg="#cbd5e1").pack(pady=(0, 18))
            form = tk.Frame(frame, bg="#0f172a", padx=30, pady=24)
            form.pack()
            self.reset_identifier = tk.Entry(form, width=34, font=("Arial", 11))
            self.reset_email = tk.Entry(form, width=34, font=("Arial", 11))
            self.reset_password = tk.Entry(form, width=34, show="*", font=("Arial", 11))
            self.reset_confirm = tk.Entry(form, width=34, show="*", font=("Arial", 11))
            for row, (label, entry) in enumerate([
                ("Username หรือ Email", self.reset_identifier), ("Email ที่ลงทะเบียน", self.reset_email),
                ("Password ใหม่ (อย่างน้อย 8 ตัว)", self.reset_password), ("ยืนยัน Password ใหม่", self.reset_confirm)]):
                tk.Label(form, text=label, bg="#0f172a", fg="white").grid(row=row*2, column=0, sticky="w", pady=(5, 3))
                entry.grid(row=row*2+1, column=0, pady=(0, 7), ipady=4)
            tk.Button(form, text="RESET PASSWORD", width=30, bg="#2563eb", fg="white", relief="flat",
                      command=self.reset_account_password).grid(row=8, column=0, pady=(12, 7), ipady=5)
            tk.Label(form, text="หมายเหตุ: ระบบนี้ยังไม่ได้ส่ง OTP/อีเมลยืนยันจริง", bg="#0f172a", fg="#fbbf24").grid(row=9, column=0, pady=3)
            tk.Button(form, text="กลับไปหน้า Sign In", bg="#0f172a", fg="#93c5fd", relief="flat", command=self.login_page).grid(row=10, column=0)
    
    def reset_account_password(self):
            identifier = self.reset_identifier.get().strip()
            email = self.reset_email.get().strip()
            password = self.reset_password.get()
            confirm = self.reset_confirm.get()
            if not identifier or not email or not password or not confirm:
                messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลทุกช่อง")
                return
            if password != confirm:
                messagebox.showerror("Password ไม่ตรงกัน", "Password ใหม่ทั้งสองช่องต้องตรงกัน")
                return
            success, message = EXORA_database.reset_password(identifier, email, password)
            if success:
                messagebox.showinfo("สำเร็จ", message)
                self.login_page()
                self.username_entry.insert(0, identifier)
            else:
                messagebox.showerror("Reset Password", message)
            

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "ข้อมูลไม่ครบ",
                "กรุณากรอก Username/Email และ Password"
            )
            return

        user = EXORA_database.login(username, password)

        if not user:
            messagebox.showerror(
                "เข้าสู่ระบบไม่สำเร็จ",
                "Username/Email หรือ Password ไม่ถูกต้อง "
                "หรือบัญชีถูกปิดใช้งาน"
            )
            return

        self._save_remembered_username(username)
        self.current_user = user
        self.dashboard()

    def dashboard(self):
        self.clear_window()

        sidebar = tk.Frame(self.root,width=220,bg="#0f172a")

        sidebar.pack(side="left",fill="y")

        sidebar.pack_propagate(False)

        tk.Label(sidebar,text="💱 Currency\nExchange",font=("Arial", 18, "bold"),fg="white",bg="#0f172a").pack(pady=30)

        tk.Label( sidebar,text=(f"{self.current_user['username']}\n"f"Role: {self.current_user['role']}"),fg="#94a3b8",bg="#0f172a").pack(pady=10)

        self.create_menu_button(sidebar,"Dashboard",self.dashboard_home)

        self.create_menu_button(sidebar,"แลกเปลี่ยนเงิน",self.exchange_page)

        self.create_menu_button(sidebar,"ประวัติรายการ",self.history_page)

        if self.current_user["role"] == "admin":
            self.create_menu_button(sidebar,"ค่าเงิน",self.currency_management)

            self.create_menu_button(sidebar,"ผู้ใช้งาน",self.user_management)

        self.create_menu_button(sidebar,"Logout",self.logout)

        self.main_frame = tk.Frame(self.root,bg="#020617")

        self.main_frame.pack(side="right",fill="both",expand=True)

        self.dashboard_home()

    def create_menu_button(self,parent,text,command):
        tk.Button(parent,text=text,font=("Arial", 11),anchor="w",padx=20,pady=12,bg="#0f172a",fg="white",activebackground="#1e293b",activeforeground="white",relief="flat",command=command).pack(fill="x")

    def dashboard_home(self):
        self.clear_main()

        tk.Label(self.main_frame,text="Dashboard",font=("Arial", 28, "bold"),bg="#020617",fg="white").pack(pady=40)

        tk.Label(self.main_frame,text=(
                "ยินดีต้อนรับเข้าสู่ระบบร้าน EXORA\n\n"
                "สามารถจัดการอัตราแลกเปลี่ยน "
                "ทำรายการแลกเงิน และตรวจสอบประวัติได้"
            ),font=("Arial", 14),bg="#020617",fg="#cbd5e1",justify="center").pack()

    def currency_management(self):
        self.clear_main()

        self.currency_page = CurrencyPage(self.main_frame)

        self.currency_page.show()

    def exchange_page(self):
        self.clear_main()

        tk.Label(self.main_frame,text="แลกเปลี่ยนเงิน",font=("Arial", 26, "bold"),bg="#020617",fg="white").pack(pady=25)

        form = tk.Frame(self.main_frame,bg="#020617")

        form.pack(pady=10)

        tk.Label(form,text="ประเภท",bg="#020617",fg="white").grid(row=0,column=0,padx=10,pady=10)

        self.type_var = tk.StringVar(value="BUY")

        type_combo = ttk.Combobox(form,textvariable=self.type_var,values=["BUY","SELL"],state="readonly",width=20)

        type_combo.grid(row=0,column=1)

        tk.Label(form,text="จาก",bg="#020617",fg="white").grid(row=1,column=0,padx=10,pady=10)

        currencies = EXORA_database.getcurs()

        codes = [row[1]for row in currencies]

        self.from_var = tk.StringVar()

        ttk.Combobox(form,textvariable=self.from_var,values=codes,state="readonly",width=20).grid(row=1,column=1)

        tk.Label(form,text="จำนวนเงิน",bg="#020617",fg="white").grid(row=2,column=0,padx=10,pady=10)

        self.amount_var = tk.StringVar()

        tk.Entry(form,textvariable=self.amount_var,width=23).grid(row=2,column=1)

        tk.Label(form,text="เป็น",bg="#020617",fg="white").grid(row=3, column=0, padx=10, pady=10)

        self.to_var = tk.StringVar()

        ttk.Combobox(form,textvariable=self.to_var,values=codes,state="readonly",width=20).grid(row=3,column=1 )

        tk.Button(form,text="คำนวณ",bg="#2563eb",fg="white",width=20,command=self.calculate_exchange).grid(row=4,column=0, columnspan=2, pady=25)

        self.result_label = tk.Label(self.main_frame,text="ผลลัพธ์",font=("Arial", 18, "bold"),bg="#020617",fg="#38bdf8")

        self.result_label.pack(pady=20)
    
    def calculate_exchange(self):
        try:
            from_currency = self.from_var.get()
            to_currency = self.to_var.get()
            amount = float(self.amount_var.get())

            if not from_currency or not to_currency:
                raise ValueError("กรุณาเลือกสกุลเงินให้ครบ")

            if amount <= 0:
                raise ValueError("จำนวนเงินต้องมากกว่า 0")

            from_data = EXORA_database.getcur(from_currency)
            to_data = EXORA_database.getcur(to_currency)

            if not from_data or not to_data:
                raise ValueError("ไม่พบข้อมูลสกุลเงิน")

            from_rate = from_data[3]
            to_rate = to_data[4]

            result, rate = EXORA_calculator.calculator(
                self.type_var.get(),
                from_currency,
                to_currency,
                amount,
                from_rate,
                to_rate
            )

            self.pending_exchange = {
                "transaction_type": self.type_var.get(),
                "from_currency": from_currency,
                "from_amount": amount,
                "to_currency": to_currency,
                "to_amount": result,
                "exchange_rate": rate
            }

            self.result_label.config(
                text=(
                    f"{amount:,.2f} {from_currency}\n"
                    f"= {result:,.2f} {to_currency}\n\n"
                    f"อัตราแลกเปลี่ยน: {rate:.6f}"
                )
            )

            if hasattr(self, "exchange_button"):
                self.exchange_button.destroy()

            self.exchange_button = tk.Button(
                self.main_frame,
                text="ดำเนินการแลกเงิน",
                font=("Arial", 12, "bold"),
                bg="#16a34a",
                fg="white",
                command=self.customer_exchange_page
            )
            self.exchange_button.pack(pady=10, ipadx=15, ipady=8)

        except (ValueError, TypeError, IndexError) as e:
            messagebox.showerror("ข้อมูลไม่ถูกต้อง", str(e))
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", str(e))
        
        
    def customer_exchange_page(self):
        data = getattr(self, "pending_exchange", None)

        if not data:
            messagebox.showwarning(
                "แจ้งเตือน",
                "กรุณาคำนวณอัตราแลกเปลี่ยนก่อน"
            )
            return

        self.clear_main()

        tk.Label(
            self.main_frame,
            text="ข้อมูลลูกค้า",
            font=("Arial", 24, "bold"),
            bg="#020617",
            fg="white"
        ).pack(pady=20)

        form = tk.Frame(self.main_frame, bg="#020617")
        form.pack(pady=10)

        tk.Label(
            form, text="ชื่อลูกค้า",
            bg="#020617", fg="white"
        ).grid(row=0, column=0, padx=10, pady=10)

        self.customer_name_entry = tk.Entry(form, width=30)
        self.customer_name_entry.grid(row=0, column=1, padx=10)

        tk.Label(
            form, text="เบอร์โทรศัพท์",
            bg="#020617", fg="white"
        ).grid(row=1, column=0, padx=10, pady=10)

        self.customer_phone_entry = tk.Entry(form, width=30)
        self.customer_phone_entry.grid(row=1, column=1, padx=10)

        tk.Label(
            self.main_frame,
            text=(
                f"รายการ: {data['from_amount']:,.2f} "
                f"{data['from_currency']}\n"
                f"รับเป็น: {data['to_amount']:,.2f} "
                f"{data['to_currency']}"
            ),
            font=("Arial", 15),
            bg="#020617",
            fg="#38bdf8"
        ).pack(pady=15)

        tk.Button(
            self.main_frame,
            text="ตรวจสอบรายการ",
            bg="#2563eb",
            fg="white",
            command=self.review_and_show_qr
        ).pack(pady=10)

        tk.Button(
            self.main_frame,
            text="ย้อนกลับ",
            command=self.exchange_page
        ).pack(pady=5)

    def review_and_show_qr(self):
        name = self.customer_name_entry.get().strip()
        phone = self.customer_phone_entry.get().strip()

        if not name or not phone:
            messagebox.showwarning(
                "ข้อมูลไม่ครบ",
                "กรุณากรอกชื่อและเบอร์โทรศัพท์"
            )
            return

        if not phone.isdigit() or not 9 <= len(phone) <= 10:
            messagebox.showwarning(
                "เบอร์โทรศัพท์ไม่ถูกต้อง",
                "กรุณากรอกเบอร์โทรศัพท์เป็นตัวเลข 9-10 หลัก"
            )
            return

        self.pending_exchange["customer_name"] = name
        self.pending_exchange["customer_phone"] = phone

        self.clear_main()
        data = self.pending_exchange

        tk.Label(
            self.main_frame,
            text="ตรวจสอบรายการก่อนชำระเงิน",
            font=("Arial", 22, "bold"),
            bg="#020617",
            fg="white"
        ).pack(pady=10)

        summary = (
            f"ลูกค้า: {name}\n"
            f"เบอร์โทรศัพท์: {phone}\n\n"
            f"จำนวนเงินที่แลก: {data['from_amount']:,.2f} "
            f"{data['from_currency']}\n"
            f"จำนวนเงินที่จะได้รับ: {data['to_amount']:,.2f} "
            f"{data['to_currency']}\n"
            f"อัตราแลกเปลี่ยน: {data['exchange_rate']:.6f}"
        )

        tk.Label(
            self.main_frame,
            text=summary,
            font=("Arial", 12),
            justify="left",
            bg="#020617",
            fg="white"
        ).pack(pady=10)

        tk.Label(
            self.main_frame,
            text="QR CODE — DEMO ONLY",
            font=("Arial", 14, "bold"),
            bg="#020617",
            fg="#38bdf8"
        ).pack(pady=5)

        canvas = tk.Canvas(
            self.main_frame,
            width=180,
            height=180,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cbd5e1"
        )
        canvas.pack(pady=5)

        # วาดลวดลาย QR จำลอง ไม่ใช่ QR ที่สแกนชำระเงินจริง
        cell = 10
        pattern = [
            "1111111001011",
            "1000001011101",
            "1011101000101",
            "1011101011101",
            "1011101001001",
            "1000001010111",
            "1111111010101",
            "0000000001010",
            "1101011100111",
            "0110100111000",
            "1011101010110",
            "0100110101101",
            "1110101110011"
        ]

        offset = 25
        for row, line in enumerate(pattern):
            for col, bit in enumerate(line):
                if bit == "1":
                    x1 = offset + col * cell
                    y1 = offset + row * cell
                    canvas.create_rectangle(
                        x1, y1,
                        x1 + cell, y1 + cell,
                        fill="black",
                        outline="black"
                    )

        tk.Label(
            self.main_frame,
            text="QR นี้เป็นภาพตัวอย่าง ไม่สามารถใช้ชำระเงินจริงได้",
            bg="#020617",
            fg="#fbbf24"
        ).pack(pady=5)

        tk.Button(
            self.main_frame,
            text="ยืนยันการชำระเงิน (จำลอง)",
            font=("Arial", 12, "bold"),
            bg="#16a34a",
            fg="white",
            relief="flat",
            command=self.confirm_demo_payment
        ).pack(pady=10, ipadx=10, ipady=6)

        tk.Button(
            self.main_frame,
            text="ยกเลิก",
            bg="#334155",
            fg="white",
            command=self.exchange_page
        ).pack(pady=5)

        
    def confirm_demo_payment(self):
        data = getattr(self, "pending_exchange", None)

        if not data:
            messagebox.showerror(
                "ไม่พบรายการ",
                "กรุณาเริ่มทำรายการใหม่"
            )
            return

        try:
            transaction_no = (
                "TX" + datetime.now().strftime("%Y%m%d%H%M%S%f")
            )

            saved = EXORA_database.save_transaction(
                transaction_no,
                self.current_user["id"],
                data["transaction_type"],
                data["from_currency"],
                data["from_amount"],
                data["to_currency"],
                data["to_amount"],
                data["exchange_rate"],
                data["customer_name"],
                data["customer_phone"]
            )

            if saved:
                self.pending_exchange = None

                messagebox.showinfo(
                    "ทำรายการสำเร็จ (จำลอง)",
                    f"บันทึกรายการเรียบร้อย\n"
                    f"เลขที่รายการ: {transaction_no}\n\n"
                    "หมายเหตุ: ระบบไม่ได้ตรวจสอบการชำระเงินจริง"
                )

                self.exchange_page()

        except Exception as e:
            messagebox.showerror(
                "บันทึกรายการไม่สำเร็จ",
                f"เกิดข้อผิดพลาด:\n{e}"
            )


    def history_page(self):
        self.clear_main()

        tk.Label(self.main_frame,text="📋 ประวัติรายการ",font=("Arial", 26, "bold"),bg="#020617",fg="white").pack(pady=25)

        search_frame = tk.Frame(self.main_frame,bg="#020617")

        search_frame.pack()

        self.search_var = tk.StringVar()

        tk.Entry(search_frame,textvariable=self.search_var,width=35).pack(side="left",padx=5)

        tk.Button(search_frame,text="ค้นหา", command=self.load_history).pack(side="left")

        columns = ("no","user","type","from","amount","to","result","rate","date")

        self.history_tree = ttk.Treeview(self.main_frame,columns=columns,show="headings")

        headings = ["Transaction","User","Type","From","Amount","To","Result","Rate","Date"]

        for col, heading in zip(columns,headings):
            self.history_tree.heading(col,text=heading)

        self.history_tree.pack(fill="both",expand=True,padx=20,pady=20)

        self.load_history()

    def load_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        search = self.search_var.get()
        data = EXORA_database.get_transactions(search)

        for row in data:
            self.history_tree.insert("","end",values=row)

    def user_management(self):
        self.clear_main()

        tk.Label(self.main_frame,text="จัดการผู้ใช้งาน",font=("Arial", 26, "bold"),bg="#020617",fg="white").pack(pady=25)

        form = tk.Frame(self.main_frame,bg="#020617")
        form.pack(pady=10)

        tk.Label(form,text="Username",bg="#020617",fg="white").grid(row=0,column=0)

        username = tk.Entry(form)
        username.grid(row=0, column=1, padx=10)

        tk.Label(form,text="Password",bg="#020617",fg="white").grid(row=1,column=0)

        password = tk.Entry(form,show="*")
        password.grid(row=1, column=1, padx=10)

        role = ttk.Combobox(form,values=["staff","admin"],state="readonly")
        role.set("staff")

        role.grid(row=2,column=1,pady=5)

        def add():
            if not username.get() or not password.get():
                messagebox.showwarning(
                    "ข้อมูลไม่ครบ",
                    "กรุณากรอกข้อมูลให้ครบ"
                )
                return

            success = EXORA_database.adduser(
                username.get(),
                password.get(),
                role.get()
            )

            if success:
                messagebox.showinfo(
                    "สำเร็จ",
                    "เพิ่มผู้ใช้งานแล้ว"
                )

                self.user_management()

            else:
                messagebox.showerror(
                    "ผิดพลาด",
                    "Username นี้มีอยู่แล้ว"
                )

        tk.Button(form,text="เพิ่มผู้ใช้",command=add).grid(row=3,column=0,columnspan=2,pady=10)

        columns = ("id","username","role")

        tree = ttk.Treeview(self.main_frame,columns=columns,show="headings")

        for col in columns:
            tree.heading(col,text=col)

        tree.pack(fill="both",expand=True,padx=30,pady=20)

        for row in EXORA_database.user():
            tree.insert("","end",values=row)

    def clear_main(self):
        if hasattr(self,"main_frame"):
            for widget in self.main_frame.winfo_children():
                widget.destroy()

        self.currency_page = None

    def logout(self):
        self.current_user = None
        self.login_page()
'''