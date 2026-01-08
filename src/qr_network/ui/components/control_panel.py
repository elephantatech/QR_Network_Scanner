import tkinter as tk
import customtkinter as ctk
from ...utils import get_camera_names


class ControlPanel(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        """
        :param parent: Parent frame (scanner_frame)
        :param app: Reference to main app (callbacks)
        """
        super().__init__(parent, **kwargs)
        self.app = app

        # State vars
        self.confirm_connect = tk.BooleanVar(value=True)
        self.add_only = tk.BooleanVar(value=False)
        self.camera_idx_var = tk.StringVar()
        self.timeout_var = tk.IntVar(value=60)
        self.camera_map = {}

        self.setup_ui()
        self.pack(
            fill="x", padx=20, pady=10
        )  # Self-pack if convenient, or let parent do it. Let's do it consistent with previous usage.

    def setup_ui(self):
        # 1. Camera Selection
        cam_frame = ctk.CTkFrame(self, fg_color="transparent")
        cam_frame.pack(side="left", padx=10, pady=10)

        cam_label = ctk.CTkLabel(
            cam_frame, text="Camera Source:", font=("Arial", 12, "bold")
        )
        cam_label.pack(anchor="w")

        camera_names = get_camera_names()
        if camera_names:
            self.camera_idx_var.set(camera_names[0])
            self.camera_map = {name: i for i, name in enumerate(camera_names)}
        else:
            self.camera_idx_var.set("No Camera")
            camera_names = ["No Camera"]

        self.cam_combo = ctk.CTkOptionMenu(
            cam_frame, variable=self.camera_idx_var, values=camera_names, width=200
        )
        self.cam_combo.pack(pady=(5, 0))

        # 2. Timeout Setting
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(side="left", padx=20, pady=10)

        timeout_label = ctk.CTkLabel(
            time_frame, text="Scan Timeout:", font=("Arial", 12, "bold")
        )
        timeout_label.pack(anchor="w")

        spin_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        spin_frame.pack(pady=(5, 0), anchor="w")

        # CTk doesn't have Spinbox by default usually, simplest is Entry or OptionMenu or dedicated Spinbox extension.
        # Simple entry is fine for now, or OptionMenu with predefined values.
        # Let's use OptionMenu for simplicity and touch friendliness
        timeout_values = ["15", "30", "60", "120", "300"]
        self.timeout_menu = ctk.CTkOptionMenu(
            spin_frame, variable=self.timeout_var, values=timeout_values, width=80
        )
        self.timeout_menu.pack(side="left")
        # Ensure var is set to string representation if using OptionMenu with mixed types?
        # CTkOptionMenu uses string values. We need to sync.
        self.timeout_var.set(60)
        self.timeout_menu.configure(
            variable=self.camera_idx_var
        )  # Wait, variable binding in CTk is tricky sometimes if types mismatch.
        # Actually let's use a simple callback wrapper or just bind stringvar.
        # Re-implement timeout logic:
        self.timeout_str_var = tk.StringVar(value="60")
        self.timeout_menu.configure(variable=self.timeout_str_var)
        self.timeout_var = (
            self.timeout_str_var
        )  # Alias for app access (will need int conversion on get)

        sec_label = ctk.CTkLabel(spin_frame, text="sec")
        sec_label.pack(side="left", padx=5)

        # 3. Actions (Right Aligned)
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(side="right", padx=10, pady=10)

        self.scan_btn = ctk.CTkButton(
            action_frame,
            text="📷 Scan Camera",
            command=self.app.toggle_scan,
            fg_color="#2ecc71",  # Green
            hover_color="#27ae60",
            cursor="hand2",
            font=("Arial", 13, "bold"),
            height=40,
        )
        self.scan_btn.pack(side="left", padx=10)

        self.screen_scan_btn = ctk.CTkButton(
            action_frame,
            text="🖥️ Scan Screen",
            command=self.app.scan_from_screen,
            fg_color="#3498db",  # Blue
            hover_color="#2980b9",
            cursor="hand2",
            font=("Arial", 13, "bold"),
            height=40,
        )
        self.screen_scan_btn.pack(side="left", padx=10)

    def set_scanning_state(self, is_scanning):
        """Updates button appearance based on scanning state"""
        if is_scanning:
            self.scan_btn.configure(
                text="🛑 Stop Camera", fg_color="#e74c3c", hover_color="#c0392b"
            )
        else:
            self.scan_btn.configure(
                text="📷 Scan Camera", fg_color="#2ecc71", hover_color="#27ae60"
            )

    def get_selected_camera_index(self):
        name = self.camera_idx_var.get()
        return self.camera_map.get(name, 0)
