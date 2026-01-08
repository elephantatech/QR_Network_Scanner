import unittest
from unittest.mock import patch
from typer.testing import CliRunner
from qr_network.cli import app, ExitCode

runner = CliRunner()


class TestCLI(unittest.TestCase):
    @patch("qr_network.utils.get_camera_names")
    def test_list_cameras_success(self, mock_get_names):
        """Test listing cameras when cameras are found."""
        mock_get_names.return_value = ["FaceTime HD", "External Cam"]

        result = runner.invoke(app, ["list-cameras"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Available Cameras", result.stdout)
        self.assertIn("FaceTime HD", result.stdout)
        self.assertIn("External Cam", result.stdout)

    @patch("qr_network.utils.get_camera_names")
    def test_list_cameras_empty(self, mock_get_names):
        """Test listing cameras when none are found."""
        mock_get_names.return_value = []

        result = runner.invoke(app, ["list-cameras"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("No cameras detected", result.stdout)

    @patch("qr_network.cli.QRCodeScanner")
    @patch("qr_network.cli.NetworkManager")
    def test_scan_success(self, MockNetManager, MockScanner):
        """Test successful scan and connect flow."""
        # Setup mocks
        mock_scanner = MockScanner.return_value
        mock_scanner.scan_one.return_value = "WIFI:S:MyNet;T:WPA;P:secret;;"

        mock_net = MockNetManager.return_value
        mock_net.add_network.return_value = (True, "Added")
        mock_net.get_current_network.return_value = "OtherNet"
        mock_net.activate_network.return_value = (True, "Connected")

        result = runner.invoke(app, ["scan", "--timeout", "1"])

        self.assertEqual(result.exit_code, ExitCode.SUCCESS)
        self.assertIn("Found Network: MyNet", result.stdout)
        self.assertIn("Successfully connected to MyNet", result.stdout)

        # Verify calls
        mock_scanner.scan_one.assert_called_once()
        mock_net.add_network.assert_called_with("MyNet", "secret", "WPA", hidden=False)
        mock_net.activate_network.assert_called_with("MyNet", "secret")

    @patch("qr_network.cli.QRCodeScanner")
    @patch("qr_network.cli.NetworkManager")
    def test_scan_timeout(self, MockNetManager, MockScanner):
        """Test scan timeout."""
        mock_scanner = MockScanner.return_value
        # Simulate timeout (returns None)
        mock_scanner.scan_one.return_value = None

        result = runner.invoke(app, ["scan", "--timeout", "1"])

        # Usually timeout without catching exit code raises an exception or exits with code
        # In our CLI we raise typer.Exit(code=ExitCode.SCAN_TIMEOUT)
        self.assertEqual(result.exit_code, ExitCode.SCAN_TIMEOUT)
        self.assertIn("Scan timed out", result.stdout)

    @patch("qr_network.ui.app.main")
    def test_gui_launch(self, mock_gui_main):
        """Test GUI command launches app."""
        result = runner.invoke(app, ["gui"])

        self.assertEqual(result.exit_code, 0)
        mock_gui_main.assert_called_once_with(debug=False)

    @patch("qr_network.ui.app.main")
    def test_gui_launch_debug(self, mock_gui_main):
        """Test GUI command with debug flag."""
        result = runner.invoke(app, ["gui", "--debug"])

        self.assertEqual(result.exit_code, 0)
        mock_gui_main.assert_called_once_with(debug=True)
