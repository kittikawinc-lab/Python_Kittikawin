
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os
import EXORA_database
import EXORA_calculator
from EXORA_currency_page import CurrencyPage


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("EXORA | Currency Exchange Management System")

        self.root.geometry("1280x800")

        self.root.minsize(1080,700)
        self.root.configure(bg="#f3f6fb")
        self.configure_styles()

        self.current_user = None

        self.currency_page = None

        self.login_page()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.currency_page = None

    def configure_styles(self):
        """ตั้งค่าธีม EXORA ให้สม่ำเสมอ โดยไม่เปลี่ยนการทำงานของระบบ"""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background="#ffffff", foreground="#20324d",
                        fieldbackground="#ffffff", rowheight=32, font=("Arial", 10), borderwidth=0)
        style.configure("Treeview.Heading", background="#e7eef8", foreground="#17345d",
                        font=("Arial", 10, "bold"), padding=(9, 9), relief="flat")
        style.map("Treeview", background=[("selected", "#d8e8ff")],
                  foreground=[("selected", "#17345d")])
        style.configure("TCombobox", padding=7, fieldbackground="#ffffff",
                        background="#ffffff", foreground="#20324d", arrowcolor="#2563eb")
        style.map("TCombobox", fieldbackground=[("readonly", "#ffffff")])

    def apply_theme(self):
        sidebar = getattr(self, "sidebar_frame", None)

        def in_sidebar(widget):
            current = widget
            while current is not None:
                if sidebar is not None and current == sidebar:
                    return True
                parent_name = current.winfo_parent()
                if not parent_name:
                    break
                try:
                    current = current._nametowidget(parent_name)
                except (KeyError, tk.TclError):
                    break
            return False

        def walk(parent):
            for widget in parent.winfo_children():
                try:
                    kind = widget.winfo_class()
                    side = in_sidebar(widget)
                    if kind in ("Frame", "Labelframe"):
                        old_bg = widget.cget("bg")
                        if side:
                            widget.configure(bg="#10213b")
                        elif old_bg in ("#020617", "#0f172a", "#10213b"):
                            widget.configure(bg="#ffffff" if old_bg == "#0f172a" else "#f3f6fb")
                    elif kind == "Label":
                        old_bg = widget.cget("bg")
                        old_fg = widget.cget("fg")
                        if side:
                            widget.configure(bg="#10213b")
                            if old_fg not in ("#38bdf8", "#93c5fd", "#fbbf24"):
                                widget.configure(fg="#eaf1ff")
                        else:
                            if old_bg in ("#020617", "#0f172a", "#10213b"):
                                widget.configure(bg="#ffffff" if old_bg == "#0f172a" else "#f3f6fb")
                            if old_fg == "white":
                                widget.configure(fg="#20324d")
                            elif old_fg == "#94a3b8":
                                widget.configure(fg="#64748b")
                            elif old_fg == "#cbd5e1":
                                widget.configure(fg="#475569")
                            elif old_fg == "#38bdf8":
                                widget.configure(fg="#1769e0")
                            elif old_fg == "#fbbf24":
                                widget.configure(fg="#a16207")
                    elif kind == "Button":
                        old_bg = widget.cget("bg")
                        if side:
                            if old_bg not in ("#2563eb", "#16a34a", "#dc2626"):
                                widget.configure(bg="#1b3457", fg="#ffffff",
                                                 activebackground="#294b78", activeforeground="#ffffff")
                        else:
                            if old_bg in ("#020617", "#0f172a", "#334155", "#20335b"):
                                widget.configure(bg="#e7eef8", fg="#17345d",
                                                 activebackground="#d5e4f7", activeforeground="#17345d")
                            elif old_bg in ("#2563eb", "#1d4ed8"):
                                widget.configure(bg="#1769e0", fg="#ffffff",
                                                 activebackground="#0f55bd", activeforeground="#ffffff")
                            elif old_bg == "#16a34a":
                                widget.configure(bg="#15803d", fg="#ffffff",
                                                 activebackground="#166534", activeforeground="#ffffff")
                        widget.configure(font=("Arial", 10, "bold"), relief="flat",
                                         cursor="hand2", padx=10, pady=7, borderwidth=0)
                    elif kind == "Entry":
                        widget.configure(bg="#ffffff", fg="#20324d", insertbackground="#1769e0",
                                         relief="solid", bd=1, highlightthickness=1,
                                         highlightbackground="#d6e0ed", highlightcolor="#1769e0",
                                         font=("Arial", 11))
                    elif kind == "Checkbutton":
                        if side:
                            widget.configure(bg="#10213b", fg="#eaf1ff",
                                             selectcolor="#1b3457",
                                             activebackground="#10213b",
                                             activeforeground="#ffffff")
                        else:
                            widget.configure(bg="#ffffff", fg="#20324d",
                                             selectcolor="#e7eef8",
                                             activebackground="#ffffff",
                                             activeforeground="#17345d")
                        widget.configure(font=("Arial", 10))
                    walk(widget)
                except (tk.TclError, AttributeError):
                    pass

        walk(self.root)

    '''
    def login_page(self):
        self.clear_window()
        frame = tk.Frame(self.root,bg="#020617")
        frame.pack(fill="both",expand=True)

        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "EXORA_assets",
            "login_bg.jpg"
        )

        self.login_bg_photo = None

        if os.path.exists(image_path):
            try:
                bg_image = Image.open(image_path)

                # ปรับภาพตามขนาดหน้าต่าง
                bg_image = bg_image.resize(
                    (1280, 800),
                    Image.Resampling.LANCZOS
                )

                self.login_bg_photo = ImageTk.PhotoImage(
                    bg_image
                )

                self.login_bg_label = tk.Label(
                    frame,
                    image=self.login_bg_photo,
                    bd=0
                )

                self.login_bg_label.place(
                    x=0, y=0,
                    relwidth=1,
                    relheight=1
                )

                # ให้ภาพอยู่ด้านหลังฟอร์ม
                self.login_bg_label.lower()

            except Exception as error:
                print("โหลดภาพพื้นหลังไม่สำเร็จ:", error)


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
        self.apply_theme()
    '''

    def login_page(self):
     self.clear_window()

     frame = tk.Frame(self.root, bg="#020617")
     frame.pack(fill="both", expand=True)
     
     image_path = os.path.join(
         os.path.dirname(os.path.abspath(__file__)),
         "EXORA_assets",
         "login_bg.jpg"
     )

     self.login_bg_photo = None

     if os.path.exists(image_path):
         try:
             bg_image = Image.open(image_path)

             self.login_bg_photo = ImageTk.PhotoImage(
                 bg_image.resize(
                     (1280, 800),
                     Image.Resampling.LANCZOS
                 )
             )

             self.login_bg_label = tk.Label(
                 frame,
                 image=self.login_bg_photo,
                 bd=0
             )
             self.login_bg_label.place(
                 x=0, y=0,
                 relwidth=1,
                 relheight=1
             )
             self.login_bg_label.lower()

         except Exception as error:
             print("โหลดภาพพื้นหลังไม่สำเร็จ:", error)
     else:
         print("ไม่พบไฟล์ภาพพื้นหลัง:", image_path)

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
     self.apply_theme()


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
            
            frame = tk.Frame(self.root, bg="#071B3A")
            frame.pack(fill="both", expand=True)

            image_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "EXORA_assets",
                "login_bg.jpg"
            )

            self.login_bg_photo = None

            if os.path.exists(image_path):
                try:
                    bg_image = Image.open(image_path)

                    self.login_bg_photo = ImageTk.PhotoImage(
                        bg_image.resize(
                            (1280, 800),
                            Image.Resampling.LANCZOS
                        )
                    )

                    self.login_bg_label = tk.Label(
                        frame,
                        image=self.login_bg_photo,
                        bd=0
                    )
                    self.login_bg_label.place(
                        x=0, y=0,
                        relwidth=1,
                        relheight=1
                    )
                    self.login_bg_label.lower()

                except Exception as error:
                    print("โหลดภาพพื้นหลังไม่สำเร็จ:", error)
            else:
                print("ไม่พบไฟล์ภาพพื้นหลัง:", image_path)

            # ===== กล่องฟอร์ม Login =====
            form = tk.Frame(
                frame,
                bg="#0F172A",
                padx=32,
                pady=24,
                highlightbackground="#2563EB",
                highlightthickness=1
            )
            form.pack()


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
            self.apply_theme()

    
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
            self.apply_theme()

    
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

        sidebar = tk.Frame(self.root,width=238,bg="#10213b")
        self.sidebar_frame = sidebar

        sidebar.pack(side="left",fill="y")

        sidebar.pack_propagate(False)

        tk.Label(sidebar,text="EXORA\nCURRENCY EXCHANGE",font=("Arial", 14, "bold"),fg="white",bg="#10213b").pack(pady=30)

        tk.Label( sidebar,text=(f"{self.current_user['username']}\n"f"Role: {self.current_user['role']}"),fg="#94a3b8",bg="#0f172a").pack(pady=10)

        self.create_menu_button(sidebar,"หน้าหลัก",self.dashboard_home)

        self.create_menu_button(sidebar,"แลกเปลี่ย" \
        "นเงิน",self.exchange_page)

        self.create_menu_button(sidebar,"ประวัติรายการ",self.history_page)

        if self.current_user["role"] == "admin":
            self.create_menu_button(sidebar,"ค่าเงิน",self.currency_management)

            self.create_menu_button(sidebar,"ผู้ใช้งาน",self.user_management)

        self.create_menu_button(sidebar,"Logout",self.logout)

        self.main_frame = tk.Frame(self.root,bg="#020617")

        self.main_frame.pack(side="right",fill="both",expand=True)

        self.dashboard_home()
        self.apply_theme()

    def create_menu_button(self,parent,text,command):
        tk.Button(parent,text=text,font=("Arial", 11, "bold"),anchor="w",padx=20,pady=13,bg="#10213b",fg="#eaf1ff",activebackground="#24436e",activeforeground="white",relief="flat",cursor="hand2",borderwidth=0,command=command).pack(fill="x")

    def dashboard_home(self):
        self.clear_main()

        self.main_frame.configure(bg="#071B3A")

        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "EXORA_assets",
            "dashboard_bg.jpg"
        )

        self.dashboard_bg_label = tk.Label(
            self.main_frame,
            bg="#071B3A",
            bd=0
        )
        self.dashboard_bg_label.place(
            x=0, y=0,
            relwidth=1,
            relheight=1
        )
        self.dashboard_bg_label.lower()

        self.dashboard_bg_original = None
        self.dashboard_bg_photo = None

        if os.path.exists(image_path):
            try:
                self.dashboard_bg_original = Image.open(image_path).convert("RGB")

                def resize_dashboard_bg(event):
                    if event.widget != self.main_frame:
                        return

                    width = event.width
                    height = event.height

                    if width <= 1 or height <= 1:
                        return

                    resized = self.dashboard_bg_original.resize(
                        (width, height),
                        Image.Resampling.LANCZOS
                    )

                    self.dashboard_bg_photo = ImageTk.PhotoImage(resized)
                    self.dashboard_bg_label.configure(
                        image=self.dashboard_bg_photo
                    )

                self.main_frame.bind(
                    "<Configure>",
                    resize_dashboard_bg
                )

            except Exception as error:
                print("โหลดภาพพื้นหลัง Dashboard ไม่สำเร็จ:", error)

        else:
            print("ไม่พบภาพพื้นหลัง Dashboard:", image_path)

        content = tk.Frame(
            self.main_frame,
            bg="#0B2547",
            padx=28,
            pady=24
        )
        content.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=28
        )

        tk.Label(
            content,
            text="EXORA",
            font=("Arial", 15, "bold"),
            bg="#0B2547",
            fg="#38BDF8"
        ).pack(anchor="w")

        tk.Label(
            content,
            text="CURRENCY EXCHANGE",
            font=("Arial", 25, "bold"),
            bg="#0B2547",
            fg="white"
        ).pack(anchor="w", pady=(8, 4))

        tk.Label(
            content,
            text="EXCHANGE SMARTER. MANAGE BETTER.",
            font=("Arial", 11, "bold"),
            bg="#0B2547",
            fg="#7DD3FC"
        ).pack(anchor="w", pady=(0, 18))

        intro = tk.Frame(
            content,
            bg="#16345A",
            padx=22,
            pady=18,
            highlightbackground="#2563EB",
            highlightthickness=1
        )
        intro.pack(fill="x", pady=(0, 20))

        tk.Label(
            intro,
            text="ยินดีต้อนรับเข้าสู่ EXORA",
            font=("Arial", 18, "bold"),
            bg="#16345A",
            fg="white"
        ).pack(anchor="w", pady=(0, 10))

        description = (
            "ระบบบริหารจัดการร้านแลกเปลี่ยนเงินตราต่างประเทศ "
            "ที่ช่วยให้พนักงานดำเนินรายการได้สะดวกและเป็นระบบ\n\n"
            "EXORA ช่วยคำนวณจำนวนเงินที่ลูกค้าจะได้รับ "
            "ตรวจสอบอัตราแลกเปลี่ยน และบันทึกประวัติรายการ "
            "เพื่อให้สามารถตรวจสอบข้อมูลย้อนหลังได้"
        )

        tk.Label(
            intro,
            text=description,
            font=("Tahoma", 11),
            bg="#16345A",
            fg="#E2E8F0",
            justify="left",
            anchor="w",
            wraplength=780
        ).pack(fill="x")

        # ===== กล่องแนะนำความสามารถ =====
        tk.Label(
            content,
            text="ความสามารถของระบบ",
            font=("Arial", 17, "bold"),
            bg="#0B2547",
            fg="white"
        ).pack(anchor="w", pady=(0, 12))

        features = tk.Frame(content, bg="#0B2547")
        features.pack(fill="x", pady=(0, 20))

        feature_data = [
            (
                "01",
                "แลกเปลี่ยนเงิน",
                "เลือกสกุลเงิน ระบุจำนวนเงิน\nและคำนวณยอดเงินที่ได้รับ"
            ),
            (
                "02",
                "ประวัติรายการ",
                "ค้นหาและตรวจสอบข้อมูล\nรายการแลกเปลี่ยนย้อนหลัง"
            ),
            (
                "03",
                "จัดการอัตราแลกเปลี่ยน",
                "ตรวจสอบและจัดการข้อมูล\nอัตราแลกเปลี่ยนตามสิทธิ์"
            )
        ]

        for number, title, detail in feature_data:
            card = tk.Frame(
                features,
                bg="#16345A",
                padx=14,
                pady=16,
                highlightbackground="#28527F",
                highlightthickness=1
            )
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 10)
            )

            tk.Label(
                card,
                text=number,
                font=("Arial", 20, "bold"),
                bg="#16345A",
                fg="#38BDF8"
            ).pack(anchor="w")

            tk.Label(
                card,
                text=title,
                font=("Tahoma", 11, "bold"),
                bg="#16345A",
                fg="white",
                wraplength=200,
                justify="left"
            ).pack(anchor="w", pady=(8, 6))

            tk.Label(
                card,
                text=detail,
                font=("Tahoma", 9),
                bg="#16345A",
                fg="#CBD5E1",
                justify="left",
                wraplength=200
            ).pack(anchor="w")

        tk.Label(
            content,
            text=(
                f"ผู้ใช้งาน: {self.current_user['username']}   |   "
                f"สิทธิ์: {self.current_user['role']}"
            ),
            font=("Tahoma", 10, "bold"),
            bg="#0B2547",
            fg="#7DD3FC"
        ).pack(anchor="w", pady=(5, 0))



    def currency_management(self):
        self.clear_main()

        self.currency_page = CurrencyPage(self.main_frame)

        self.currency_page.show()
        self.apply_theme()


    
    def exchange_page(self):
        self.clear_main()

        self.main_frame.configure(bg="#071B3A")

        bg_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "EXORA_assets",
            "exchange_bg.jpg"
        )

        self.exchange_bg_label = tk.Label(
            self.main_frame,
            bg="#071B3A",
            bd=0
        )
        self.exchange_bg_label.place(
            x=0, y=0, relwidth=1, relheight=1
        )
        self.exchange_bg_label.lower()

        try:
            self.exchange_bg_original = Image.open(bg_path).convert("RGB")

            def resize_exchange_background(event):
                if event.width <= 1 or event.height <= 1:
                    return

                resized = self.exchange_bg_original.resize(
                    (event.width, event.height),
                    Image.Resampling.LANCZOS
                )

                self.exchange_bg_photo = ImageTk.PhotoImage(resized)
                self.exchange_bg_label.configure(
                    image=self.exchange_bg_photo
                )

            self.main_frame.bind(
                "<Configure>",
                resize_exchange_background
            )

            self.main_frame.update_idletasks()
            resize_exchange_background(
                type("Event", (), {
                    "width": max(self.main_frame.winfo_width(), 1),
                    "height": max(self.main_frame.winfo_height(), 1)
                })()
            )

        except Exception as e:
            print(f"ไม่สามารถโหลดภาพพื้นหลัง Exchange: {e}")

        page = tk.Frame(
            self.main_frame,
            bg="#0B2547",
            padx=28,
            pady=22
        )
        page.pack(fill="both", expand=True, padx=24, pady=20)

        header = tk.Frame(page, bg="#0B2547")
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header,
            text="EXORA  /  EXCHANGE",
            font=("Arial", 10, "bold"),
            bg="#0B2547",
            fg="#38BDF8"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="แลกเปลี่ยนเงินตราต่างประเทศ",
            font=("Tahoma", 20, "bold"),
            bg="#0B2547",
            fg="#FFFFFF"
        ).pack(anchor="w", pady=(3, 2))

        tk.Label(
            header,
            text="Foreign Currency Exchange",
            font=("Arial", 11),
            bg="#0B2547",
            fg="#A8BCD8"
        ).pack(anchor="w")

        tk.Frame(
            page,
            bg="#244568",
            height=1
        ).pack(fill="x", pady=(0, 5))

        body = tk.Frame(page, bg="#0B2547")
        body.pack(fill="both", expand=True)

        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        form_card = tk.Frame(
            body,
            bg="#102D50",
            padx=22,
            pady=12,
            highlightbackground="#315579",
            highlightthickness=1
        )
        form_card.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 8)
        )

        tk.Label(
            form_card,
            text="รายละเอียดรายการ",
            font=("Tahoma", 15, "bold"),
            bg="#102D50",
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            form_card,
            text="กรอกข้อมูลเพื่อคำนวณยอดเงินที่ต้องการแลก",
            font=("Tahoma", 9),
            bg="#102D50",
            fg="#A8BCD8"
        ).pack(anchor="w", pady=(5, 12))

        style = ttk.Style()
        style.configure(
            "EXORA.TCombobox",
            padding=8,
            font=("Arial", 11)
        )

        def add_field(title, hint=None):
            tk.Label(
                form_card,
                text=title,
                font=("Tahoma", 10, "bold"),
                bg="#102D50",
                fg="#DCE8F7"
            ).pack(anchor="w", pady=(2, 1))

            if hint:
                tk.Label(
                    form_card,
                    text=hint,
                    font=("Tahoma", 8),
                    bg="#102D50",
                    fg="#8FAACB"
                ).pack(anchor="w", pady=(0, 4))

        add_field("ประเภทการแลกเงิน")

        self.type_var = tk.StringVar(value="BUY")

        type_combo = ttk.Combobox(
            form_card,
            textvariable=self.type_var,
            values=["BUY", "SELL"],
            state="readonly",
            style="EXORA.TCombobox",
            font=("Arial", 11)
        )
        type_combo.pack(fill="x", ipady=2)

        tk.Label(
            form_card,
            text="BUY = รับซื้อเงินตรา  |  SELL = ขายเงินตรา",
            font=("Tahoma", 8),
            bg="#102D50",
            fg="#8FAACB"
        ).pack(anchor="w", pady=(3, 2))

        add_field("สกุลเงินต้นทาง", "สกุลเงินที่ใช้ในการทำรายการ")

        currencies = EXORA_database.getcurs()
        codes = [row[1] for row in currencies]

        self.from_var = tk.StringVar()

        from_combo = ttk.Combobox(
            form_card,
            textvariable=self.from_var,
            values=codes,
            state="readonly",
            style="EXORA.TCombobox",
            font=("Arial", 11)
        )
        from_combo.pack(fill="x", ipady=2)

        add_field("จำนวนเงิน", "ระบุจำนวนเงินที่ต้องการแลก")

        self.amount_var = tk.StringVar()

        amount_entry = tk.Entry(
            form_card,
            textvariable=self.amount_var,
            font=("Arial", 15, "bold"),
            bg="#071B3A",
            fg="#FFFFFF",
            insertbackground="#38BDF8",
            relief="flat",
            bd=0
        )
        amount_entry.pack(fill="x", ipady=10, pady=(0, 4))

        add_field("สกุลเงินปลายทาง", "สกุลเงินที่ต้องการรับ")

        self.to_var = tk.StringVar()

        to_combo = ttk.Combobox(
            form_card,
            textvariable=self.to_var,
            values=codes,
            state="readonly",
            style="EXORA.TCombobox",
            font=("Arial", 11)
        )
        to_combo.pack(fill="x", ipady=2)

        tk.Button(
            form_card,
            text="คำนวณอัตราแลกเปลี่ยน  →",
            font=("Tahoma", 11, "bold"),
            bg="#0284C7",
            fg="white",
            activebackground="#0369A1",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.calculate_exchange
        ).pack(fill="x", pady=(20, 4), ipady=11)

        result_card = tk.Frame(
            body,
            bg="#102D50",
            padx=22,
            pady=22,
            highlightbackground="#315579",
            highlightthickness=1
        )
        result_card.grid(
            row=0, column=1,
            sticky="nsew",
            padx=(12, 0)
        )

        tk.Label(
            result_card,
            text="EXCHANGE SUMMARY",
            font=("Arial", 10, "bold"),
            bg="#102D50",
            fg="#38BDF8"
        ).pack(anchor="w")

        tk.Label(
            result_card,
            text="สรุปยอดแลกเปลี่ยน",
            font=("Tahoma", 16, "bold"),
            bg="#102D50",
            fg="white"
        ).pack(anchor="w", pady=(7, 18))

        result_box = tk.Frame(
            result_card,
            bg="#071B3A",
            padx=16,
            pady=22
        )
        result_box.pack(fill="x")

        tk.Label(
            result_box,
            text="จำนวนเงินที่ได้รับ",
            font=("Tahoma", 10),
            bg="#071B3A",
            fg="#A8BCD8"
        ).pack(anchor="w")

        self.result_label = tk.Label(
            result_box,
            text="รอการคำนวณ",
            font=("Tahoma", 17, "bold"),
            bg="#071B3A",
            fg="#38BDF8",
            justify="left",
            wraplength=270
        )
        self.result_label.pack(anchor="w", pady=(12, 4))

        self.exchange_button = tk.Button(
            result_card,
            text="ดำเนินการแลกเงิน",
            font=("Arial", 12, "bold"),
            bg="#00C2FF",
            fg="#071B3A",
            activebackground="#38D9FF",
            activeforeground="#071B3A",
            cursor="hand2",
            relief="flat",
            padx=20,
            pady=10,
            command=self.customer_exchange_page
        )

        self.exchange_button.pack(
            side="bottom",
            fill="x",
            padx=30,
            pady=15
        )

        tk.Frame(
            result_card,
            bg="#315579",
            height=1
        ).pack(fill="x", pady=14)
        '''
        tk.Label(
            result_card,
            text="โปรดตรวจสอบข้อมูลก่อนยืนยันรายการทุกครั้ง",
            font=("Tahoma", 8),
            bg="#102D50",
            fg="#FBBF24",
            wraplength=280,
            justify="left"
        ).pack(anchor="w", pady=(12, 0))
        '''
        self.apply_theme()
    
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

            self.exchange_button.config(
                state="normal",
                bg="#16A34A",
                fg="white"
            )

            self.apply_theme()

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

        # สีหลักของ EXORA
        bg = "#07182E"
        card_bg = "#102844"
        field_bg = "#F8FAFC"
        primary = "#38BDF8"
        muted = "#B8C7D9"
        green = "#22C55E"

        self.main_frame.configure(bg=bg)

        # ---------- ส่วนหัว ----------
        header = tk.Frame(self.main_frame, bg=bg)
        header.pack(fill="x", padx=34, pady=(22, 12))

        tk.Label(
            header,
            text="EXORA  |  CURRENCY EXCHANGE",
            font=("Arial", 10, "bold"),
            bg=bg,
            fg=primary
        ).pack(anchor="w")

        tk.Label(
            header,
            text="ข้อมูลลูกค้า",
            font=("Tahoma", 24, "bold"),
            bg=bg,
            fg="white"
        ).pack(anchor="w", pady=(8, 3))

        tk.Label(
            header,
            text="กรอกข้อมูลและตรวจสอบรายละเอียดก่อนยืนยันรายการ",
            font=("Tahoma", 10),
            bg=bg,
            fg=muted,
            wraplength=680,
            justify="left"
        ).pack(anchor="w")

        # ---------- พื้นที่เนื้อหา ----------
        content = tk.Frame(self.main_frame, bg=bg)
        content.pack(
            fill="both",
            expand=True,
            padx=34,
            pady=(4, 20)
        )

        # ---------- การ์ดข้อมูลลูกค้า ----------
        form_card = tk.Frame(
            content,
            bg=card_bg,
            highlightbackground="#294766",
            highlightthickness=1
        )
        form_card.pack(fill="x", pady=(0, 14))

        tk.Label(
            form_card,
            text="ข้อมูลติดต่อ",
            font=("Tahoma", 14, "bold"),
            bg=card_bg,
            fg="white"
        ).pack(anchor="w", padx=22, pady=(18, 3))

        tk.Label(
            form_card,
            text="กรุณากรอกข้อมูลให้ถูกต้อง",
            font=("Tahoma", 9),
            bg=card_bg,
            fg=muted
        ).pack(anchor="w", padx=22, pady=(0, 14))

        fields = tk.Frame(form_card, bg=card_bg)
        fields.pack(fill="x", padx=22, pady=(0, 18))
        fields.grid_columnconfigure(0, weight=1)
        fields.grid_columnconfigure(1, weight=1)

        tk.Label(
            fields,
            text="ชื่อลูกค้า *",
            font=("Tahoma", 10, "bold"),
            bg=card_bg,
            fg="#E5EDF7"
        ).grid(
            row=0, column=0,
            sticky="w", padx=(0, 12), pady=(0, 7)
        )

        tk.Label(
            fields,
            text="เบอร์โทรศัพท์ *",
            font=("Tahoma", 10, "bold"),
            bg=card_bg,
            fg="#E5EDF7"
        ).grid(
            row=0, column=1,
            sticky="w", padx=(12, 0), pady=(0, 7)
        )

        self.customer_name_entry = tk.Entry(
            fields,
            font=("Tahoma", 11),
            bg=field_bg,
            fg="#0F172A",
            relief="flat",
            insertbackground="#0F172A"
        )
        self.customer_name_entry.grid(
            row=1, column=0,
            sticky="ew", padx=(0, 12), ipady=9
        )

        self.customer_phone_entry = tk.Entry(
            fields,
            font=("Tahoma", 11),
            bg=field_bg,
            fg="#0F172A",
            relief="flat",
            insertbackground="#0F172A"
        )
        self.customer_phone_entry.grid(
            row=1, column=1,
            sticky="ew", padx=(12, 0), ipady=9
        )

        tk.Label(
            form_card,
            text="กรุณาตรวจสอบข้อมูลก่อนดำเนินการต่อ",
            font=("Tahoma", 9),
            bg=card_bg,
            fg="#A7F3D0"
        ).pack(anchor="w", padx=22, pady=(0, 18))

        # ---------- การ์ดสรุปรายการแลกเงิน ----------
        summary_card = tk.Frame(
            content,
            bg="#F8FAFC",
            highlightbackground="#D7E2EE",
            highlightthickness=1
        )
        summary_card.pack(fill="x", pady=(0, 14))

        tk.Label(
            summary_card,
            text="สรุปรายการแลกเปลี่ยน",
            font=("Tahoma", 14, "bold"),
            bg="#F8FAFC",
            fg="#102844"
        ).pack(anchor="w", padx=22, pady=(16, 10))

        amounts = tk.Frame(summary_card, bg="#F8FAFC")
        amounts.pack(fill="x", padx=22, pady=(0, 12))
        amounts.grid_columnconfigure(0, weight=1)
        amounts.grid_columnconfigure(1, weight=1)

        tk.Label(
            amounts,
            text="จำนวนเงินต้นทาง",
            font=("Tahoma", 9),
            bg="#F8FAFC",
            fg="#64748B"
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            amounts,
            text=f"{data['from_amount']:,.2f} {data['from_currency']}",
            font=("Arial", 15, "bold"),
            bg="#F8FAFC",
            fg="#102844"
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        tk.Label(
            amounts,
            text="จำนวนเงินที่คาดว่าจะได้รับ",
            font=("Tahoma", 9),
            bg="#F8FAFC",
            fg="#64748B"
        ).grid(row=0, column=1, sticky="w", padx=(14, 0))

        tk.Label(
            amounts,
            text=f"{data['to_amount']:,.2f} {data['to_currency']}",
            font=("Arial", 15, "bold"),
            bg="#F8FAFC",
            fg="#047857"
        ).grid(row=1, column=1, sticky="w", padx=(14, 0), pady=(4, 0))

        tk.Frame(
            summary_card,
            bg="#D7E2EE",
            height=1
        ).pack(fill="x", padx=22)

        tk.Label(
            summary_card,
            text=(
                f"อัตราแลกเปลี่ยนที่ใช้: "
                f"1 {data['from_currency']} = "
                f"{data['exchange_rate']:.6f} "
                f"{data['to_currency']}"
            ),
            font=("Tahoma", 10, "bold"),
            bg="#F8FAFC",
            fg="#334155"
        ).pack(anchor="w", padx=22, pady=(10, 4))

        tk.Label(
            summary_card,
            text="โปรดตรวจสอบจำนวนเงินและอัตราแลกเปลี่ยนก่อนดำเนินการต่อ",
            font=("Tahoma", 9),
            bg="#F8FAFC",
            fg="#B45309",
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 16))

        # ---------- ปุ่มดำเนินการ ----------
        actions = tk.Frame(content, bg=bg)
        actions.pack(fill="x", pady=(2, 0))

        tk.Button(
            actions,
            text="ตรวจสอบรายการต่อ  →",
            font=("Tahoma", 11, "bold"),
            bg=green,
            fg="#052E16",
            activebackground="#4ADE80",
            activeforeground="#052E16",
            relief="flat",
            cursor="hand2",
            command=self.review_and_show_qr
        ).pack(fill="x", ipady=10, pady=(0, 8))

        tk.Button(
            actions,
            text="← กลับไปแก้ไขรายการแลกเงิน",
            font=("Tahoma", 10),
            bg="#1E3551",
            fg="#E2E8F0",
            activebackground="#294766",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.exchange_page
        ).pack(fill="x", ipady=7)

        # ---------- ข้อความท้ายหน้า ----------
        tk.Label(
            content,
            text="EXORA  •  โปรดดูแลข้อมูลติดต่อของคุณ",
            font=("Tahoma", 8),
            bg=bg,
            fg="#8296AD"
        ).pack(pady=(12, 0))

        self.apply_theme()



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
        self.apply_theme()


        
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
        self.apply_theme()


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
        self.apply_theme()


    def clear_main(self):
        if hasattr(self,"main_frame"):
            for widget in self.main_frame.winfo_children():
                widget.destroy()

        self.currency_page = None

    def logout(self):
        self.current_user = None
        self.login_page()
