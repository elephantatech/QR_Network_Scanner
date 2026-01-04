import logging
import unittest
from unittest.mock import patch, MagicMock
from qr_network.utils import RedactedLogger, get_camera_names


class TestRedactedLogger(unittest.TestCase):
    def setUp(self):
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.redacted_logger = RedactedLogger(self.mock_logger)

    def test_redact_password(self):
        """Test that Wi-Fi passwords are redacted."""
        original_msg = "WIFI:S:MyNetwork;T:WPA;P:SecretPassword123;;"
        self.redacted_logger.info(original_msg)

        # Check that the logger was called with the redacted message
        self.mock_logger.info.assert_called_once()
        args, _ = self.mock_logger.info.call_args
        redacted_msg = args[0]

        self.assertIn("P:***;", redacted_msg)
        self.assertNotIn("SecretPassword123", redacted_msg)

    def test_no_redaction_needed(self):
        """Test that messages without passwords remain unchanged."""
        original_msg = "WIFI:S:PublicNetwork;T:nopass;;"
        self.redacted_logger.info(original_msg)

        self.mock_logger.info.assert_called_once_with(original_msg)

    def test_non_string_message(self):
        """Test that non-string messages are handled gracefully."""
        self.redacted_logger.info(123)
        self.mock_logger.info.assert_called_once_with(123)


class TestGetCameraNames(unittest.TestCase):
    @patch("subprocess.run")
    def test_get_camera_names_success(self, mock_run):
        """Test parsing of system_profiler output."""
        # Mock output mimicking "system_profiler SPCameraDataType"
        mock_output = """
Camera:

    FaceTime HD Camera:

      Model ID: UVC Camera VendorID_1452 ProductID_34065
      Unique ID: 0x8020000005ac8511

    Logitech Brio:

      Model ID: UVC Camera VendorID_1133 ProductID_2125
      Unique ID: 0x14400000046d084d
"""
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        cameras = get_camera_names()

        self.assertEqual(len(cameras), 2)
        self.assertEqual(cameras[0], "FaceTime HD Camera")
        self.assertEqual(cameras[1], "Logitech Brio")

    @patch("subprocess.run")
    def test_get_camera_names_error(self, mock_run):
        """Test fallback when subprocess fails."""
        mock_run.side_effect = Exception("Command failed")

        cameras = get_camera_names()

        # Should return default fallback
        self.assertEqual(cameras, ["Camera 0", "Camera 1"])

    @patch("subprocess.run")
    def test_get_camera_names_no_cameras(self, mock_run):
        """Test fallback when no cameras found."""
        mock_output = "Camera:\n"
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        cameras = get_camera_names()

        # Should return default fallback list
        self.assertEqual(cameras, ["Camera 0"])
