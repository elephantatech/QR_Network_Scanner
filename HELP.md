# QR Network Scanner - User Guide & Troubleshooting

## 📱 How to Use (GUI App)

1. **Prepare:** Have a WiFi QR code ready (e.g., from an Android phone's WiFi sharing screen).
2. **Launch:** Open **QRNetworkScanner** from your Applications folder (or `dist/` folder).
3. **Scan:** Go to the **Scanner** tab and click **Start Scanning**.
4. **Connect:** Point your camera at the code. The app will automatically:
    * Detect the network credentials.
    * Add the network to your macOS System Settings.
    * Attempt to connect immediately.

---

## 💻 CLI Mode (Advanced Users)

If you prefer the terminal or want to run from source code using `uv`, you can use the Command Line Interface.

### Prerequisites

* **uv** installed (Python package manager).

### Running from Repo

Clone the repository and run:

```bash
# GUI Mode
uv run qr-network gui

# CLI Scanning Mode
uv run qr-network scan
```

### CLI Options

When running `qr-network scan`:

* **`--verbose` / `-v`**: Enable detailed logging (useful for debugging).
* **`--camera <ID>`**: Select a specific camera (Default: 0).
* **`--timeout <SECONDS>`**: Set how long to wait before stopping (Default: 60s).

### 🍎 Running CLI from Built App (.app)

If you have built the application (`dist/QRNetworkScanner.app`), you cannot use the `open` command with arguments. You must run the executable directly:

```bash
# Correct way to run CLI from the .app
./dist/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner scan --verbose
```

*(Note: You may need to grant Terminal permission to access the Camera)*

**Example:**

```bash
uv run qr-network scan --verbose --timeout 30
```

---

## ❓ Troubleshooting (FAQ)

### 🔴 "Could not open camera" / Camera Black Screen

This is almost always a **macOS Permission Issue**.

1. **Grant Permission:** When you first run the app, macOS will ask if "QRNetworkScanner" can access the camera. Click **Allow**.
2. **RESTART REQUIRED:** After clicking "Allow", you often **MUST Quit and Restart the application** for the camera to actually start working. This is a known macOS security behavior.
3. **Check Settings:** If it still fails:
    * Open **System Settings**.
    * Go to **Privacy & Security** > **Camera**.
    * Ensure the toggle next to **QRNetworkScanner** is turned **ON**.

### 🟡 Scanning but not detecting?

* **Distance:** Try moving the QR code slightly closer or further away (approx. 6-12 inches).
* **Lighting:** Ensure there is decent lighting on the QR code.
* **Focus:** If your webcam has manual focus, ensure it's sharp. The app uses `zxing-cpp` (industrial grade detection), so it tolerates angles well, but blur can be an issue.

### � Where are the Logs?

* **Debug Log:** `~/qr_network_debug.log` (Home Directory)
  * *Only created if you run with* `--debug`
  * Contains detailed application activity.
* **Crash Log:** `~/qr_crash.log`
  * Created automatically if the application crashes unexpectedly.

To view them via Terminal:

```bash
cat ~/qr_network_debug.log
```

---

## 🛠 Building from Source

To create the standalone macOS Application yourself:

```bash
uv run python build_release.py
```

The app will be generated in `dist/QRNetworkScanner.app`.
