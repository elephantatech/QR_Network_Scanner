<p align="center">
  <img src="assets/icon.png" alt="QR Network Scanner Logo" width="128" height="128">
</p>

# QR Network Scanner 📶

[![CI/CD](https://github.com/elephantatech/QR_Network_Scanner/actions/workflows/build.yml/badge.svg)](https://github.com/elephantatech/QR_Network_Scanner/actions/workflows/build.yml)

![Beta](https://img.shields.io/badge/status-Beta-orange) ![macOS](https://img.shields.io/badge/platform-macOS-lightgrey) ![License](https://img.shields.io/badge/license-Apache%202.0-blue)

A native macOS utility to scan WiFi QR codes (from Android/iOS sharing) and automatically connect your Mac to the network. No more typing long, complex passwords!

![Demo](https://via.placeholder.com/800x450.png?text=Demo+GIF+Here)
*(Add a demo GIF here showing the scan & connect flow)*

## 🔒 Privacy & Security First

**Your WiFi credentials never leave your device.**

* **Local Processing:** All scanning and QR code parsing happens 100% locally on your machine using `zxing-cpp` and standard macOS APIs.
* **No Analytics:** This app does not track your usage or collect any data.
* **Open Source:** The code is fully open source so you can verify exactly what it does.

## 🚀 Installation

### Option 1: Download the App (Recommended)

1. Go to the [Releases Page](../../releases).
2. Download the latest `QRNetworkScanner_v0.1.0-beta.zip`.
3. Unzip and drag `QRNetworkScanner.app` to your Applications folder.
4. **Note:** On first launch, you may need to Right-Click > Open to bypass macOS security checks for unsigned apps.

### Option 2: Install via Terminal (Developers)

If you prefer running from source or want the CLI tool:

```bash
# Clone the repo
git clone https://github.com/elephantatech/QR_Network_Scanner.git
cd QR_Network_Scanner

# Install with uv (recommended)
uv sync
```

## 📖 Usage

### GUI Mode

Launch the visual scanner:

```bash
uv run qr-network gui
```

1. **Optional:** Check "Confirm before connecting" to review network details first.
2. **Optional:** Check "Add to settings only" if you don't want to connect immediately.
3. **Tabs:**
   * **Camera:** Scan using your webcam.
   * **Screen:** Scan a QR code visible on your screen (e.g., from a website).
   * **File:** Drag & Drop or select an image/PDF containing a QR code.
4. Click **Start Scanning** / **Scan Screen** / **Scan File**.
5. The app will act based on your settings (Auto-connect or Save-only).

### CLI Mode (Terminal)

Perfect for power users who live in the terminal.

**Option A: Using the Installed App (No Python required)**
If you installed `QRNetworkScanner.app` to your Applications folder:

```bash
/Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner scan
```

*(Tip: You can alias this in your shell profile: `alias qr-scanner='/Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner'`)*

**Option B: Running from Source**

```bash
uv run qr-network scan
```

**Options:**

* `--timeout <seconds>`: Stop scanning after N seconds (default: 60).
* `--camera <id>`: Use a specific camera index (default: 0).
* `list-cameras`: List all available cameras and their IDs.
* `--screen`: Scan from the screen instead of the camera.
* `--file <path>`: Scan from a local image or PDF file.
* `-v, --verbose`: Show debug logs.

**Example:**

```bash
# Scan with verbose logging and a 30s timeout
uv run qr-network scan --verbose --timeout 30
```

> **Note:** The CLI returns specific exit codes (0=Success, 10=Camera Error, 20=Network Error, 30=Timeout, 40=User Cancel) for easier scripting.

## ⚠️ Permissions & Troubleshooting

First time running? macOS is strict! You will see prompts for:

* **Camera:** Required to scan the QR code.
* **Location/WiFi:** Required to modify system network settings.

**"Camera not found" error?**

1. Open **System Settings** > **Privacy & Security** > **Camera**.
2. Ensure your terminal (e.g., iTerm2, Terminal) or `QRNetworkScanner` has permission.
3. Restart the app.

## 🚧 Known Limitations (Beta)

* **Supported Encryption:** WPA, WPA2, WPA3, and WEP.
* **Hidden Networks:** Currently requires the network to be broadcast.
* **Enterprise:** WPA2-Enterprise QR codes are not yet supported.

## 🤝 Contributing

Found a bug? Have a feature request?

* [Report a Bug](.github/ISSUE_TEMPLATE/bug_report.md)
* [Request a Feature](.github/ISSUE_TEMPLATE/feature_request.md)

See [CONTRIBUTING.md](CONTRIBUTING.md) for developer setup and guidelines.

License: Apache 2.0
