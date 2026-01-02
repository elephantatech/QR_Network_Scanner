import tkinter as tk
from tkinter import scrolledtext, messagebox, Label
import tkinter.ttk as ttk
import threading
from .scanner import QRCodeScanner
from .network import NetworkManager, WiFiQRParser
import sys
import cv2
from PIL import Image, ImageTk

import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class QRNetworkApp:
    def __init__(self, root, debug=False):
        self.root = root
        self.root.title("📶 QR Network Scanner")
        self.root.geometry("800x700")
        self.debug = debug
        
        # Determine log file path
        home_dir = os.path.expanduser("~")
        self.log_file = os.path.join(home_dir, "qr_network_debug.log") if debug else None

        if self.debug and self.log_file:
             try:
                 with open(self.log_file, "a") as f:
                     f.write(f"--- QR Network Scanner Log Started: {os.getcwd()} ---\n")
             except Exception:
                 pass

        # Set Window Icon
        try:
            icon_path = resource_path("assets/icon.png")
            # Use PIL for better format support
            icon_pil = Image.open(icon_path)
            icon_img = ImageTk.PhotoImage(icon_pil)
            self.root.iconphoto(False, icon_img)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        # --- Tabs Layout ---
        self.style = ttk.Style()
        self.style.configure('TNotebook.Tab', font=('Helvetica', 12, 'bold'), padding=[10, 5])
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # 1. Scanner Tab
        self.scanner_frame = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.scanner_frame, text='  📷 Scanner  ')
        
        # 2. Help Tab
        self.help_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.help_frame, text='  ❓ Help & FAQ  ')

        self.setup_scanner_ui()
        self.setup_help_ui()
        
        self.scanner = QRCodeScanner()
        self.is_scanning = False 
        self.camera_active = True
        self.is_paused = False # New flag for focus tracking
        
        # Delay camera start to ensure UI is ready
        self.root.after(500, self.start_camera_safe)
        
        self.create_native_menu()
        
        # Bind Focus Events for pausing camera
        self.root.bind("<FocusIn>", self.on_focus_in)
        self.root.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        # Only handle root window focus events to avoid child widget noise
        if event.widget == self.root:
            self.is_paused = False
            # self.log("App Focused - Resuming Camera")

    def on_focus_out(self, event):
        if event.widget == self.root:
            self.is_paused = True
            # self.log("App Lost Focus - Pausing Camera")

    def create_native_menu(self):
        """Create native macOS menu bar"""
        menubar = tk.Menu(self.root)
        
        # 'Apple' Menu (Application Name Menu)
        # On macOS, the first menu added is the 'Application' menu
        app_menu = tk.Menu(menubar, name='apple')
        menubar.add_cascade(menu=app_menu)
        
        app_menu.add_command(label='About QR Network Scanner', command=self.show_about)
        app_menu.add_separator()
        
        self.root.config(menu=menubar)
        
    # ... (rest of methods) ...

    def update_camera_feed(self):
        if self.camera_active:
            # If paused (lost focus) or camera stopped, skip processing but keep loop alive
            if self.is_paused:
                self.root.after(200, self.update_camera_feed) # Slow poll
                return

            ret, frame = self.scanner.get_frame()
            if ret:
                # Resize the frame to fit the UI
                height, width, _ = frame.shape
                new_width = 640
                new_height = int(height * (new_width / width))
                resize_frame = cv2.resize(frame, (new_width, new_height))
                
                # Convert frame for Tkinter
                rgb_frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
                
                # Perform Detection if scanning (on main thread)
                if self.is_scanning:
                    # Detect on the ORIGINAL frame for better resolution/accuracy
                    # This might cause slight UI stutter on slower machines but ensures detection works
                    decoded_text, points = self.scanner.detect_qr(frame)
                    
                    if decoded_text:
                        self.log("QR Code found! Parsing...")
                        self.is_scanning = False
                        self.scan_btn.config(text="Start Scanning", bg="#007AFF")
                        # Process immediately as we are on main thread
                        self.process_qr_data(decoded_text, NetworkManager())

            
            # Continue updating feed
            self.root.after(10, self.update_camera_feed)

    def process_qr_data(self, qr_data, net_mgr):
        try:
            wifi_info = WiFiQRParser.parse(qr_data)
            ssid = wifi_info['ssid']
            password = wifi_info.get('password', '')
            security = wifi_info.get('type', 'WPA')
        except ValueError as e:
            self.log(f"Error parsing QR: {e}")
            return

        self.log(f"Network: {ssid} ({security})")
        
        self.log("Adding network to system settings...")
        success, output = net_mgr.add_network(ssid, password, security)
        if success:
            self.log("Successfully added network.")
        else:
            self.log(f"Failed to add network: {output}")
        
        self.log(f"Connecting to {ssid}...")
        current = net_mgr.get_current_network()
        if current == ssid:
            self.log(f"Already connected to {ssid}.")
        else:
            success, output = net_mgr.connect_network(ssid, password)
            if success:
                self.log(f"SUCCESS: Connected to {ssid}!")
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Connected to {ssid}"))
            else:
                self.log(f"Failed to connect: {output}")
                self.root.after(0, lambda: messagebox.showerror("Connection Failed", output))

    def on_closing(self):
        self.camera_active = False
        if self.scanner:
            self.scanner.stop_camera()
        self.root.destroy()

def main(debug=False):
    import traceback
    try:
        root = tk.Tk()
        app = QRNetworkApp(root, debug=debug)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception:
        # Emergency Crash Logging
        error_msg = traceback.format_exc()
        crash_file = os.path.expanduser("~/qr_crash.log")
        with open(crash_file, "w") as f:
            f.write(error_msg)
        try:
             # Try to show error via TK if possible, though unlikely if crashed
             messagebox.showerror("Critical Error", f"App crashed. Log saved to {crash_file}\n\n{error_msg}")
        except:
             pass

if __name__ == "__main__":
    main()
