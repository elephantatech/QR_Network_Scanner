import cv2
import time
import sys
from typing import Optional


class QRCodeScanner:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None

    def start_camera(self):
        """Initializes the camera capture."""
        if sys.platform == "darwin":
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_AVFOUNDATION)
        else:
            self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            raise RuntimeError(
                "Could not open camera. Please check if the application has permission to access the camera (System Settings -> Privacy & Security -> Camera)."
            )

    def stop_camera(self):
        """Releases the camera."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def get_frame(self):
        """Reads a frame from the camera."""
        if not self.cap:
            self.start_camera()
        ret, frame = self.cap.read()
        return ret, frame

    def detect_qr(self, frame) -> Optional[str]:
        """Detects QR code in a frame using zxing-cpp."""
        try:
            import zxingcpp

            results = zxingcpp.read_barcodes(frame)
            for result in results:
                if result.text:
                    return result.text, None
            return None, None
        except Exception as e:
            print(f"ZXing error: {e}")
            return None, None

    def scan_one(
        self, timeout: float = 30.0, show_window: bool = True
    ) -> Optional[str]:
        """
        Scans for a single QR code.
        """
        if not self.cap:
            self.start_camera()

        start_time = time.time()

        try:
            while (time.time() - start_time) < timeout:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                decoded_text, points = self.detect_qr(frame)

                if decoded_text:
                    if show_window:
                        if points is not None:
                            points = points.astype(int)
                            for i in range(len(points)):
                                pt1 = tuple(points[i][0])
                                pt2 = tuple(points[(i + 1) % len(points)][0])
                                cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

                        cv2.imshow("QR Scanner", frame)
                        cv2.waitKey(500)
                    return decoded_text

                if show_window:
                    cv2.imshow("QR Scanner", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        return None
        finally:
            if show_window:
                cv2.destroyAllWindows()
            self.stop_camera()

        return None

    def scan_screen(self, screen_index: Optional[int] = None) -> Optional[str]:
        """
        Captures screen content and detects QR code.
        """
        try:
            from PIL import ImageGrab
            import numpy as np

            try:
                screenshot = ImageGrab.grab(all_screens=True)
            except Exception:
                screenshot = ImageGrab.grab()

            img_np = np.array(screenshot)
            frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            decoded_text, _ = self.detect_qr(frame)
            return decoded_text

        except Exception as e:
            print(f"Screen scan error: {e}")
            return None

    def scan_file(self, file_path: str) -> Optional[str]:
        """
        Scans a file (Image or PDF) for a QR code.
        """
        import os
        import numpy as np

        if not os.path.exists(file_path):
            return None

        ext = os.path.splitext(file_path)[1].lower()

        try:
            # Handle PDF
            if ext == ".pdf":
                import fitz  # PyMuPDF

                doc = fitz.open(file_path)
                if doc.page_count < 1:
                    return None

                # Scan first 3 pages max to find a QR
                for i in range(min(3, doc.page_count)):
                    page = doc.load_page(i)
                    pix = page.get_pixmap(dpi=300)  # High DPI for better detection

                    # Convert to numpy array (RGB)
                    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                        pix.h, pix.w, pix.n
                    )

                    # Convert RGB/RGBA to BGR for OpenCV
                    if pix.n == 4:  # RGBA
                        frame = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
                    elif pix.n == 3:  # RGB
                        frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                    else:
                        continue  # Gray etc, might need specific handling or skip

                    decoded_text, _ = self.detect_qr(frame)
                    if decoded_text:
                        return decoded_text
                return None

            # Handle Images
            else:
                # Use cv2.imread handling mostly standard formats
                # For more robust format support (like HEIC on mac if supported by cv2 build, or others),
                # we might fallback to PIL, but cv2 is usually fine for png/jpg.
                frame = cv2.imread(file_path)
                if frame is None:
                    return None

                decoded_text, _ = self.detect_qr(frame)
                return decoded_text

        except Exception as e:
            print(f"File scan error: {e}")
            return None
