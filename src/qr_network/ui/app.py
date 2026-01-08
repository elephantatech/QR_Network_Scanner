import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import webbrowser
import os
import sys
import time
import cv2
from PIL import Image, ImageTk

# Updated imports for refactor
from ..capture.scanner import QRCodeScanner
from ..net.manager import NetworkManager
from ..qr.parser import WiFiQRParser
from ..utils import RedactedLogger

# Components
from .components.dialogs import DialogManager
from .components.status_panel import StatusPanel
from .components.control_panel import ControlPanel
from .components.security_sheet import SecurityConfirmationSheet


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class QRNetworkApp(ctk.CTk):
    def __init__(self, debug=False):
        super().__init__()

        # System Theme Setup
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme(
            "blue"
        )  # Themes: "blue" (standard), "green", "dark-blue"

        self.title("QR Network Scanner")
        self.geometry("850x750")
        self.debug = debug

        # Determine log file path
        home_dir = os.path.expanduser("~")
        self.log_file = (
            os.path.join(home_dir, "qr_network_debug.log") if debug else None
        )

        # CLI Alias Command
        self.alias_cmd = 'alias qr-network="/Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner"'

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
            self.wm_iconphoto(False, icon_img)
            self.icon_img = icon_img  # Keep ref
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        # Initialize Redactor and Managers
        self._redactor = RedactedLogger(None)
        self.dialog_manager = DialogManager(self)
        self.network_mgr = NetworkManager()  # Initialize early

        # State
        self.scanner = QRCodeScanner()
        self.is_scanning = False
        self.camera_active = False
        self.is_paused = False

        self.setup_layout()
        self.create_native_menu()

        # Bind Focus Events
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def setup_layout(self):
        # Using CTkTabview instead of Notebook
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Scanner Tab
        self.tabview.add("  📷 Scanner  ")
        self.scanner_frame = self.tabview.tab("  📷 Scanner  ")

        # 2. Help Tab
        self.tabview.add("  ❓ Help & FAQ  ")
        self.help_frame = self.tabview.tab("  ❓ Help & FAQ  ")

        # Init Components inside frames (Pass self.scanner_frame as master)
        # Note: Components need to be updated to accept CTkFrame as master
        self.control_panel = ControlPanel(self.scanner_frame, self)

        # Access exposed vars
        self.confirm_connect = self.control_panel.confirm_connect
        self.add_only = self.control_panel.add_only

        self.status_panel = StatusPanel(self.scanner_frame)
        self.status_label = self.status_panel.status_label

        self.setup_help_ui()

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        redacted_msg = self._redactor.redact(message)

        if self.debug:
            print(f"[{timestamp}] {redacted_msg}")
            if self.log_file:
                try:
                    with open(self.log_file, "a") as f:
                        f.write(f"[{timestamp}] {redacted_msg}\n")
                except Exception:
                    pass

        # Update UI Log via component
        if hasattr(self, "status_panel"):
            self.status_panel.log(f"[{timestamp}] {redacted_msg}")

    def on_focus_in(self, event):
        if event.widget == self:
            self.is_paused = False

    def on_focus_out(self, event):
        if event.widget == self:
            self.is_paused = True

    def create_native_menu(self):
        # CTk doesn't have a native menu replacement, so we use standard tk.Menu attached to root
        # Since self is CTk (which inherits from Tk), this works fine.
        menubar = tk.Menu(self)
        app_menu = tk.Menu(menubar, name="apple")
        menubar.add_cascade(menu=app_menu)
        app_menu.add_command(
            label="About QR Network Scanner", command=self.dialog_manager.show_about
        )
        app_menu.add_separator()
        # Theme toggle is now built-in to system sync, but we can offer manual override
        theme_menu = tk.Menu(menubar, tearoff=0)
        app_menu.add_cascade(label="Appearance", menu=theme_menu)
        theme_menu.add_command(
            label="System", command=lambda: ctk.set_appearance_mode("System")
        )
        theme_menu.add_command(
            label="Dark", command=lambda: ctk.set_appearance_mode("Dark")
        )
        theme_menu.add_command(
            label="Light", command=lambda: ctk.set_appearance_mode("Light")
        )
        app_menu.add_separator()

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
            command=lambda: self.dialog_manager.show_permission_help("General"),
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="Copy CLI Alias", command=self.dialog_manager.show_cli_alias_help
        )
        help_menu.add_command(
            label="Install Alias to ~/.zshrc", command=self.install_alias_to_zshrc
        )

        self.config(menu=menubar)

    def open_html_help(self):
        try:
            path = resource_path("assets/help.html")
            url = "file://" + path
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open help file: {e}")

    def setup_help_ui(self):
        # Toolbar
        toolbar = ctk.CTkFrame(self.help_frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=10)

        def mk_btn(txt, cmd):
            b = ctk.CTkButton(
                toolbar, text=txt, command=cmd, height=32, font=("Arial", 12)
            )
            b.pack(side="right", padx=5)
            return b

        mk_btn(
            "🐛 Report Bug",
            lambda: webbrowser.open(
                "https://github.com/elephantatech/QR_Network_Scanner/issues"
            ),
        )
        mk_btn(
            "🌎 Online Docs",
            lambda: webbrowser.open(
                "https://github.com/elephantatech/QR_Network_Scanner/blob/main/HELP.md"
            ),
        )
        mk_btn("📄 Offline Guide", self.open_html_help)
        mk_btn("ℹ️ About", self.dialog_manager.show_about)
        mk_btn("💻 CLI Setup", self.dialog_manager.show_cli_alias_help)

        # Appearance Menu Option
        appearance_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["System", "Dark", "Light"],
            command=lambda v: ctk.set_appearance_mode(v),
            width=100,
        )
        appearance_menu.set("System")
        appearance_menu.pack(side="right", padx=5)

        # Help Text - Using CTkTextbox
        self.help_text = ctk.CTkTextbox(
            self.help_frame, wrap="word", font=("Segoe UI", 13)
        )
        self.help_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Insert Content (Formatting is simpler in Textbox, limited tags support in CTkTextbox compared to tk.Text but works well for plain text)
        # Note: CTkTextbox doesn't support advanced tagging like tk.Text fully yet in the same way, but let's try basic insert.

        content = """QR Network Scanner Guide

How to Use
1. (Optional) Toggle 'Confirm before connecting' or 'Add only' in the toolbar.
2. Click 'Scan Camera' or 'Scan Screen'.
3. Point camera at code OR ensure QR is visible on screen.
4. The app will auto-connect or save based on your settings.

CLI Mode (Terminal)
Run from Installed App:
• /Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner scan --help

Command Options:
• list-cameras: Show available cameras and IDs.
• --camera <ID>: Select a specific camera.
• --timeout <SEC>: Stop scan after N seconds.
• --screen: Scan from screen.
• --verbose (-v): Enable debug logs.

Run from Source (Dev):
• uv run qr-network scan

UI Options Explained
• Confirm before connecting: Shows a dialog with Network Name (SSID) and Security Type before initiating connection.
• Add to settings only: Saves the network profile to System Settings so you can connect manually later.

Security & Privacy
• Credentials stored in macOS Keychain.
• Logs are redacted (no passwords).
• Source code is open for review.

Frequently Asked Questions (FAQ)
Q: Camera shows 'Could not open camera'
A: This is a macOS permission issue. Click 'Check Permissions' in Help menu.

Q: It's scanning but not detecting?
A: Ensure good lighting. Moving closer/further helps. Timeout is 60s.

Q: What happens if I can't connect?
A: The app adds the network to macOS Settings. Click the WiFi icon in your menu bar to select it manually.
"""
        self.help_text.insert("0.0", content)
        self.help_text.configure(state="disabled")

    def start_camera_safe(self):
        try:
            # Get index from control panel
            idx = self.control_panel.get_selected_camera_index()

            # If changed/first time
            if self.scanner.camera_id != idx:
                self.scanner.stop_camera()
                self.scanner = QRCodeScanner(camera_id=idx)

            self.scanner.start_camera()
            self.camera_active = True
            self.is_scanning = True  # Enable QR detection when camera starts
            self.scan_start_time = time.time()  # Start timeout counter
            self.update_camera_feed()
            self.log("Camera started. Ready to scan.")

            # Update button state
            self.control_panel.set_scanning_state(True)
            self.control_panel.screen_scan_btn.configure(state="disabled")

        except Exception as e:
            self.log(f"Camera Error: {e}")
            if (
                "not found" in str(e).lower()
                or "authorization" in str(e).lower()
                or "access" in str(e).lower()
            ):
                self.dialog_manager.show_permission_help("Camera")
            else:
                self.dialog_manager.show_error_with_copy(
                    "Camera Error", f"Could not start camera:\n{e}"
                )

    def stop_camera(self):
        self.camera_active = False
        self.is_scanning = False  # Disable QR detection
        if self.scanner:
            self.scanner.stop_camera()

        self.status_label.configure(
            image=None, text="Camera is Off\nClick 'Scan Camera' to start"
        )
        # CTkLabel doesn't support compound image+text easily in same way?
        # Actually it does, but clearing image requires specific handling.
        # Check components impl.

        # Reset butons
        self.control_panel.set_scanning_state(False)
        self.control_panel.screen_scan_btn.configure(state="normal")

    def toggle_scan(self):
        if self.camera_active:
            self.stop_camera()
            self.log("Camera stopped by user.")
        else:
            self.start_camera_safe()

    def update_camera_feed(self):
        if not self.camera_active:
            return

        if self.is_paused:
            self.after(500, self.update_camera_feed)
            return

        ret, frame = self.scanner.get_frame()
        if not ret or frame is None:
            self.after(10, self.update_camera_feed)
            return

        # Display Frame on Label
        try:
            # Get dimensions
            w = self.status_label.winfo_width()
            h = self.status_label.winfo_height()
            if w < 10 or h < 10:
                w, h = 640, 480  # Default if not yet rendered

            # Convert CV2 to PIL
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)

            # Aspect Ratio Resize
            img_w, img_h = img.size
            ratio = min(w / img_w, h / img_h)
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)

            # CTkImage is preferred for scaling support
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))

            self.status_label.configure(image=ctk_img, text="")
            self.status_label._image = (
                ctk_img  # Keep ref (internal ctk prop, or just keep variable)
            )
            self.current_image = ctk_img  # Keep explicit ref
        except Exception:
            pass

        # Scan for QR if detection is enabled
        if self.is_scanning:
            # Timeout Check
            try:
                elapsed = time.time() - self.scan_start_time
                current_timeout = self.control_panel.timeout_var.get()
                if elapsed > current_timeout:
                    self.stop_camera()
                    self.log(f"Scan timed out after {current_timeout}s.")
                    # Use standard messagebox or CTk one? Standard is fine for alerts.
                    if messagebox.askretrycancel(
                        "Scan Timed Out",
                        f"No QR code detected within {current_timeout} seconds.\n\nRetry?",
                    ):
                        self.toggle_scan()  # Restart scan
                    return
                remaining = int(current_timeout - elapsed)

                # Overlay - we can't easily draw on CTkImage, assume CV2 drawing is sufficient on the frame source
                # Re-do drawing on frame for overlay
                display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.putText(
                    display_frame,
                    f"Scanning: {remaining}s",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                img_ov = Image.fromarray(display_frame)
                ctk_img_ov = ctk.CTkImage(
                    light_image=img_ov, dark_image=img_ov, size=(new_w, new_h)
                )
                self.status_label.configure(image=ctk_img_ov)
                self.current_image = ctk_img_ov

            except Exception:
                pass

            decoded_text, _ = self.scanner.detect_qr(frame)
            if decoded_text:
                self.log("QR Detected!")
                self.is_scanning = False
                self.stop_camera()
                self.process_qr_data(decoded_text)

        self.after(10, self.update_camera_feed)

    def scan_from_screen(self):
        self.stop_camera()  # Ensure camera is off
        self.log("Scanning screen...")
        try:
            decoded_text = self.scanner.scan_screen()
            if decoded_text:
                self.log("QR Code found on screen!")
                self.process_qr_data(decoded_text)
            else:
                self.log("No QR code found on screen.")
                messagebox.showinfo(
                    "Scan Screen",
                    "No QR code could be detected on your screen.\nMake sure the QR code is clearly visible.",
                )
        except Exception as e:
            self.log(f"Screen scan error: {e}")

    def process_qr_data(self, qr_data):
        try:
            wifi_info = WiFiQRParser.parse(qr_data)
            ssid = wifi_info["ssid"]
            password = wifi_info.get("password", "")
            security = wifi_info.get("type", "WPA")
            hidden = wifi_info.get("hidden", False)
        except ValueError as e:
            self.log(f"Error parsing QR: {e}")
            return

        hidden_msg = " (Hidden)" if hidden else ""
        self.log(f"Process QR detected: {ssid} ({security})")

        self.status_label.configure(
            text=f"Found: {ssid}{hidden_msg} ({security})",
            text_color="blue",  # CTk text_color
        )

        # Update confirmation dialog text
        self.confirm_dialog_text = (
            f"Network: {ssid}\nType: {security}{hidden_msg}\n\nDo you want to connect?"
        )

        self.pending_ssid = ssid
        self.pending_password = password
        self.pending_security = security
        self.pending_hidden = hidden

        self.stop_camera()
        self.log("Showing security confirmation sheet...")
        self.show_security_sheet(ssid, password, security, hidden)

    def show_security_sheet(self, ssid, password, security, hidden):
        def on_connect():
            self.connect_to_network(ssid, password, security, hidden, add_only=False)

        def on_add_only():
            self.connect_to_network(ssid, password, security, hidden, add_only=True)

        def on_cancel():
            self.log("Connection cancelled by user.")
            self.toggle_scan()

        SecurityConfirmationSheet(
            self,  # Parent is self (CTk)
            ssid,
            security,
            hidden,
            on_connect,
            on_add_only,
            on_cancel,
            {},  # Colors no longer needed, CTk handles it
        )

    def connect_to_network(
        self,
        ssid,
        password,
        security_type="WPA",
        hidden: bool = False,
        add_only: bool = False,
    ):
        """Adds and activates the network."""
        self.status_label.configure(
            text=f"Adding network {ssid}...", text_color="text_color"
        )  # reset color
        self.update()

        # Add to preferred list
        success, output = self.network_mgr.add_network(
            ssid, password, security_type, hidden=hidden
        )
        if success:
            self.log("Successfully added network.")
        else:
            self.log(f"Failed to add network: {output}")

        if add_only:
            self.log("Add Only mode enabled. Skipping connection.")
            messagebox.showinfo(
                "Network Added", f"Profile for '{ssid}' updated.\nAuto-connect skipped."
            )
            return

        self.log(f"Connecting to {ssid}...")
        current = self.network_mgr.get_current_network()
        if current == ssid:
            self.log(f"Already connected to {ssid}.")
        else:
            success, output = self.network_mgr.activate_network(ssid, password)
            if success:
                self.log(f"SUCCESS: Connected to {ssid}!")
                self.after(
                    0, lambda: messagebox.showinfo("Success", f"Connected to {ssid}")
                )
            else:
                self.log(f"Failed to connect: {output}")
                self.after(0, lambda: messagebox.showerror("Connection Failed", output))

    def install_alias_to_zshrc(self):
        try:
            home = os.path.expanduser("~")
            zshrc_path = os.path.join(home, ".zshrc")

            # Check if alias already exists
            if os.path.exists(zshrc_path):
                with open(zshrc_path, "r") as f:
                    content = f.read()
                    if "alias qr-network=" in content:
                        messagebox.showinfo(
                            "Info", "Alias 'qr-network' already exists in .zshrc"
                        )
                        return

            with open(zshrc_path, "a") as f:
                f.write(f"\n# QR Network Scanner Alias\n{self.alias_cmd}\n")

            messagebox.showinfo(
                "Success",
                f"Alias added to {zshrc_path}.\nPlease restart your terminal or run 'source ~/.zshrc'.",
            )

        except Exception as e:
            messagebox.showerror("Error", f"Could not write to .zshrc: {e}")

    def on_closing(self):
        self.camera_active = False
        if self.scanner:
            self.scanner.stop_camera()
        self.destroy()


def main(debug=False):
    import traceback

    try:
        app = QRNetworkApp(debug=debug)
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception:
        # Emergency Crash Logging
        error_msg = traceback.format_exc()
        crash_file = os.path.expanduser("~/qr_crash.log")
        with open(crash_file, "w") as f:
            f.write(error_msg)
        try:
            # Try to show error via TK if possible, though unlikely if crashed
            # We can use simple tk call here just to show message if possible
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Critical Error",
                f"App crashed. Log saved to {crash_file}\n\n{error_msg}",
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
