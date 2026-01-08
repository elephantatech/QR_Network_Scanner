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

    @patch("PIL.ImageGrab.grab")
    def test_scan_screen_success(self, mock_grab):
        """Test scanning from screen successfully."""
        setup_mock_zxing()  # Ensure zxing mock is ready

        scanner = QRCodeScanner()

        # Mock ImageGrab returning an image
        mock_image = MagicMock()
        # Create a tiny numpy array to represent the image
        mock_image_np = np.zeros((100, 100, 3), dtype=np.uint8)
        # When __array__ is called, return the numpy array
        mock_image.__array__ = MagicMock(return_value=mock_image_np)

        mock_grab.return_value = mock_image

        # Mock detection result
        mock_result = MagicMock()
        mock_result.text = "WIFI:S:ScreenNet;T:WPA;P:pass;;"
        sys.modules["zxingcpp"].read_barcodes.return_value = [mock_result]

        result = scanner.scan_screen()

        self.assertEqual(result, "WIFI:S:ScreenNet;T:WPA;P:pass;;")
        mock_grab.assert_called()

    @patch("os.path.exists")
    @patch("cv2.imread")
    def test_scan_file_image_success(self, mock_imread, mock_exists):
        """Test scanning a local image file successfully."""
        setup_mock_zxing()
        mock_exists.return_value = True

        scanner = QRCodeScanner()

        # Mock cv2.imread returning a valid frame
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_frame

        # Mock detection result
        mock_result = MagicMock()
        mock_result.text = "WIFI:S:FileNet;T:WPA;P:pass;;"
        sys.modules["zxingcpp"].read_barcodes.return_value = [mock_result]

        result = scanner.scan_file("test.png")

        self.assertEqual(result, "WIFI:S:FileNet;T:WPA;P:pass;;")
        mock_imread.assert_called_with("test.png")

    @patch("os.path.exists")
    @patch("fitz.open")
    def test_scan_file_pdf_success(self, mock_fitz_open, mock_exists):
        """Test scanning a PDF file successfully."""
        setup_mock_zxing()
        mock_exists.return_value = True

        scanner = QRCodeScanner()

        # Mock PDF document structure
        mock_doc = MagicMock()
        mock_doc.page_count = 1
        mock_page = MagicMock()
        mock_doc.load_page.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        # Mock pixmap
        mock_pix = MagicMock()
        mock_pix.h = 100
        mock_pix.w = 100
        mock_pix.n = 3  # RGB
        # Create bytes for 100x100 RGB image
        mock_pix.samples = bytes(100 * 100 * 3)
        mock_page.get_pixmap.return_value = mock_pix

        # Mock detection result
        mock_result = MagicMock()
        mock_result.text = "WIFI:S:PDFNet;T:WPA;P:pass;;"
        sys.modules["zxingcpp"].read_barcodes.return_value = [mock_result]

        result = scanner.scan_file("test.pdf")

        self.assertEqual(result, "WIFI:S:PDFNet;T:WPA;P:pass;;")
        mock_fitz_open.assert_called_with("test.pdf")

    @patch("os.path.exists")
    def test_scan_file_not_found(self, mock_exists):
        """Test scanning a non-existent file."""
        mock_exists.return_value = False
        scanner = QRCodeScanner()
        result = scanner.scan_file("nonexistent.png")
        self.assertIsNone(result)


def setup_mock_zxing():
    """Helper to ensure zxingcpp mock is set up if not already."""
    if "zxingcpp" not in sys.modules or not isinstance(
        sys.modules["zxingcpp"], MagicMock
    ):
        sys.modules["zxingcpp"] = MagicMock()
    sys.modules["zxingcpp"].read_barcodes.reset_mock()
