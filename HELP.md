# QR Network Scanner - User Guide & Troubleshooting

## 📱 How to Use (GUI App)

1. **Prepare:** Have a WiFi QR code ready (e.g., from an Android phone's WiFi sharing screen).
2. **Launch:** Open **QRNetworkScanner** from your Applications folder (or `dist/` folder).
3. **Scan:** Select the desired tab:
    * **Camera:** Point your webcam at a code.
    * **Screen:** Scan a code visible on your monitor.
    * **File:** Drag & drop or click to select an image/PDF file.
4. **Connect:** The app will automatically:
    * Detect the network credentials.
    * Add the network to your macOS System Settings.
    * Attempt to connect immediately.

---

## 💻 CLI Mode (Advanced Users)

If you prefer the terminal or want to run from source code using `uv`, you can use the Command Line Interface.

### Prerequisites

* **uv** installed (Python package manager).

### Running the CLI

**Preferred Method (Installed App):**

If you have installed the app to your Applications folder, run the CLI tool directly:

```bash
/Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner scan --help
```

### ⚡ Setting up an Alias (Recommended)

To run the app simply by typing `qr-network`, add an alias to your shell configuration. You have 3 ways to do this:

**Option A: Native Menu (Easiest)**

1. Open the app.
2. Go to **Help** in the macOS menu bar.
3. Click **Install Alias to ~/.zshrc** (Automated) or **Copy CLI Alias** (Manual Paste).

**Option B: GUI Button**

1. Open the **Help & FAQ** tab.
2. Click **💻 CLI Setup**.
3. Click **⚡ Install to ~/.zshrc** or **📋 Copy Alias**.

**Option C: Manual Configuration**

1. Open your terminal config (e.g., `~/.zshrc`).
2. Add the following line:

   ```bash
   alias qr-network="/Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner"
   ```

3. Restart your terminal. Now you can use:

   ```bash
   qr-network scan
   ```

**(Dev Mode) Running from Source:**

```bash
uv run qr-network scan
```

### CLI Options

* **`--verbose` / `-v`**: Enable detailed logging.
* **`--camera <ID>`**: Select a specific camera (Default: 0).
* **`list-cameras`**: List extracted camera names and IDs.
* **`--timeout <SECONDS>`**: Set timeout (Default: 60s).
* **`--screen`**: Scan from screen.
* **`--file <PATH>`**: Scan from local image/PDF file.

**Example:**

```bash
/Applications/QRNetworkScanner.app/Contents/MacOS/QRNetworkScanner scan --verbose --timeout 30
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
