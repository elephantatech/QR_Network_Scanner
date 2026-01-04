import unittest
from unittest.mock import patch, MagicMock
import sys
import numpy as np
from qr_network.capture.scanner import QRCodeScanner

# Mock zxingcpp before tests run
sys.modules["zxingcpp"] = MagicMock()


class TestQRCodeScanner(unittest.TestCase):
    def setUp(self):
        # Reset zxingcpp mock
        sys.modules["zxingcpp"].read_barcodes.reset_mock()

    @patch("cv2.VideoCapture")
    def test_init_camera_success(self, mock_cap_cls):
        """Test camera initialization success."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap_cls.return_value = mock_cap

        scanner = QRCodeScanner(camera_id=0)
        scanner.start_camera()

        self.assertIsNotNone(scanner.cap)
        mock_cap_cls.assert_called()

    @patch("cv2.VideoCapture")
    def test_init_camera_failure(self, mock_cap_cls):
        """Test exception when camera fails to open."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_cls.return_value = mock_cap

        scanner = QRCodeScanner(camera_id=0)

        with self.assertRaises(RuntimeError) as cm:
            scanner.start_camera()

        self.assertIn("Could not open camera", str(cm.exception))

    @patch("cv2.VideoCapture")
    def test_process_frame_qr_found(self, mock_cap_cls):
        """Test QR detection logic."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap_cls.return_value = mock_cap

        scanner = QRCodeScanner()

        # Create a dummy frame (black image)
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

        # Mock zxingcpp return value
        mock_result = MagicMock()
        mock_result.text = "WIFI:S:TestNet;T:WPA;P:pass;;"
        sys.modules["zxingcpp"].read_barcodes.return_value = [mock_result]

        text, points = scanner.detect_qr(dummy_frame)

        self.assertEqual(text, "WIFI:S:TestNet;T:WPA;P:pass;;")
        sys.modules["zxingcpp"].read_barcodes.assert_called_once_with(dummy_frame)

    @patch("cv2.VideoCapture")
    def test_process_frame_no_qr(self, mock_cap_cls):
        """Test detection when no QR is present."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap_cls.return_value = mock_cap

        scanner = QRCodeScanner()
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

        # Mock empty result
        sys.modules["zxingcpp"].read_barcodes.return_value = []

        text, points = scanner.detect_qr(dummy_frame)

        self.assertIsNone(text)

    def test_stop_camera(self):
        """Test resource release."""
        scanner = QRCodeScanner()
        mock_cap = MagicMock()
        scanner.cap = mock_cap

        scanner.stop_camera()

        mock_cap.release.assert_called_once()
        self.assertIsNone(scanner.cap)
