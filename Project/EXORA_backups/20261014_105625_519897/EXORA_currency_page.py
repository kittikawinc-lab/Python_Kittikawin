import tkinter as tk
from tkinter import ttk, messagebox
import EXORA_database
import EXORA_api

class CurrencyPage:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, bg="#f3f6fb")
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.frame, text="อัตราแลกเปลี่ยนเงินตรา", font=("Arial", 24, "bold"),fg="#17345d", bg="#f3f6fb")
        title.pack(pady=(20, 5))

        subtitle = tk.Label(self.frame, text="ข้อมูลอัตราการแลกเปลี่ยน", font=("Arial", 11),fg="#17345d", bg="#f3f6fb")
        subtitle.pack(pady=(20, 5))

        self.update_button = tk.Button(self.frame, text="อัปเดตค่าเงิน", font=("Arial", 12, "bold"),fg="white", bg="#1769e0", activebackground="#0f55bd", activeforeground="white", relief="flat", padx=20, pady=10, command=self.update_api)
        self.update_button.pack(pady=10, ipadx=8, ipady=2)

        self.last_update = tk.Label(self.frame, text="กำลังดาวน์โหลดข้อมูล...", font=("Arial", 10), fg="#38bdf8", bg="#f3f6fb")
        self.last_update.pack(pady=5)

        table_frame = tk.Frame(self.frame, bg="#ffffff", padx=8, pady=8)
        table_frame.pack(fill="both",expand=True,padx=30,pady=20)
        columns = (
            "code",
            "name",
            "mid",
            "buy",
            "sell",
            "api_date",
            "updated"
        )

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Exora.Treeview", background="#ffffff", foreground="#20324d",
                        fieldbackground="#ffffff", rowheight=34, font=("Arial", 10), borderwidth=0)
        style.configure("Exora.Treeview.Heading", background="#e7eef8", foreground="#17345d",
                        font=("Arial", 10, "bold"), padding=(9, 9), relief="flat")
        style.map("Exora.Treeview", background=[("selected", "#d8e8ff")],
                  foreground=[("selected", "#17345d")])
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Exora.Treeview")
        self.tree.heading("code",text="Currency")

        self.tree.heading("name",text="ชื่อสกุลเงิน")
        self.tree.heading("mid",text="ราคากลาง")
        self.tree.heading("buy",text="Buy Rate")
        self.tree.heading("sell",text="Sell Rate")
        self.tree.heading("api_date",text="วันที่ API")
        self.tree.heading("updated",text="อัปเดตล่าสุด")

        self.tree.column("code",width=90,anchor="center")
        self.tree.column("name", width=180)
        self.tree.column("mid",width=110,anchor="center")
        self.tree.column("buy",width=110,anchor="center")
        self.tree.column("sell",width=110,anchor="center")
        self.tree.column("api_date",width=110,anchor="center")
        self.tree.column("updated",width=170,anchor="center")

        scrollbar = ttk.Scrollbar(table_frame,orient="vertical",command=self.tree.yview)

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left",fill="both",expand=True)

        scrollbar.pack(side="right",fill="y")

        spread_frame = tk.Frame(self.frame, bg="#f3f6fb")
        spread_frame.pack(pady=10)
        
        tk.Label(spread_frame,text="ส่วนต่างร้านค้า:",fg="white",bg="#f3f6fb",font=("Arial", 10)).pack(side="left")

        self.spread_var = tk.StringVar(value="0.50")

        tk.Entry(spread_frame,textvariable=self.spread_var,width=8,justify="center",font=("Arial", 11),relief="solid",bd=1).pack(side="left",padx=5,ipady=4)

        tk.Label(spread_frame,text="%",fg="white",bg="#f3f6fb").pack(side="left")

        tk.Button(spread_frame,text="ใช้ Spread",command=self.update_api,bg="#1769e0",fg="white",activebackground="#0f55bd",activeforeground="white",relief="flat",font=("Arial", 10, "bold"),cursor="hand2",padx=12,pady=7).pack(side="left",padx=10)

        # ปรับวิดเจ็ตหลักให้มีระยะห่างและคอนทราสต์ที่ชัดเจน
        self.frame.configure(padx=20)
        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f7faff")

    def show(self):
        self.frame.pack(fill="both", expand="True")
        self.load_data()

    def hide(self):
        self.frame.pack_forget()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        currencies = EXORA_database.getcurs()
        latest_update = None
        for row in currencies:
            (
                currency_id,
                code,
                name,
                buy_rate,
                sell_rate,
                mid_rate,
                api_date,
                updated_at
            ) = row

            self.tree.insert("","end",
                tags=("even" if len(self.tree.get_children()) % 2 == 0 else "odd",),
                values=(
                    code,
                    name,
                    f"{mid_rate:.6f}",
                    f"{buy_rate:.6f}",
                    f"{sell_rate:.6f}",
                    api_date or "-",
                    updated_at or "-"
                )
            )

            if updated_at:
                if (latest_update is None or updated_at > latest_update):
                    latest_update = updated_at

        if latest_update:
            self.last_update.config(text=f"อัปเดตข้อมูลล่าสุด: {latest_update}")

        else:
            self.last_update.config(text="ยังไม่มีข้อมูล")
    def update_api(self):
        self.update_button.config(state="disabled", text="กำลังอัปเดต...")
        self.root.update_idletasks()
        try:
            currencies = EXORA_database.getcurs()
            codes = [row[1] for row in currencies if row[1] != "THB"]
            result = EXORA_api.getexr(base="THB", currencies = codes)
            if not result["success"]:
                messagebox.showerror("เชื่อมต่อไม่สำเร็จ","ไม่สามารถเชื่อมต่อข้อมูลค่าเงินำด้\n\n" + result["error"])
                return 
            rates = result["rates"]
            api_date = result["date"]
            try:
                spread_percent = float(self.spread_var.get())
                if spread_percent < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("spread ไม่ถูกต้อง", "กรุณาระบุเป็นตัวเลข")
                return
            for code in codes :
                if code not in rates:
                    continue
                foreign_per_thb = rates[code]
                if foreign_per_thb == 0:
                    continue
                mid_rate = 1 / foreign_per_thb
                spread = spread_percent / 100
                buy_rate = mid_rate * (1 - spread)
                sell_rate = mid_rate * (1 + spread)
                EXORA_database.upcur_api(code,mid_rate,buy_rate,sell_rate,api_date)
            EXORA_database.upcur_api("THB",1,1,1,api_date)
            self.load_data()
            messagebox.showinfo("สำเร็จ", "อัปเดตอัตราแลกเปลี่ยนเรียบร้อย")
        finally:
            self.update_button.config(state="normal", text="อัปเดตค่าเงิน")


