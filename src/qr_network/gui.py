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
        
        # Delay camera start to ensure UI is ready
        self.root.after(500, self.start_camera_safe)
        
        self.create_native_menu()

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

    def setup_scanner_ui(self):
        # Scan Button
        self.scan_btn = tk.Button(self.scanner_frame, text="Start Scanning", command=self.toggle_scan, 
                                  height=2, bg="#007AFF", fg="black", font=("Arial", 14, "bold"))
        self.scan_btn.pack(pady=20, fill=tk.X, padx=50)

        # Camera Feed Label
        self.camera_label = Label(self.scanner_frame, bg="black")
        self.camera_label.pack(pady=5, padx=10)
        
        # Log Area
        log_frame = tk.LabelFrame(self.scanner_frame, text="Activity Log", bg="#f0f0f0", font=("Arial", 10, "bold"))
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, state='disabled', height=8)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_help_ui(self):
        import webbrowser
        
        # --- Toolbar Frame ---
        toolbar = tk.Frame(self.help_frame, bg="white", pady=10)
        toolbar.pack(fill=tk.X, padx=20)
        
        # Search Bar
        tk.Label(toolbar, text="🔍", bg="white", font=("Arial", 14)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        entry = tk.Entry(toolbar, textvariable=self.search_var, font=("Arial", 12), width=30)
        entry.pack(side=tk.LEFT, padx=5)
        entry.bind("<Return>", lambda e: self.search_help())
        
        btn_search = tk.Button(toolbar, text="Search", command=self.search_help)
        btn_search.pack(side=tk.LEFT, padx=5)

        # External Links
        btn_github = tk.Button(toolbar, text="🐛 Report Bug", 
                               command=lambda: webbrowser.open("https://github.com/elephantatech/QR_Network_Scanner/issues"),
                               bg="#ffdddd")
        btn_github.pack(side=tk.RIGHT, padx=5)
        
        btn_html = tk.Button(toolbar, text="🌐 Open HTML Guide", command=self.open_html_help)
        btn_html.pack(side=tk.RIGHT, padx=5)

        btn_about = tk.Button(toolbar, text="ℹ️ About", command=self.show_about)
        btn_about.pack(side=tk.RIGHT, padx=5)

        # --- Help Text Area ---
        self.help_text = scrolledtext.ScrolledText(self.help_frame, wrap=tk.WORD, 
                                              font=("Segoe UI", 11), padx=20, pady=20, bd=0)
        self.help_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure Tags for Styling
        self.help_text.tag_config("h1", font=("Segoe UI", 22, "bold"), foreground="#007AFF", spacing3=15)
        self.help_text.tag_config("h2", font=("Segoe UI", 16, "bold"), foreground="#333333", spacing1=20, spacing3=10)
        self.help_text.tag_config("q", font=("Segoe UI", 12, "bold"), foreground="#d63031", spacing1=10)
        self.help_text.tag_config("a", font=("Segoe UI", 11), foreground="#2d3436", spacing3=15, lmargin1=20, lmargin2=20)
        self.help_text.tag_config("step", font=("Segoe UI", 11), foreground="#2d3436", lmargin1=20, lmargin2=20)
        self.help_text.tag_config("li", lmargin1=30, lmargin2=30)
        self.help_text.tag_config("highlight", background="yellow", foreground="black")
        
        # Insert Content
        self.help_text.insert(tk.END, "QR Network Scanner Guide\n", "h1")
        
        self.help_text.insert(tk.END, "How to Use\n", "h2")
        self.help_text.insert(tk.END, "1. Have a WiFi QR code ready (e.g. from Android WiFi sharing).\n", "step")
        self.help_text.insert(tk.END, "2. Go to the 'Scanner' tab and click 'Start Scanning'.\n", "step")
        self.help_text.insert(tk.END, "3. Point the camera at the code. The app will auto-connect.\n", "step")

        self.help_text.insert(tk.END, "CLI Mode (Advanced)\n", "h2")
        self.help_text.insert(tk.END, "Run from Source (Terminal):\n", "step")
        self.help_text.insert(tk.END, "• uv run qr-network scan\n", "li")
        
        self.help_text.insert(tk.END, "Run from Built App (.app):\n", "step")
        self.help_text.insert(tk.END, "• ./dist/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner scan\n", "li")
        self.help_text.insert(tk.END, "(Do NOT use the 'open' command for CLI arguments!)\n", "li")

        self.help_text.insert(tk.END, "Frequently Asked Questions (FAQ)\n", "h2")
        
        self.help_text.insert(tk.END, "Q: Camera shows 'Could not open camera'\n", "q")
        self.help_text.insert(tk.END, "A: This is a macOS permission issue.\n", "a")
        self.help_text.insert(tk.END, "• You must click 'Allow' when prompted.\n", "li")
        self.help_text.insert(tk.END, "• IMPORTANT: Restart the app after granting permission.\n", "li")
        self.help_text.insert(tk.END, "• Check System Settings > Privacy > Camera.\n", "li")

        self.help_text.insert(tk.END, "Q: It's scanning but not detecting?\n", "q")
        self.help_text.insert(tk.END, "A: Move the code closer/further. Ensure good lighting. The content must be a standard WiFi QR code.\n", "a")
        
        self.help_text.insert(tk.END, "Q: What happens if I can't connect?\n", "q")
        self.help_text.insert(tk.END, "A: The app adds the network to macOS Settings. You can also try clicking the WiFi icon in your menu bar to select it manually if the auto-switch fails.\n", "a")

        self.help_text.config(state="disabled")

    def search_help(self):
        query = self.search_var.get().strip()
        self.help_text.tag_remove("highlight", "1.0", tk.END)
        
        if not query:
            return
            
        start_pos = "1.0"
        while True:
            # Search for keyword
            start_pos = self.help_text.search(query, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break
            
            # Highlight match
            end_pos = f"{start_pos}+{len(query)}c"
            self.help_text.tag_add("highlight", start_pos, end_pos)
            start_pos = end_pos
            
        self.help_text.see("highlight.first") # Scroll to first match

    def open_html_help(self):
        import webbrowser
        try:
            path = resource_path("assets/help.html")
            url = "file://" + path
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open help file: {e}")

    def show_about(self):
        about_msg = (
            "QR Network Scanner v0.1.0\n\n"
            "Copyright © 2026 Elephanta Technologies and Design Inc\n"
            "Developed by elephantatech\n\n"
            "Licensed under the Apache License, Version 2.0.\n"
            "You may obtain a copy of the License at:\n"
            "http://www.apache.org/licenses/LICENSE-2.0"
        )
        messagebox.showinfo("About QR Network Scanner", about_msg)

    def start_camera_safe(self):
        try:
            self.scanner.start_camera()
            self.update_camera_feed()
            self.log("Camera started. Ready to scan.")
        except Exception as e:
            self.log(f"Camera Error: {e}")
            messagebox.showerror("Camera Error", f"Could not start camera: {e}")

    def log(self, message: str):
        try:
            print(f"[GUI LOG] {message}") # Console debug
        except:
            pass
        
        if self.debug and self.log_file:
            try:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.log_file, "a") as f:
                    f.write(f"[{timestamp}] {message}\n")
            except Exception as e:
                pass

        def _log():
            if not self.root: return
            try:
                self.log_area.config(state='normal')
                self.log_area.insert(tk.END, message + "\n")
                self.log_area.see(tk.END)
                self.log_area.config(state='disabled')
            except:
                pass
        self.root.after(0, _log)

    def toggle_scan(self):
        if self.is_scanning:
            # Stop scanning
            self.is_scanning = False
            self.scan_btn.config(text="Start Scanning", bg="#007AFF")
            self.log("Scanning stopped.")
        else:
            # Start scanning
            self.is_scanning = True
            self.scan_btn.config(text="Stop Scanning", bg="red")
            self.log("Scanning started...")

    def update_camera_feed(self):
        if self.camera_active:
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
