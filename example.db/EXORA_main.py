'''
import tkinter as tk
import EXORA_database
from EXORA_gui import Application

def main():
    EXORA_database.createdb()
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
'''