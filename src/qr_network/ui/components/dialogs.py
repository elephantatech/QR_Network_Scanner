import customtkinter as ctk
import webbrowser
import os
import sys
from PIL import Image
import platform


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class DialogManager:
    def __init__(self, app):
        """
        :param app: Reference to the main QRNetworkApp instance (which is now root CTk).
        """
        self.app = app
        self.root = app

    def show_error_with_copy(self, title, message):
        """Shows an error dialog with a 'Copy Debug Info' button."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x350")

        # Make modal-ish
        dialog.transient(self.root)
        dialog.lift()
        dialog.focus_force()

        # Icon/Title
        title_label = ctk.CTkLabel(
            dialog,
            text=f"❌ {title}",
            font=("Arial", 16, "bold"),
            text_color="#e74c3c",  # Red
        )
        title_label.pack(pady=15)

        # Message Area
        txt = ctk.CTkTextbox(
            dialog, height=80, font=("Arial", 12), wrap="word", corner_radius=8
        )
        txt.insert("0.0", message)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Info to copy
        debug_info = (
            f"Error: {title}\n"
            f"Message: {message}\n"
            f"App Version: 0.1.0-beta.18\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"Python: {sys.version.split()[0]}"
        )

        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(debug_info)
            self.root.update()
            btn_copy.configure(text="Copied! ✓")

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        btn_copy = ctk.CTkButton(
            btn_frame, text="📋 Copy Debug Info", command=copy_to_clipboard
        )
        btn_copy.pack(side="left", padx=20)

        ctk.CTkButton(
            btn_frame, text="Close", command=dialog.destroy, fg_color="gray"
        ).pack(side="right", padx=20)

    def show_permission_help(self, focus="Camera"):
        """Shows a helper window to guide user to System Settings."""
        perm_window = ctk.CTkToplevel(self.root)
        perm_window.title("⚠️ Permission Required")
        perm_window.geometry("500x450")
        perm_window.transient(self.root)

        pad = ctk.CTkFrame(perm_window, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=20, pady=20)

        # Icon
        try:
            icon_path = resource_path("assets/icon.png")
            icon_img = Image.open(icon_path)
            # Use CTk Image
            icon_ctk = ctk.CTkImage(
                light_image=icon_img, dark_image=icon_img, size=(64, 64)
            )
            icon_label = ctk.CTkLabel(pad, image=icon_ctk, text="")
            icon_label.pack(pady=(0, 10))
        except Exception:
            pass

        ctk.CTkLabel(
            pad,
            text=f"{focus} Access Needed",
            font=("Arial", 20, "bold"),
            text_color="#e74c3c",
        ).pack(pady=(0, 10))

        msg = (
            f"macOS requires you to explicitly grant access for this app to use the {focus}.\n\n"
            "1. Click the button below to open System Settings.\n"
            f"2. Find 'QR Network Scanner' (or Terminal if running via CLI) in the list.\n"
            "3. Enable the toggle.\n"
            "4. IMPORTANT: You must restart the app/terminal for changes to take effect."
        )

        msg_label = ctk.CTkLabel(
            pad,
            text=msg,
            justify="left",
            wraplength=450,
            font=("Arial", 13),
        )
        msg_label.pack(pady=10)

        # Deep Links
        def open_settings(url):
            webbrowser.open(url)

        btn_frame = ctk.CTkFrame(pad, fg_color="transparent")
        btn_frame.pack(pady=20)

        if focus == "Camera":
            ctk.CTkButton(
                btn_frame,
                text="Open Camera Settings ↗",
                command=lambda: open_settings(
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_Camera"
                ),
            ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Open Wi-Fi Settings ↗",
            command=lambda: open_settings(
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Location"
            ),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            pad, text="Close", command=perm_window.destroy, fg_color="gray"
        ).pack(side="bottom")

    def show_cli_alias_help(self):
        """Shows a dialog with CLI alias instructions."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("CLI Setup")
        dialog.geometry("550x400")
        dialog.transient(self.root)

        pad = ctk.CTkFrame(dialog, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            pad,
            text="Run from Terminal",
            font=("Arial", 18, "bold"),
            text_color="#3498db",
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            pad,
            text="To run this app from your terminal using 'qr-network', paste this alias into your shell config (e.g., ~/.zshrc):",
            justify="left",
            wraplength=500,
        ).pack(anchor="w")

        # Alias Command - Use Entry for easy copy if needed, or Textbox
        cmd_entry = ctk.CTkentry(
            pad
        )  # Wait, simple Textbox better for multiline wrapping if needed, but alias is single line usually.
        # But Entry allows selecting.
        cmd_entry = ctk.CTkEntry(pad, width=500, font=("Courier", 12))
        cmd_entry.insert(0, self.app.alias_cmd)
        cmd_entry.configure(state="readonly")
        cmd_entry.pack(pady=15)

        def copy_cmd_local():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.app.alias_cmd)
            self.root.update()
            btn_copy.configure(text="Copied! ✓")

        btn_copy = ctk.CTkButton(pad, text="📋 Copy Alias", command=copy_cmd_local)
        btn_copy.pack(pady=5)

        btn_install = ctk.CTkButton(
            pad,
            text="⚡ Install to ~/.zshrc",
            command=self.app.install_alias_to_zshrc,
            fg_color="#f39c12",
            hover_color="#d35400",
        )
        btn_install.pack(pady=5)

        ctk.CTkLabel(
            pad,
            text="After adding, restart terminal and run:\n  qr-network scan",
            text_color="gray",
            justify="center",
        ).pack(pady=10)

        ctk.CTkButton(pad, text="Close", command=dialog.destroy, fg_color="gray").pack(
            side="bottom"
        )

    def show_about(self):
        # Pause camera updates
        was_active = getattr(self.app, "camera_active", False)
        self.app.camera_active = False

        about_window = ctk.CTkToplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x380")
        about_window.resizable(False, False)
        about_window.transient(self.root)

        pad_frame = ctk.CTkFrame(about_window, fg_color="transparent")
        pad_frame.pack(fill="both", expand=True, padx=20, pady=20)

        try:
            icon_path = resource_path("assets/icon.png")
            icon_img = Image.open(icon_path)
            icon_ctk = ctk.CTkImage(
                light_image=icon_img, dark_image=icon_img, size=(80, 80)
            )
            ctk.CTkLabel(pad_frame, image=icon_ctk, text="").pack(pady=(0, 10))
        except Exception:
            pass

        ctk.CTkLabel(
            pad_frame, text="QR Network Scanner", font=("Arial", 20, "bold")
        ).pack(pady=(0, 5))

        ctk.CTkLabel(pad_frame, text="v0.1.0-beta.19", text_color="gray").pack()

        copyright_text = (
            "Copyright © 2026\nElephanta Technologies and Design Inc\n\n"
            "Developed by elephantatech"
        )
        ctk.CTkLabel(pad_frame, text=copyright_text, justify="center").pack(pady=20)

        ctk.CTkLabel(
            pad_frame,
            text="Licensed under Apache License 2.0",
            text_color="#3498db",
            cursor="hand2",
        ).pack()

        # Close Handler
        def close_about():
            about_window.destroy()
            if was_active:
                self.app.camera_active = True
                if hasattr(self.app, "update_camera_feed"):
                    self.app.update_camera_feed()

        ctk.CTkButton(
            pad_frame, text="Close", command=close_about, width=100, fg_color="gray"
        ).pack(side="bottom", pady=10)
        about_window.protocol("WM_DELETE_WINDOW", close_about)
