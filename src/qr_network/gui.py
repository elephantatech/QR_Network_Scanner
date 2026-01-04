import tkinter as tk
import webbrowser
from tkinter import scrolledtext, messagebox, Label
import tkinter.ttk as ttk
from .scanner import QRCodeScanner
from .network import NetworkManager, WiFiQRParser
from .utils import RedactedLogger
import sys
import cv2
import time
from PIL import Image, ImageTk

import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class QRNetworkApp:
    def __init__(self, root, debug=False):
        self.root = root
        self.root.title("QR Network Scanner")
        self.root.geometry("800x700")
        self.debug = debug

        # Determine log file path
        home_dir = os.path.expanduser("~")
        self.log_file = (
            os.path.join(home_dir, "qr_network_debug.log") if debug else None
        )

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
        # --- Theme & Styles ---
        self.style = ttk.Style()
        try:
            self.style.theme_use(
                "clam"
            )  # Use 'clam' for better color customization support
        except Exception:
            pass

        # Configure Colors & Fonts (Material-like)
        self.style.configure(".", background="white", font=("Helvetica", 12))
        self.style.configure("TFrame", background="white")
        self.style.configure("TNotebook", background="white", tabposition="n")
        self.style.configure(
            "TNotebook.Tab",
            font=("Helvetica", 12, "bold"),
            padding=[15, 8],
            background="#f0f0f0",
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#007AFF")],
            foreground=[("selected", "white")],
        )

        # Configure Green Button Style
        self.style.configure(
            "Green.TButton",
            background="#28a745",
            foreground="white",
            font=("Helvetica", 15, "bold"),
            borderwidth=0,
            focuscolor="none",
            padding=[10, 10],
        )  # Padding handles the size
        self.style.map(
            "Green.TButton",
            background=[("active", "#218838"), ("pressed", "#1e7e34")],
            foreground=[("active", "white"), ("pressed", "white")],
        )

        # Configure Red Button Style (for Stop)
        self.style.configure(
            "Red.TButton",
            background="#d32f2f",
            foreground="white",
            font=("Helvetica", 15, "bold"),
            borderwidth=0,
            focuscolor="none",
            padding=[10, 10],
        )
        self.style.map(
            "Red.TButton",
            background=[("active", "#b71c1c"), ("pressed", "#c62828")],
            foreground=[("active", "white"), ("pressed", "white")],
        )

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # 1. Scanner Tab
        self.scanner_frame = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.scanner_frame, text="  📷 Scanner  ")

        # 2. Help Tab
        self.help_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.help_frame, text="  ❓ Help & FAQ  ")

        # Security Options
        self.confirm_connect = tk.BooleanVar(value=False)
        self.add_only = tk.BooleanVar(value=False)

        # Initialize Redactor
        self._redactor = RedactedLogger(None)

        self.setup_scanner_ui()
        self.setup_help_ui()

        self.scanner = QRCodeScanner()
        self.is_scanning = False
        self.camera_active = False  # Start with camera off
        self.is_paused = False  # New flag for focus tracking

        # Delay camera start to ensure UI is ready (Disabled auto-start)
        # self.root.after(500, self.start_camera_safe)

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
        app_menu = tk.Menu(menubar, name="apple")
        menubar.add_cascade(menu=app_menu)

        app_menu.add_command(label="About QR Network Scanner", command=self.show_about)
        app_menu.add_separator()

        # 'Help ' Menu (Extra space to avoid macOS Search Bar injection)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help ", menu=help_menu)
        help_menu.add_command(
            label="Online Documentation",
            command=lambda: webbrowser.open(
                "https://github.com/elephantatech/QR_Network_Scanner/blob/main/HELP.md"
            ),
        )
        help_menu.add_command(label="Offline Guide (HTML)", command=self.open_html_help)
        help_menu.add_separator()
        help_menu.add_command(
            label="Report an Issue",
            command=lambda: webbrowser.open(
                "https://github.com/elephantatech/QR_Network_Scanner/issues"
            ),
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="Check Permissions...",
            command=lambda: self.show_permission_help("General"),
        )

        self.root.config(menu=menubar)

    def setup_scanner_ui(self):
        # Scan Button
        # Using ttk.Button with custom 'Green.TButton' style for solid color support on macOS ('clam' theme)
        # Buttons Frame
        btn_frame = tk.Frame(self.scanner_frame, bg="#f0f0f0")
        btn_frame.pack(pady=20, fill=tk.X, padx=50)

        # Camera Scan Button
        self.scan_btn = ttk.Button(
            btn_frame,
            text="📷 Scan Camera",
            command=self.toggle_scan,
            style="Green.TButton",
            cursor="hand2",
        )
        self.scan_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        # Screen Scan Button
        self.screen_scan_btn = ttk.Button(
            btn_frame,
            text="🖥️ Scan Screen",
            command=self.scan_from_screen,
            style="Green.TButton",
            cursor="hand2",
        )
        self.screen_scan_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Scan Options Frame (Renamed from Security Options which was implicit)
        opt_frame = tk.LabelFrame(self.scanner_frame, text="Scan Options", bg="#f0f0f0")
        opt_frame.pack(pady=(5, 10), padx=50, fill=tk.X)

        # Row 1: Camera & Timeout
        row1 = tk.Frame(opt_frame, bg="#f0f0f0")
        row1.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(row1, text="Camera:", bg="#f0f0f0").pack(side=tk.LEFT)

        # Fetch actual camera names if possible (macOS)
        from .utils import get_camera_names

        camera_names = get_camera_names()

        self.camera_idx_var = tk.StringVar(value=camera_names[0])

        cam_combo = ttk.Combobox(
            row1,
            textvariable=self.camera_idx_var,
            values=camera_names,
            state="readonly",
            width=20,
        )
        cam_combo.pack(side=tk.LEFT, padx=(5, 15))
        # Keep map of name -> index
        self.camera_map = {name: i for i, name in enumerate(camera_names)}

        tk.Label(row1, text="Timeout (s):", bg="#f0f0f0").pack(side=tk.LEFT)
        self.timeout_var = tk.IntVar(value=60)
        timeout_spin = tk.Spinbox(
            row1, from_=5, to=300, textvariable=self.timeout_var, width=4
        )
        timeout_spin.pack(side=tk.LEFT, padx=(5, 0))

        # Row 2: Checkboxes
        row2 = tk.Frame(opt_frame, bg="#f0f0f0")
        row2.pack(fill=tk.X, padx=10, pady=5)

        # Checkboxes
        chk_confirm = ttk.Checkbutton(
            row2, text="Confirm before connecting", variable=self.confirm_connect
        )
        chk_confirm.pack(side=tk.LEFT, padx=(0, 10))

        chk_add = ttk.Checkbutton(
            row2, text="Add only (don't connect)", variable=self.add_only
        )
        chk_add.pack(side=tk.LEFT)

        # Camera Feed Label
        self.camera_label = Label(
            self.scanner_frame,
            bg="black",
            text="Camera is Off\nClick 'Scan Camera' to start",
            fg="white",
        )
        self.camera_label.pack(pady=5, padx=10, expand=True, fill=tk.BOTH)

        # Log Area
        log_frame = tk.LabelFrame(
            self.scanner_frame,
            text="Activity Log",
            bg="#f0f0f0",
            font=("Arial", 10, "bold"),
        )
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(log_frame, state="disabled", height=8)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_help_ui(self):
        import webbrowser

        # --- Toolbar Frame ---
        toolbar = tk.Frame(self.help_frame, bg="white", pady=10)
        toolbar.pack(fill=tk.X, padx=20)

        # External Links
        btn_github = tk.Button(
            toolbar,
            text="🐛 Report Bug",
            command=lambda: webbrowser.open(
                "https://github.com/elephantatech/QR_Network_Scanner/issues"
            ),
            bg="#ffdddd",
        )
        btn_github.pack(side=tk.RIGHT, padx=5)

        btn_online = tk.Button(
            toolbar,
            text="🌎 Online Docs",
            command=lambda: webbrowser.open(
                "https://github.com/elephantatech/QR_Network_Scanner/blob/main/HELP.md"
            ),
        )
        btn_online.pack(side=tk.RIGHT, padx=5)

        btn_html = tk.Button(
            toolbar, text="📄 Offline Guide", command=self.open_html_help
        )
        btn_html.pack(side=tk.RIGHT, padx=5)

        btn_about = tk.Button(toolbar, text="ℹ️ About", command=self.show_about)
        btn_about.pack(side=tk.RIGHT, padx=5)

        # --- Help Text Area ---
        self.help_text = scrolledtext.ScrolledText(
            self.help_frame, wrap=tk.WORD, font=("Segoe UI", 11), padx=20, pady=20, bd=0
        )
        self.help_text.pack(fill=tk.BOTH, expand=True)

        # Configure Tags for Styling
        self.help_text.tag_config(
            "h1", font=("Segoe UI", 22, "bold"), foreground="#007AFF", spacing3=15
        )
        self.help_text.tag_config(
            "h2",
            font=("Segoe UI", 16, "bold"),
            foreground="#333333",
            spacing1=20,
            spacing3=10,
        )
        self.help_text.tag_config(
            "q", font=("Segoe UI", 12, "bold"), foreground="#d63031", spacing1=10
        )
        self.help_text.tag_config(
            "a",
            font=("Segoe UI", 11),
            foreground="#2d3436",
            spacing3=15,
            lmargin1=20,
            lmargin2=20,
        )
        self.help_text.tag_config(
            "step",
            font=("Segoe UI", 11),
            foreground="#2d3436",
            lmargin1=20,
            lmargin2=20,
        )
        self.help_text.tag_config("li", lmargin1=30, lmargin2=30)
        self.help_text.tag_config("highlight", background="yellow", foreground="black")

        # Insert Content
        self.help_text.insert(tk.END, "QR Network Scanner Guide\n", "h1")

        self.help_text.insert(tk.END, "How to Use\n", "h2")
        self.help_text.insert(
            tk.END,
            "1. (Optional) Toggle 'Confirm before connecting' or 'Add only'.\n",
            "step",
        )
        self.help_text.insert(
            tk.END, "2. Click 'Start Scanning' or 'Scan Screen'.\n", "step"
        )
        self.help_text.insert(
            tk.END,
            "3. Point camera at code OR ensure QR is visible on screen.\n",
            "step",
        )
        self.help_text.insert(
            tk.END,
            "4. The app will auto-connect or save based on your settings.\n",
            "step",
        )

        self.help_text.insert(tk.END, "CLI Mode (Terminal)\n", "h2")
        self.help_text.insert(tk.END, "Run from Installed App:\n", "step")
        self.help_text.insert(
            tk.END,
            "• /Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner scan --help\n",
            "li",
        )

        self.help_text.insert(tk.END, "Command Options:\n", "step")
        self.help_text.insert(
            tk.END,
            "• --screen: Captures and scans content from your screen(s).\n",
            "li",
        )
        self.help_text.insert(
            tk.END,
            "• --timeout <SEC>: Stops scanning after specified seconds (default: 60).\n",
            "li",
        )
        self.help_text.insert(
            tk.END,
            "• --camera <ID>: Select a specific camera device index (0, 1, ...).\n",
            "li",
        )
        self.help_text.insert(
            tk.END,
            "• --verbose (-v): Enable detailed debug logging to console.\n",
            "li",
        )

        self.help_text.insert(tk.END, "Run from Source (Dev):\n", "step")
        self.help_text.insert(tk.END, "• uv run qr-network scan\n", "li")

        self.help_text.insert(tk.END, "UI Options Explained\n", "h2")
        self.help_text.insert(tk.END, "• Confirm before connecting:\n", "step")
        self.help_text.insert(
            tk.END,
            "  Shows a dialog with Network Name (SSID) and Security Type before initiating connection.\n",
            "li",
        )
        self.help_text.insert(tk.END, "• Add to settings only:\n", "step")
        self.help_text.insert(
            tk.END,
            "  Saves the network profile to System Settings so you can connect manually later, but does not switch your WiFi immediately.\n",
            "li",
        )

        self.help_text.insert(tk.END, "Security & Privacy\n", "h2")
        self.help_text.insert(tk.END, "• Credentials stored in macOS Keychain.\n", "li")
        self.help_text.insert(tk.END, "• Logs are redacted (no passwords).\n", "li")
        self.help_text.insert(tk.END, "• Source code is open for review.\n", "li")

        self.help_text.insert(tk.END, "Frequently Asked Questions (FAQ)\n", "h2")

        self.help_text.insert(tk.END, "Q: Camera shows 'Could not open camera'\n", "q")
        self.help_text.insert(tk.END, "A: This is a macOS permission issue.\n", "a")
        self.help_text.insert(
            tk.END, "• Click 'Check Permissions' in Help menu.\n", "li"
        )
        self.help_text.insert(tk.END, "• Restart app after granting access.\n", "li")

        self.help_text.insert(tk.END, "Q: It's scanning but not detecting?\n", "q")
        self.help_text.insert(
            tk.END,
            "A: Ensure good lighting. Moving closer/further helps. Timeout is 60s.\n",
            "a",
        )

        self.help_text.insert(tk.END, "Q: What happens if I can't connect?\n", "q")
        self.help_text.insert(
            tk.END,
            "A: The app adds the network to macOS Settings. You can also try clicking the WiFi icon in your menu bar to select it manually if the auto-switch fails.\n",
            "a",
        )

        self.help_text.config(state="disabled")

    def open_html_help(self):
        import webbrowser

        try:
            path = resource_path("assets/help.html")
            url = "file://" + path
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open help file: {e}")

    def show_about(self):
        # Pause camera updates
        was_active = self.camera_active
        self.camera_active = False

        # Create Custom Window (Non-blocking Toplevel)
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x350")
        about_window.resizable(False, False)
        about_window.configure(bg="white")

        # Make it modal-like (transient) but without blocking the main loop aggressively
        about_window.transient(self.root)

        # Content
        pad_frame = tk.Frame(about_window, bg="white", padx=20, pady=20)
        pad_frame.pack(fill=tk.BOTH, expand=True)

        # Icon
        try:
            icon_path = resource_path("assets/icon.png")
            icon_img = Image.open(icon_path)
            icon_img = icon_img.resize((64, 64), Image.Resampling.LANCZOS)
            icon_tk = ImageTk.PhotoImage(icon_img)
            icon_label = tk.Label(pad_frame, image=icon_tk, bg="white")
            icon_label.image = icon_tk  # Keep ref
            icon_label.pack(pady=(0, 10))
        except Exception:
            pass

        tk.Label(
            pad_frame, text="QR Network Scanner", font=("Arial", 16, "bold"), bg="white"
        ).pack(pady=(0, 10))
        tk.Label(
            pad_frame, text="v0.1.0-beta.16", font=("Arial", 10), fg="#666", bg="white"
        ).pack()

        copyright_text = (
            "Copyright © 2026\nElephanta Technologies and Design Inc\n\n"
            "Developed by elephantatech"
        )
        tk.Label(pad_frame, text=copyright_text, bg="white", justify=tk.CENTER).pack(
            pady=20
        )

        license_info = "Licensed under Apache License 2.0"
        tk.Label(
            pad_frame, text=license_info, bg="white", fg="#007AFF", cursor="hand2"
        ).pack()

        # Close Handler
        def close_about():
            about_window.destroy()
            if was_active:
                self.camera_active = True
                self.update_camera_feed()

        tk.Button(pad_frame, text="Close", command=close_about, width=10).pack(pady=30)

        # Handle "X" button click
        about_window.protocol("WM_DELETE_WINDOW", close_about)

    def start_camera_safe(self):
        try:
            # Get index from name
            selected_name = self.camera_idx_var.get()
            idx = self.camera_map.get(selected_name, 0)

            # If changed/first time
            if self.scanner.camera_id != idx:
                self.scanner.stop_camera()  # Stop old
                self.scanner = QRCodeScanner(camera_id=idx)

            self.scanner.start_camera()
            self.camera_active = True
            self.update_camera_feed()
            self.log("Camera started. Ready to scan.")
        except Exception as e:
            self.log(f"Camera Error: {e}")
            if (
                "not found" in str(e).lower()
                or "authorization" in str(e).lower()
                or "access" in str(e).lower()
            ):
                self.show_permission_help("Camera")
            else:
                self.show_error_with_copy(
                    "Camera Error", f"Could not start camera:\n{e}"
                )

    def show_error_with_copy(self, title, message):
        """Shows an error dialog with a 'Copy Debug Info' button."""
        import platform

        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.config(bg="white")

        # Icon/Title
        tk.Label(
            dialog,
            text="❌ " + title,
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#d32f2f",
        ).pack(pady=10)

        # Message Area
        txt_frame = tk.Frame(dialog, bg="white", padx=10)
        txt_frame.pack(fill=tk.BOTH, expand=True)

        txt = tk.Text(
            txt_frame,
            height=5,
            width=40,
            font=("Arial", 10),
            wrap=tk.WORD,
            borderwidth=0,
        )
        txt.insert(tk.END, message)
        txt.config(state="disabled")  # Read-only
        txt.pack(fill=tk.BOTH, expand=True)

        # Info to copy
        debug_info = (
            f"Error: {title}\n"
            f"Message: {message}\n"
            f"App Version: 0.1.0-beta.10\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"Python: {sys.version.split()[0]}"
        )

        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(debug_info)
            self.root.update()  # Required for clipboard
            btn_copy.config(text="Copied! ✓")

        btn_frame = tk.Frame(dialog, bg="white", pady=10)
        btn_frame.pack(fill=tk.X)

        btn_copy = ttk.Button(
            btn_frame, text="📋 Copy Debug Info", command=copy_to_clipboard
        )
        btn_copy.pack(side=tk.LEFT, padx=20)

        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(
            side=tk.RIGHT, padx=20
        )

    def show_permission_help(self, focus="Camera"):
        """Shows a helper window to guide user to System Settings."""
        perm_window = tk.Toplevel(self.root)
        perm_window.title("⚠️ Permission Required")
        perm_window.geometry("500x400")
        perm_window.config(bg="white")

        pad = tk.Frame(perm_window, bg="white", padx=20, pady=20)
        pad.pack(fill=tk.BOTH, expand=True)

        # Icon
        try:
            icon_path = resource_path("assets/icon.png")
            icon_img = Image.open(icon_path)
            icon_img = icon_img.resize((64, 64), Image.Resampling.LANCZOS)
            icon_tk = ImageTk.PhotoImage(icon_img)
            icon_label = tk.Label(pad, image=icon_tk, bg="white")
            icon_label.image = icon_tk  # Keep ref
            icon_label.pack(pady=(0, 10))
        except Exception:
            pass

        tk.Label(
            pad,
            text=f"{focus} Access Needed",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#d32f2f",
        ).pack(pady=(0, 10))

        msg = (
            f"macOS requires you to explicitly grant access for this app to use the {focus}.\n\n"
            "1. Click the button below to open System Settings.\n"
            f"2. Find 'QR Network Scanner' (or Terminal if running via CLI) in the list.\n"
            "3. Enable the toggle.\n"
            "4. IMPORTANT: You must restart the app/terminal for changes to take effect."
        )

        tk.Label(
            pad,
            text=msg,
            bg="white",
            justify=tk.LEFT,
            wraplength=450,
            font=("Arial", 11),
        ).pack(pady=10)

        # Deep Links
        def open_settings(url):
            webbrowser.open(url)

        btn_frame = tk.Frame(pad, bg="white")
        btn_frame.pack(pady=20)

        if focus == "Camera":
            tk.Button(
                btn_frame,
                text="Open Camera Settings ↗",
                command=lambda: open_settings(
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_Camera"
                ),
            ).pack(side=tk.LEFT, padx=5)

        # Always show Location/WiFi option too as it's common
        tk.Button(
            btn_frame,
            text="Open Wi-Fi/Location Settings ↗",
            command=lambda: open_settings(
                "x-apple.systempreferences:com.apple.preference.security?Privacy_LocationServices"
            ),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(pad, text="Close", command=perm_window.destroy).pack(side=tk.BOTTOM)

    def log(self, message: str):
        # Redact sensitive info
        if hasattr(self, "_redactor"):
            message = self._redactor._redact(message)

        try:
            print(f"[GUI LOG] {message}")  # Console debug
        except Exception:
            pass

        if self.debug and self.log_file:
            try:
                import datetime

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.log_file, "a") as f:
                    f.write(f"[{timestamp}] {message}\n")
            except Exception:
                pass

        def _log():
            if not self.root:
                return
            try:
                self.log_area.config(state="normal")
                self.log_area.insert(tk.END, message + "\n")
                self.log_area.see(tk.END)
                self.log_area.config(state="disabled")
            except Exception:
                pass

        self.root.after(0, _log)

    def scan_from_screen(self):
        """Captures screen and scans for QR code"""
        # Stop camera scanning if active to prevent conflict/confusion
        if self.is_scanning:
            self.toggle_scan()

        # Temporarily stop camera feed to save resources/prevent interference while grabbing screen?
        # For now, we can leave the feed running but just pause detection logic which is already handled since is_scanning is False.
        # Actually, let's just log what we are doing.
        self.log("Capturing screen...")

        # Run in thread to not freeze UI during grab/process?
        # Screen grab is usually fast, but detection might take a split second.
        # For responsiveness, main thread is usually okay for single shot, but threading is safer.
        # However, Tkinter needs UI updates on main thread. Let's do simple blocking for now as it's a button click.

        try:
            decoded_text = self.scanner.scan_screen()

            if decoded_text:
                self.log("QR Code found on screen!")
                self.process_qr_data(decoded_text, NetworkManager())
            else:
                self.log("No Wi-Fi QR code found on any screen.")
                messagebox.showinfo(
                    "Scan from Screen",
                    "No Wi-Fi QR code detected on any connected screen.\n\nMake sure the QR code is clearly visible.",
                )

        except Exception as e:
            self.log(f"Screen scan failed: {e}")
            messagebox.showerror("Error", f"Could not scan screen: {e}")

    def toggle_scan(self):
        if self.is_scanning:
            # Stop scanning
            self.is_scanning = False
            self.scan_btn.config(text="📷 Scan Camera", style="Green.TButton")
            self.log("Scanning stopped.")

            # Stop camera to save resources
            self.camera_active = False
            self.scanner.stop_camera()

            # Reset Label
            self.camera_label.config(
                image="", text="Camera is Off\nClick 'Scan Camera' to start"
            )
        else:
            # Start scanning
            if not self.camera_active:
                self.start_camera_safe()
                # self.camera_active = True # Moved to start_camera_safe

            self.scan_start_time = time.time()
            self.is_scanning = True
            self.scan_btn.config(text="🛑 Stop Scanning", style="Red.TButton")
            self.log("Scanning started...")

    def update_camera_feed(self):
        if self.camera_active:
            # If paused (lost focus) or camera stopped, skip processing but keep loop alive
            if self.is_paused:
                self.root.after(200, self.update_camera_feed)  # Slow poll
                return

            ret, frame = self.scanner.get_frame()
            if ret:
                # Resize the frame to fit the UI (Dynamic resizing)
                # Get current label size
                label_w = self.camera_label.winfo_width()
                label_h = self.camera_label.winfo_height()

                # If label size is too small (e.g. minimized or initializing), use default 640x480 ratio target
                if label_w < 10 or label_h < 10:
                    label_w = 640
                    label_h = 480

                # Calculate aspect ratio
                h, w, _ = frame.shape
                aspect_ratio = w / h

                # Determine new dimensions to fit within label while maintaining aspect ratio
                if label_w / label_h > aspect_ratio:
                    # Label is wider than frame -> height is limiting factor
                    new_height = label_h
                    new_width = int(new_height * aspect_ratio)
                else:
                    # Label is taller than frame -> width is limiting factor
                    new_width = label_w
                    new_height = int(new_width / aspect_ratio)

                # Resize
                resize_frame = cv2.resize(frame, (new_width, new_height))

                # Convert frame for Tkinter
                rgb_frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(
                    image=imgtk, text=""
                )  # interactively clear text

                # Perform Detection if scanning (on main thread)
                if self.is_scanning:
                    # Timeout Check
                    try:
                        elapsed = time.time() - self.scan_start_time
                        current_timeout = self.timeout_var.get()
                        if elapsed > current_timeout:
                            self.toggle_scan()  # Assuming this is the equivalent of stop_scan() for now
                            self.log(f"Scan timed out after {current_timeout}s.")
                            # The original code had a messagebox.askretrycancel here.
                            # The new snippet implies a different error handling.
                            # For now, I'll keep the original messagebox logic but adapt the message.
                            if messagebox.askretrycancel(
                                "Scan Timed Out",
                                f"No QR code detected within {current_timeout} seconds.\n\nRetry?",
                            ):
                                self.toggle_scan()
                            return
                        remaining = int(current_timeout - elapsed)
                        # Overlay
                        cv2.putText(
                            resize_frame,
                            f"Scanning: {remaining}s",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2,
                        )
                        # Re-update label with overlay
                        img_ov = Image.fromarray(
                            cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                        )
                        imgtk_ov = ImageTk.PhotoImage(image=img_ov)
                        self.camera_label.imgtk = imgtk_ov
                        self.camera_label.configure(image=imgtk_ov)
                    except Exception:
                        pass

                    # Detect on the ORIGINAL frame for better resolution/accuracy
                    # This might cause slight UI stutter on slower machines but ensures detection works
                    decoded_text, points = self.scanner.detect_qr(frame)

                    if decoded_text:
                        self.log("QR Code found! Parsing...")
                        self.is_scanning = False
                        self.scan_btn.config(
                            text="📷 Scan Camera", style="Green.TButton"
                        )

                        # Stop camera to save resources
                        self.camera_active = False
                        self.scanner.stop_camera()

                        # Process immediately as we are on main thread
                        self.process_qr_data(decoded_text, NetworkManager())

            # Continue updating feed
            self.root.after(10, self.update_camera_feed)

    def process_qr_data(self, qr_data, net_mgr):
        try:
            wifi_info = WiFiQRParser.parse(qr_data)
            ssid = wifi_info["ssid"]
            password = wifi_info.get("password", "")
            security = wifi_info.get("type", "WPA")
        except ValueError as e:
            self.log(f"Error parsing QR: {e}")
            return

        self.log(f"Network: {ssid} ({security})")

        # Confirm before connect
        if self.confirm_connect.get():
            # Show a custom dialog or standard yes/no
            # We want to show SSID and Security. Password hidden by default in log,
            # here we can show "Password: *****"
            msg = f"Network Found:\nSSID: {ssid}\nSecurity: {security}\n\nDo you want to proceed?"
            if not messagebox.askyesno("Confirm Connection", msg):
                self.log("User cancelled connection.")
                return

        self.log("Adding network to system settings...")
        success, output = net_mgr.add_network(ssid, password, security)
        if success:
            self.log("Successfully added network.")
        else:
            self.log(f"Failed to add network: {output}")
            # If add failed, usually connect will fail too, but maybe it exists?
            # We continue if Add Only is NOT checked, otherwise we stop?

        if self.add_only.get():
            self.log("Add Only mode enabled. Skipping connection.")
            messagebox.showinfo(
                "Network Added", f"Profile for '{ssid}' updated.\nAuto-connect skipped."
            )
            return

        self.log(f"Connecting to {ssid}...")
        current = net_mgr.get_current_network()
        if current == ssid:
            self.log(f"Already connected to {ssid}.")
        else:
            success, output = net_mgr.activate_network(ssid, password)
            if success:
                self.log(f"SUCCESS: Connected to {ssid}!")
                self.root.after(
                    0, lambda: messagebox.showinfo("Success", f"Connected to {ssid}")
                )
            else:
                self.log(f"Failed to connect: {output}")
                self.root.after(
                    0, lambda: messagebox.showerror("Connection Failed", output)
                )

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
            messagebox.showerror(
                "Critical Error",
                f"App crashed. Log saved to {crash_file}\n\n{error_msg}",
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
