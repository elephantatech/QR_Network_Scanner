# GUI Test Strategy: QR Network Scanner

Testing graphical user interfaces (GUIs), especially those built with `tkinter`, presents unique challenges. This document outlines our strategy to ensure the reliability of the UI layer without relying on fragile, pixel-based automation tools.

## 1. The Challenge

* **Mainloop Blocking**: `tkinter` runs in an infinite loop (`root.mainloop()`), which blocks standard test execution.
* **Hardware Dependencies**: The app relies on a physical camera and network adapters, which aren't available in CI/CD environments.
* **Visual Verification**: Verifying that a specific pixel is "red" is brittle and doesn't prove functionality.

## 2. Selected Approach: Event Handler Testing (Headless)

We will use a **"White Box"** testing approach. Instead of simulating mouse clicks, we directly instantiate the application class and invoke the methods bound to user actions.

### Key Principles

1. **Mock Externalities**: The `QRCodeScanner` (Camera) and `NetworkManager` (WiFi) must be mocked.
2. **Headless Root**: We create a `tk.Tk` root window but keep it hidden/virtual so tests can run on headless CI servers (requires `xvfb` on Linux, but works natively on macOS/Windows in many cases).
3. **Direct Invocation**: We call the internal methods `start_scan()`, `process_result()`, etc., and assert that the mocks were called with the expected arguments.

## 3. Implementation Plan

### Phase 1: Test Infrastructure Setup

We need a `pytest` fixture that manages the Tkinter lifecycle to prevent "can't invoke command" errors or dangling windows.

**Example `tests/conftest.py` (Proposed):**

```python
import pytest
import tkinter as tk

@pytest.fixture(scope="session")
def tk_root():
    """Create a hidden root window for the duration of the test session."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    yield root
    root.destroy()
```

### Phase 2: Logic Verification

We will create `tests/test_ui_logic.py` to cover key workflows:

* **Workflow A: Successful Scan & Connect**
  * **Setup**: Mock Scanner to return "WIFI:S:TestNet;..."`. Mock NetworkManager to succeed.
  * **Action**: Call `app.start_scan()`.
  * **Assertion**: Verify `scanner.scan_one` was called. Verify `network_manager.add_network` was called with "TestNet". Verify UI status label updated to "Connected".

* **Workflow B: Scan Timeout**
  * **Setup**: Mock Scanner to return `None`.
  * **Action**: Call `app.start_scan()`.
  * **Assertion**: Verify Error MessageBox (mocked) or Status Label shows "Timeout".

* **Workflow C: Invalid QR Code**
  * **Setup**: Mock Scanner to return "InvalidString".
  * **Action**: Call `app.start_scan()`.
  * **Assertion**: Verify Error Handling logic is triggered.

## 4. Code Example

Here is how a test case looks in practice:

```python
from unittest.mock import MagicMock, patch
from qr_network.ui.app import QRNetworkApp

def test_scan_success(tk_root):
    # 1. Mock Dependencies
    mock_scanner = MagicMock()
    mock_scanner.scan_one.return_value = "WIFI:S:MyNet;T:WPA;P:pass;;"

    mock_manager = MagicMock()
    mock_manager.connect.return_value = True

    # 2. Instantiate App with Mocks
    # (Requires slight refactor to allow injecting mocks, or using patch)
    with patch('qr_network.ui.app.QRCodeScanner', return_value=mock_scanner), \
         patch('qr_network.ui.app.NetworkManager', return_value=mock_manager):

        app = QRNetworkApp(tk_root)

        # 3. Trigger Action
        app.start_scan_thread() # Or the specific method bound to the button

        # 4. Assertions
        mock_scanner.scan_one.assert_called()
        mock_manager.add_network.assert_called_with("MyNet", "pass", ...)
```

## 5. Future Roadmap: MVP Refactoring

To make testing even easier, we should eventually move towards a **Model-View-Presenter (MVP)** architecture.

* **View (`app.py`)**: Only handles layout and forwards events to Presenter.
* **Presenter (`presenter.py`)**: Contains ALL logic (if scan clicked -> call scanner -> if result -> call network).
* **Model**: The Scanner and NetworkManager.

**Benefit**: The `Presenter` can be tested with standard unit tests without ANY Tkinter code involved.

```text
