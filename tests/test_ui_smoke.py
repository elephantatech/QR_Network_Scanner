import unittest
from unittest.mock import MagicMock, patch
import sys


class TestUISmoke(unittest.TestCase):
    def setUp(self):
        # Force re-import of ui.app to apply module mocks if not already mocked
        modules_to_patch = [
            "tkinter",
            "tkinter.ttk",
            "tkinter.messagebox",
            "webbrowser",
            "PIL",
            "PIL.Image",
            "PIL.ImageTk",
            "cv2",
        ]
        self.patchers = []
        for mod in modules_to_patch:
            patcher = patch.dict(sys.modules, {mod: MagicMock()})
            patcher.start()
            self.patchers.append(patcher)

        # Clear cached module to ensure we get the version using mocks
        if "qr_network.ui.app" in sys.modules:
            del sys.modules["qr_network.ui.app"]

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()

    def test_app_initialization(self):
        """Smoke test: Verify QRNetworkApp initializes without error."""
        # Now import safe to import
        from qr_network.ui.app import QRNetworkApp

        mock_root = MagicMock()

        # We need to mock the internal dependencies that __init__ might call
        # e.g. get_camera_names, RedactedLogger are imported from utils
        with (
            patch("qr_network.ui.app.get_camera_names", return_value=["Cam 1"]),
            patch("qr_network.ui.app.RedactedLogger"),
            patch("qr_network.ui.app.NetworkManager"),
            patch("qr_network.ui.app.QRCodeScanner"),
        ):
            app = QRNetworkApp(mock_root, debug=True)

            self.assertIsNotNone(app)
            # Check basic attributes
            self.assertTrue(app.debug)
            # Verify title was set on root
            mock_root.title.assert_called_with("QR Network Scanner")
