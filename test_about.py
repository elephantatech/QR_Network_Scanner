import tkinter as tk
from tkinter import messagebox

def show_about():
    about_msg = (
        "QR Network Scanner v0.1.0\n\n"
        "Copyright © 2026 Elephanta Technologies and Design Inc\n"
        "Developed by elephantatech\n\n"
        "Licensed under the Apache License, Version 2.0.\n"
        "You may obtain a copy of the License at:\n"
        "http://www.apache.org/licenses/LICENSE-2.0"
    )
    print("DEBUG Message Content:\n" + about_msg)
    messagebox.showinfo("About QR Network Scanner", about_msg)

root = tk.Tk()
root.withdraw() # Hide main window
show_about()
root.destroy()
