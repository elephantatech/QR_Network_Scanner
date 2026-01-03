# Changelog

All notable changes to the **QR Network Scanner** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-beta.6] - 2026-01-03

### Added
- **Scan from Screen:** New feature to scan WiFi QR codes directly from the screen(s) without using the camera.
- **CLI Support:** Added `--screen` flag to the `scan` command for screen scanning logic.

### Changed
- **GUI Layout:** Reorganized scan buttons side-by-side with icons for better usability.
- **Camera Logic:** Disabled camera auto-start; camera only activates when explicitly requested.
- **Preview:** Improved camera preview resizing and added a placeholder state when the camera is off.

## [0.1.0-beta.5] - 2026-01-02

### Changed
- **Logo:** Updated application icon (`assets/icon.png`) with a new design.

## [0.1.0-beta.4] - 2026-01-02

### Added
- **Native Help Menu:** Separate "Online Documentation" (GitHub) and "Offline Guide" (Local HTML) items in the native macOS menu bar.

### Changed
- **UI Theme:** Switched to `ttk` "clam" theme for consistent cross-platform styling.
- **Start Button:** Migrated to `ttk.Button` with custom `Green.TButton` (Start) and `Red.TButton` (Stop) styles to fix color rendering issues on macOS.
- **Help Menu:** Renamed native menu to `"Help "` (with a trailing space) to bypass macOS's automatic search bar injection.

### Fixed
- **UI Crash:** Resolved `TclError` caused by unsupported background color attributes on native buttons.
- **Search Bar:** Removed persistent search bar from the Help tab toolbar and native menu.

## [0.1.0-beta.3] - 2026-01-01

### Added
- **GitHub Actions:** Automated release workflow (`build.yml`) to build and sign macOS app bundles on push/tag.
- **Documentation:** Created `HELP.md` and `assets/help.html` for comprehensive user guides.

### Fixed
- **Camera Crash:** Fixed specific AVFoundation threading crashes by ensuring all internal camera logic runs on the main thread via `root.after` polling.
- **Permissions:** Resolved specific "Camera not found" errors related to macOS privacy entitlements.
- **Signing:** Added `entitlements.plist` to properly request Camera access in the hardened runtime.

## [0.1.0-beta.2] - 2025-12-30

### Added
- **App Bundle:** Implemented `build_release.py` to package the Python script into a standalone `QRNetworkScanner.app`.
- **Icon:** Added custom application icon using `pillow` and `iconphoto`.

### Fixed
- **Threading:** Major refactor to remove background threads, switching to an event-driven loop to prevent Tkinter "run loop" freezes on macOS.

## [0.1.0-beta.1] - 2025-12-25

### Added
- Initial Beta Release.
- QR Code Scanning using `zxing-cpp` and OpenCV.
- WiFi Network Management (Add/Connect) via `networksetup` command wrapper.
- CLI Mode for terminal-based scanning.
