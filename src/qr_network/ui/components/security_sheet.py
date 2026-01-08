import customtkinter as ctk


class SecurityConfirmationSheet(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        ssid,
        security,
        hidden,
        on_connect,
        on_add_only,
        on_cancel,
        theme_colors_ignored=None,
    ):
        super().__init__(parent)
        self.title("Confirm Connection")
        self.geometry("500x400")

        # Center the window
        # CTk handles centering better if we let it, but manual ensure is safer
        self.update_idletasks()  # Ensure Parent geometry is known

        # Calculate center relative to parent or screen?
        # Toplevel implies separate window, let's just use standard geometry if possible or center manually
        # CTk usually centers new Toplevels? No, defaults to OS placement.
        # Manual centering:
        w = 500
        h = 420
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.transient(parent)  # Make modal-like
        self.make_modal()

        self.on_connect = on_connect
        self.on_add_only = on_add_only
        self.on_cancel = on_cancel

        # Layout
        self.setup_ui(ssid, security, hidden)

    def make_modal(self):
        self.lift()
        self.focus_force()
        self.grab_set()

    def setup_ui(self, ssid, security, hidden):
        # We don't need manual frames for bg, CTk handles it.
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        # Title
        ctk.CTkLabel(
            container,
            text="Network Detected",
            font=("Arial", 22, "bold"),
            text_color=("black", "white"),
        ).pack(pady=(10, 20))

        # Details Box
        details_frame = ctk.CTkFrame(
            container
        )  # Uses default theme color suitable for card
        details_frame.pack(fill="x", pady=10)

        # Content Grid
        grid_inner = ctk.CTkFrame(details_frame, fg_color="transparent")
        grid_inner.pack(padx=20, pady=20, fill="x")

        # SSID
        ctk.CTkLabel(
            grid_inner,
            text="Network:",
            font=("Arial", 14, "bold"),
            width=80,
            anchor="e",
        ).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(grid_inner, text=ssid, font=("Arial", 14)).grid(
            row=0, column=1, sticky="w", pady=5
        )

        # Security
        ctk.CTkLabel(
            grid_inner,
            text="Security:",
            font=("Arial", 14, "bold"),
            width=80,
            anchor="e",
        ).grid(row=1, column=0, padx=10, pady=5)
        hidden_text = " (Hidden)" if hidden else ""
        ctk.CTkLabel(
            grid_inner, text=f"{security}{hidden_text}", font=("Arial", 14)
        ).grid(row=1, column=1, sticky="w", pady=5)

        # Disclaimer
        ctk.CTkLabel(
            container,
            text="⚠️ No credentials are permanently stored by this application.\nThey are passed directly to macOS System Settings.",
            font=("Arial", 11),
            text_color="gray",
            justify="center",
        ).pack(pady=(20, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Join Network",
            command=self.connect_action,
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="#007AFF",
            hover_color="#0056b3",
        ).pack(fill="x", pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Add to Settings Only",
            command=self.add_only_action,
            font=("Arial", 13),
            fg_color="transparent",
            border_width=1,
            border_color="gray",
            text_color=("black", "white"),  # Ghost button
        ).pack(fill="x", pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel_action,
            fg_color="transparent",
            text_color="gray",
            font=("Arial", 12, "underline"),
            hover=False,
            height=20,
        ).pack(pady=(10, 0))

    def connect_action(self):
        self.destroy()
        if self.on_connect:
            self.on_connect()

    def add_only_action(self):
        self.destroy()
        if self.on_add_only:
            self.on_add_only()

    def cancel_action(self):
        self.destroy()
        if self.on_cancel:
            self.on_cancel()
