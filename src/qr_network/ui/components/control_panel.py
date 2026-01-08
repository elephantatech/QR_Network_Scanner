import tkinter as tk
import customtkinter as ctk
from ...utils import get_camera_names


class ScannerInterface(ctk.CTkTabview):
    def __init__(self, parent, app, **kwargs):
        """
        :param parent: Parent frame/widget
        :param app: Reference to main app (callbacks)
        """
        super().__init__(parent, **kwargs)
        self.app = app

        # State vars
        self.camera_idx_var = tk.StringVar()
        self.timeout_str_var = tk.StringVar(value="60")
        self.timeout_var = self.timeout_str_var  # For app compatibility
        self.camera_map = {}

        # Create Tabs
        self.add("Camera")
        self.add("Screen")
        self.add("File")

        # Setup Tab Contents
        self.setup_camera_tab()
        self.setup_screen_tab()
        self.setup_file_tab()

        # Configure Tab Change Event to stop camera if leaving Camera tab
        self.configure(command=self.on_tab_change)

    def on_tab_change(self):
        """Handle tab changes."""
        selected_tab = self.get()
        if selected_tab != "Camera":
            if self.app.is_scanning:
                self.app.stop_camera()

    def setup_camera_tab(self):
        tab = self.tab("Camera")

        # --- Top Controls: Source selection and Timeout ---
        # Grid layout for better alignment
        # Row 0: Camera Selection
        # Row 1: Timeout | Scan Button

        controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Camera Source
        ctk.CTkLabel(controls_frame, text="Camera:", font=("Arial", 12, "bold")).pack(
            side="left", padx=(0, 5)
        )

        camera_names = get_camera_names()
        if camera_names:
            self.camera_idx_var.set(camera_names[0])
            self.camera_map = {name: i for i, name in enumerate(camera_names)}
        else:
            self.camera_idx_var.set("No Camera")
            camera_names = ["No Camera"]

        self.cam_combo = ctk.CTkOptionMenu(
            controls_frame, variable=self.camera_idx_var, values=camera_names, width=160
        )
        self.cam_combo.pack(side="left", padx=(0, 20))

        # Timeout
        ctk.CTkLabel(controls_frame, text="Timeout:", font=("Arial", 12, "bold")).pack(
            side="left", padx=(0, 5)
        )

        timeout_values = ["15", "30", "60", "120", "300"]
        self.timeout_menu = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.timeout_str_var,
            values=timeout_values,
            width=70,
        )
        self.timeout_menu.pack(side="left")
        ctk.CTkLabel(controls_frame, text="s").pack(side="left", padx=2)

        # Start/Stop Button (Right aligned)
        self.scan_btn = ctk.CTkButton(
            controls_frame,
            text="📷 Start Camera",
            command=self.app.toggle_scan,
            fg_color="#2ecc71",  # Green
            hover_color="#27ae60",
            cursor="hand2",
            font=("Arial", 13, "bold"),
            width=120,
        )
        self.scan_btn.pack(side="right", padx=5)

        # --- Preview Area (Takes remaining space) ---
        preview_frame = ctk.CTkFrame(tab, fg_color="#000000")  # Black bg for video
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.camera_label = ctk.CTkLabel(
            preview_frame, text="Camera Preview", text_color="gray"
        )
        self.camera_label.pack(fill="both", expand=True)

    def setup_screen_tab(self):
        tab = self.tab("Screen")

        # Center the content
        center_frame = ctk.CTkFrame(tab, fg_color="transparent")
        center_frame.pack(expand=True)

        self.screen_scan_btn = ctk.CTkButton(
            center_frame,
            text="🖥️ Scan Screen",
            command=self.app.scan_from_screen,
            fg_color="#3498db",  # Blue
            hover_color="#2980b9",
            cursor="hand2",
            font=("Arial", 18, "bold"),
            height=60,
            width=250,
        )
        self.screen_scan_btn.pack(pady=20)

        ctk.CTkLabel(
            center_frame,
            text="Ensures the QR code is visible on any connected monitor.",
            text_color="gray",
        ).pack(pady=5)

    def setup_file_tab(self):
        tab = self.tab("File")

        # Center content: Large Drop Zone Visual
        center_frame = ctk.CTkFrame(tab, fg_color="transparent")
        center_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # We simulate a drop zone using a large button
        self.file_scan_btn = ctk.CTkButton(
            center_frame,
            text="⬇️\n\nDrop File Here\n\nor\n\nClick to Select File",
            command=self.app.scan_from_file_action,
            fg_color="transparent",
            border_width=2,
            border_color="#f39c12",  # Orange border
            text_color=("gray10", "gray90"),  # Adaptive text
            hover_color=("gray85", "gray25"),
            cursor="hand2",
            font=("Arial", 16, "bold"),
            corner_radius=15,
        )
        self.file_scan_btn.pack(fill="both", expand=True)

        ctk.CTkLabel(
            center_frame,
            text="Supports PNG, JPG, BMP, PDF",
            text_color="gray",
            font=("Arial", 12),
        ).pack(pady=(10, 0))

    def set_scanning_state(self, is_scanning):
        """Updates button appearance based on scanning state"""
        # Ensure we are on the Camera tab if scanning starts
        if is_scanning:
            self.set("Camera")
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
