"""Run this file in VS Code. Start a native Tkinter window, never a website."""
from pathlib import Path
import sys
import os
import importlib.util
import subprocess
import traceback

def runtime_ready():
    missing=[name for name in ('tkinter','PIL','reportlab') if importlib.util.find_spec(name) is None]
    if not missing:return True
    bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if bundled.is_file() and bundled.resolve()!=Path(sys.executable).resolve():
        result=subprocess.run([str(bundled),str(Path(__file__).resolve())],cwd=str(Path(__file__).resolve().parent))
        sys.exit(result.returncode)
    raise RuntimeError('Python นี้ขาด '+', '.join(missing)+'\nกรุณาเปิด Start_EXORA.bat หรือเลือก Python ที่มี Pillow และ ReportLab ใน VS Code')

def main():
    runtime_ready()
    if os.name=='nt':
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError,OSError):pass
    import tkinter as tk
    import EXORA_database
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
            import tkinter as tk
            from tkinter import messagebox
            root=tk.Tk();root.withdraw();messagebox.showerror('EXORA เปิดไม่สำเร็จ',str(error)+'\n\nรายละเอียดอยู่ใน EXORA_startup.log');root.destroy()
        except Exception:pass
        sys.exit(1)
