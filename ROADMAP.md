# QR Network Scanner - v1.x Roadmap

This document outlines the planned features and technical improvements for the 1.x release cycle of the QR Network Scanner.

## 🚀 Priority Features

### 1. Wi-Fi QR Generator (Share Tab) [#2](https://github.com/elephantatech/QR_Network_Scanner/issues/2)

Allows users to share saved macOS networks by generating standard Wi-Fi QR codes.

- **Status**: 📅 Planned
- **Implementation**: `networksetup` + Keychain + `qrcode` lib.

### 2. Seamless Distribution (Notarization) [#3](https://github.com/elephantatech/QR_Network_Scanner/issues/3)

Eliminate the "Right-click -> Open" friction by implementing Apple Notarization.

- **Status**: 📅 Planned
- **Implementation**: GitHub Actions + `notarytool`.

### 3. In-App Diagnostics [#4](https://github.com/elephantatech/QR_Network_Scanner/issues/4)

Built-in permission checks and debug reporting to reduce support overhead.

- **Status**: 📅 Planned
- **Implementation**: Deep-links to System Settings + Redacted debug info.

### 4. CLI for Automation [#5](https://github.com/elephantatech/QR_Network_Scanner/issues/5)

JSON output and connectivity control for power users and script integration.

- **Status**: 📅 Planned
- **Implementation**: `--json` flag + Standardized exit codes.

### 5. Rock-Solid PDF Scanning [#12](https://github.com/elephantatech/QR_Network_Scanner/issues/12)

Exhaustive scanning with DPI and rotation fallbacks for reliable file processing.

- **Status**: 📅 Planned
- **Implementation**: Multi-page rendering + Rotation detection.

---

## 🛡️ Security Hardening

- [ ] **Home Directory Redaction** [#6](https://github.com/elephantatech/QR_Network_Scanner/issues/6): Auto-mask `/Users/[USER]/` in all logs.
- [ ] **Transient Clipboard** [#7](https://github.com/elephantatech/QR_Network_Scanner/issues/7): Auto-clear sensitive data after 60 seconds.
- [ ] **Centralized Metadata** [#8](https://github.com/elephantatech/QR_Network_Scanner/issues/8): Unified version control via `pyproject.toml`.
- [ ] **Privacy Transparency** [#9](https://github.com/elephantatech/QR_Network_Scanner/issues/9): Formalize diagnostics policy in `SECURITY.md`.

---

## 🛠️ Maintenance & Optimization

- [ ] Refactor UI components for better modularity.
- [ ] Expand unit test coverage for macOS-specific edge cases.
- [ ] Optimize camera startup time on older hardware.

---
*Last updated: 2026-01-11*
