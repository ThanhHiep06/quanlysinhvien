import tkinter as tk
from tkinter import messagebox
from app.ui import MainWindow

if __name__ == "__main__":
    try:
        MainWindow().mainloop()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Không thể khởi động", f"{exc}\n\nKiểm tra MySQL, schema.sql và app/config.py.")
        root.destroy()
