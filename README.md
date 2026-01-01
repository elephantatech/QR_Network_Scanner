# QR Network Scanner

A macOS desktop application and CLI tool to scan WiFi QR codes and automatically connect to the network.

## Features
- **Desktop GUI**: Simple window with scanning status.
- **CLI Mode**: Full-featured command-line interface with verbose logging.
- **Auto-Connect**: Automatically adds the network to macOS settings and attempts connection.
- **Modern UI**: Uses `rich` for CLI output and native camera feed.

## Prerequisites
- macOS
- Python 3.10+
- `uv` (recommended) or `pip`

## Installation

```bash
uv sync
```

## Usage

### GUI Mode
Launch the graphical interface:
```bash
uv run qr-network gui
```

### CLI Mode
Scan and connect via terminal:
```bash
uv run qr-network scan
```
Options:
- `--verbose, -v`: Show detailed logs.
- `--camera, -c`: Specify camera ID.
- `--timeout`: Set scan timeout.

## Build for Release
To generate a standalone macOS `.app`:
```bash
uv run python build_release.py
```
The application will be available in `dist/QRNetworkScanner.app`.

## Development
Run tests:
```bash
uv run pytest
```