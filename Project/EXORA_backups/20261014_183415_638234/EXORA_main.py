"""Run this file in VS Code. Start a native Tkinter window, never a website."""
# คำอธิบาย import: นำเข้า Path: pathlib — จัดการพาธไฟล์และโฟลเดอร์ด้วย Path
# Path: วัตถุแทนพาธที่ใช้ตรวจ อ่าน เขียน และสร้างโฟลเดอร์
from pathlib import Path
# คำอธิบาย import: นำเข้า sys: sys — อ่านข้อมูล Python และควบคุมการเริ่มโปรแกรม
import sys
# คำอธิบาย import: นำเข้า os: os — อ่าน environment variables และทำงานร่วมกับระบบปฏิบัติการ
import os
# คำอธิบาย import: นำเข้า importlib.util: importlib.util — ตรวจว่ามีโมดูลที่จำเป็นพร้อมใช้งานหรือไม่
import importlib.util
# คำอธิบาย import: นำเข้า subprocess: subprocess — เริ่ม Python อีกตัวเมื่อ runtime ปัจจุบันขาด dependency
import subprocess
# คำอธิบาย import: นำเข้า traceback: traceback — จัดเก็บรายละเอียดข้อผิดพลาดสำหรับวิเคราะห์ปัญหา
import traceback

# คำอธิบาย def runtime_ready: ตรวจ dependency และเริ่มด้วย Python ที่พร้อมหากจำเป็น
# รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
def runtime_ready():
    missing=[name for name in ('tkinter','PIL','reportlab') if importlib.util.find_spec(name) is None]
    if not missing:return True
    bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if bundled.is_file() and bundled.resolve()!=Path(sys.executable).resolve():
        result=subprocess.run([str(bundled),str(Path(__file__).resolve())],cwd=str(Path(__file__).resolve().parent))
        sys.exit(result.returncode)
    raise RuntimeError('Python นี้ขาด '+', '.join(missing)+'\nกรุณาเปิด Start_EXORA.bat หรือเลือก Python ที่มี Pillow และ ReportLab ใน VS Code')

# คำอธิบาย def main: ตรวจ runtime เตรียมฐานข้อมูล และเริ่มหน้าต่าง EXORA
# รับค่า: ใช้ข้อมูล/สถานะภายในฟังก์ชัน
def main():
    runtime_ready()
    if os.name=='nt':
        try:
            # คำอธิบาย import: นำเข้า ctypes: ctypes — เรียก Windows API เพื่อปรับการแสดงผลตาม DPI
            import ctypes
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError,OSError):pass
    # คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
    import tkinter as tk
    # คำอธิบาย import: นำเข้า EXORA_database: EXORA_database — เชื่อมต่อฐานข้อมูลและจัดการข้อมูลหลักของ EXORA
    import EXORA_database
    # คำอธิบาย import: นำเข้า Application: EXORA_gui — สร้างหน้าต่างหลักและเชื่อมการทำงานของทุกหน้า
    # Application: คลาสควบคุมหน้าจอและการทำงานหลักของ EXORA
    from EXORA_gui import Application
    EXORA_database.createdb()
    root = tk.Tk()
    root.title("EXORA | Currency Exchange Management System")
    root.configure(bg="#f3f6fb")
    app = Application(root)
    root.mainloop()
    
if __name__ == "__main__":
    try:main()
    except Exception as error:
        log=Path(__file__).resolve().parent/'EXORA_startup.log'
        try:log.write_text(traceback.format_exc(),encoding='utf-8')
        except OSError:pass
        print('EXORA เปิดไม่สำเร็จ: '+str(error));print('รายละเอียด: '+str(log))
        try:
            # คำอธิบาย import: นำเข้า tkinter as tk: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
            import tkinter as tk
            # คำอธิบาย import: นำเข้า messagebox: tkinter — สร้างหน้าต่างและองค์ประกอบหน้าจอของโปรแกรม Windows
            # messagebox: กล่องแจ้งผล ข้อผิดพลาด และคำถามยืนยัน
            from tkinter import messagebox
            root=tk.Tk();root.withdraw();messagebox.showerror('EXORA เปิดไม่สำเร็จ',str(error)+'\n\nรายละเอียดอยู่ใน EXORA_startup.log');root.destroy()
        except Exception:pass
        sys.exit(1)
