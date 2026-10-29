import tkinter as tk
import EXORA_database
from EXORA_gui import Application

def main():
    EXORA_database.createdb()
    root = tk.Tk()
    root.title("EXORA | Currency Exchange Management System")
    root.configure(bg="#f3f6fb")
    app = Application(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()