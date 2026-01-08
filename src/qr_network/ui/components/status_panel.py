import customtkinter as ctk


class StatusPanel:
    def __init__(self, parent):
        """
        :param parent: Parent frame (usually scanner_frame)
        """
        # Status Label (The big text near camera)
        self.status_label = ctk.CTkLabel(
            parent,
            text="Camera is Off\nClick 'Scan Camera' to start",
            fg_color="black",
            text_color="white",
            corner_radius=6,  # Optional rounded corners if not filling logic
        )
        self.status_label.pack(pady=5, padx=10, expand=True, fill="both")

        # Log Area logic
        self.log_frame = ctk.CTkFrame(parent)  # Default frame styling
        # self.log_frame.configure(fg_color="transparent") # Or specific color
        self.log_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Label for log?
        log_label = ctk.CTkLabel(
            self.log_frame, text="Activity Log", font=("Arial", 12, "bold")
        )
        log_label.pack(anchor="w", padx=10, pady=(5, 0))

        self.log_area = ctk.CTkTextbox(
            self.log_frame, height=150, activate_scrollbars=True
        )
        self.log_area.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_area.configure(state="disabled")

    def log(self, message):
        """Append a message to the log area."""
        self.log_area.configure(state="normal")
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def update_status(self, text, text_color="white", fg_color="black"):
        """Update the status label."""
        self.status_label.configure(text=text, text_color=text_color, fg_color=fg_color)

    def update_theme(self, colors):
        """No longer used, kept for compatibility if needed or pass."""
        pass
