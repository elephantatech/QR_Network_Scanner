# Security Policy & Threat Model

## Credential Storage

QR Network Scanner **does not** store Wi-Fi passwords in plain text files or its own database.

Instead, it leverages the native macOS `networksetup` utility. When a network is added:

1. The operating system handles the storage of the SSID and Password.
2. Credentials are securely stored in the **macOS System Keychain**.
3. The app does not retain the password in memory after the connection attempt is initiated.

## Threat Model

### Assets

* **Wi-Fi Credentials:** The SSID and Password scanned from QR codes.
* **System Network Settings:** The ability to modify the list of known networks.

### Threats & Mitigations

| Threat | Description | Mitigation |
| :--- | :--- | :--- |
| **Malicious QR Codes** | A QR code could contain a fake SSID/Password or attempt to exploit input parsing. | • **User Confirmation:** The "Confirm before Connect" feature allows users to inspect the SSID and Encryption type before any system action is taken.<br>• **Input Validation:** The parser strictly enforces standard Wi-Fi QR code formats (`WIFI:S:...;P:...;`). |
| **Log Leakage** | Debug logs could accidentally expose passwords. | • **Redacted Logging:** All logs passed through the app's logger are filtered. Regex patterns replace password fields (`P:secret;`) with redacted placeholders (`P:***;`). |
| **Untrusted Input** | Scanning a code from an untrusted source. | • **"Add Only" Mode:** Users can choose to add the network profile without automatically connecting, preventing immediate network association. |

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it via [GitHub Issues](https://github.com/elephantatech/QR_Network_Scanner/issues) or email <security@elephantatech.com> (example).
