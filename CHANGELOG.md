# Changelog

All notable changes to the **QR Network Scanner** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-beta.19] - 2026-01-08

### Added

- **Scanner UI Tabs:** Introduced dedicated tabs for **Camera**, **Screen**, and **File** scanning.
- **File Scanning:** Added drag-and-drop support for images and PDFs (first 3 pages).
- **Screen Scanning:** Dedicated button to scan the entire screen for QR codes.
- **Unit Tests:** Added tests for screen and file scanning functionality.
- **Dev Tools:** Integrated `pre-commit` for code quality checks.

### Fixed

- **UI Freeze:** Fixed a `text_color` typo in `connect_to_network` that caused the application to crash/freeze when initiating a connection.
- **Dialog Visibility:** Ensured `messagebox` alerts (Success/Failure) appear correctly over the main window by setting the `parent` attribute explicitly.

## [0.1.0-beta.18] - 2026-01-08

### UI Modernization

- **CustomTkinter Migration:** Fully migrated the UI to `CustomTkinter` for a modern, native-feeling aesthetic on macOS.
- **Dark Mode:** Implemented robust system-aware Dark/Light mode theme switching.
- **Refactoring:** Replaced all legacy `tkinter`/`ttk` widgets (`Button`, `Frame`, `Notebook`, `Toplevel`) with their `ctk` equivalents (`CTkButton`, `CTkFrame`, `CTkTabview`, `CTkToplevel`).
- **Confirmation Sheet:** Redesigned the "Network Detected" confirmation dialog as a modern, centered modal card.

### Fixed

- **Crash:** Resolved `AttributeError` on startup related to dialog initialization.
- **Tests:** Updated smoke tests to correctly mock `CustomTkinter` dependencies.

## [0.1.0-beta.17] - 2026-01-04

### Architecture

- **Refactor:** Restructured the codebase into modular components: `qr/` (parsing), `capture/` (scanning), `net/` (network mgmt), and `ui/` (GUI). This improves maintainability and separation of concerns.

### Added

- **Data Validation:** Implemented robust validation for scanned QR data (SSID presence, valid security types, password requirements).
- **CLI Command:** Added `list-cameras` command to easily identify available camera IDs.
- **CLI Helper:** Added "CLI Setup" button with **Auto-Install** feature (`~/.zshrc`).
- **Native Menu:** Added "Copy Alias" and "Install to .zshrc" directly to the macOS Help menu.

### Fixed

- **CLI Entry Point:** Resolved `ImportError` by correcting the entry point in `pyproject.toml`.
- **GUI Crash:** Fixed `NameError` and `ModuleNotFoundError` issues caused by missing imports during the refactor.

## [0.1.0-beta.16] - 2026-01-04

### UX Enhancements

- **Camera Selection:** Added a Browser-style Camera Dropdown to the main interface, allowing users to select input devices by name (e.g., "FaceTime HD Camera").
- **Scan Timeout:** Added a customizable Timeout setting (5-300s) directly in the GUI.

## [0.1.0-beta.15] - 2026-01-04

### Branding

- **Title Bar:** Removed the emoji from the window title for a cleaner, native look. The application icon is now handled exclusively by the OS window manager and Dock.

## [0.1.0-beta.14] - 2026-01-04

### Branding

- **GUI Refinement:** Removed the emoji from the window title and added the official application logo to the main Scanner tab for a more professional look.

## [0.1.0-beta.13] - 2026-01-04

### Documentation & Branding

- **Comprehensive Help:** Updated in-app and offline help to detailedly explain all CLI options and UI features.
- **Icon Branding:** Added the application icon to the About and Permission dialogs for consistent branding across the app.

## [0.1.0-beta.12] - 2026-01-04

### Documentation

- **Help Update:** Updated in-app, offline, and markdown help to reference the compiled `.app` command for CLI usage instead of `uv run`.

## [0.1.0-beta.11] - 2026-01-04

### Security

- **Confirm before Connect:** Added an option to review network details before connecting.
- **Add Only Mode:** Added an option to save the network profile without automatically connecting.
- **Redacted Logging:** Passwords and sensitive data are now redacted from application logs.
- **Documentation:** Added `docs/SECURITY.md` detailing credential storage and threat model.

### Added

- **Permission Assistant:** New helper window with deep links to macOS System Settings for Camera and Wi-Fi access.
- **Timeout UX:** Visual countdown timer (60s) and retry option for scanning.
- **Error Dialogs:** Added "Copy Debug Info" button to GUI error messages for easier reporting.
- **CLI Exit Codes:** Implemented structured exit codes for better scriptability.

### Fixed

- **GUI Crash:** Fixed an initialization order bug that caused a crash on startup.

## [0.1.0-beta.10] - 2026-01-04

### Added

- **Contributing Guide:** Added `CONTRIBUTING.md` with detailed setup, quality assurance steps, and best practices for developers.

## [0.1.0-beta.9] - 2026-01-04

### Added

- **Developer Tools:** Added `scripts/check.sh` for one-step local quality checks (format, lint, test).
- **Git Hooks:** Added `.pre-commit-config.yaml` to enforce linting and formatting before commits.
- **Markdown Linting:** Integrated `markdownlint` into pre-commit hooks to ensure documentation quality.

## [0.1.0-beta.8] - 2026-01-04

### Added

- **Code Quality:** Integrated `ruff` for automated linting and `pytest-cov` for code coverage reporting in the CI pipeline.
- **Documentation:** Added GitHub Actions build status badge to `README.md`.

## [0.1.0-beta.7] - 2026-01-04

### Fixed

- **CI/CD:** Resolved GitHub Actions hang by removing accidental `test_about.py` file which contained blocking UI code.
- **Testing:** Configured `pytest` to strictly search only the `tests/` directory to prevent accidental execution of utility scripts.

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
