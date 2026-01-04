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
        # Try to use AVFoundation backend explicitly on macOS for better compatibility
        if sys.platform == "darwin":
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_AVFOUNDATION)
        else:
            self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            # Fallback to default if specific backend failed
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
        """Detects QR code in a frame using zxing-cpp (highly robust)."""
        try:
            import zxingcpp
            # zxing-cpp can read directly from numpy array (OpenCV image)
            # It expects the image in a rigorous format, but typically handles BGR/grayscale updates.
            # We might need to ensure it's grayscale or pass format.

            # Try simple detection first with zxing
            results = zxingcpp.read_barcodes(frame)
            for result in results:
                if result.text:
                    # zxing-cpp returns position object, but for now we essentially just need text
                    # We can return None for points if we don't strictly need to draw the box right now
                    # or adapter logic.
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
        Returns the decoded string if found, None if timeout reached.
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
                        # Draw box for visual feedback before closing
                        if points is not None:
                            points = points.astype(int)
                            for i in range(len(points)):
                                pt1 = tuple(points[i][0])
                                pt2 = tuple(points[(i + 1) % len(points)][0])
                                cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

                        cv2.imshow("QR Scanner", frame)
                        cv2.waitKey(500)  # Show success briefly
                    return decoded_text

                if show_window:
                    cv2.imshow("QR Scanner", frame)
                    # Press 'q' to quit early
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
        If screen_index is None, captures all screens (combined).
        """
        try:
            from PIL import ImageGrab
            import numpy as np

            # Capture screen
            # all_screens=True is a specialized argument depending on backend.
            # On macOS, ImageGrab.grab() usually captures the main screen or a combined one.
            # We will try to grab all if possible, or just default grab.
            try:
                # Attempt to capture all screens if supported by PIL version/OS
                screenshot = ImageGrab.grab(all_screens=True)
            except Exception:
                screenshot = ImageGrab.grab()

            # Convert to OpenCV format (BGR)
            # PIL is RGB, OpenCV is BGR
            img_np = np.array(screenshot)
            frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            # Detect
            decoded_text, _ = self.detect_qr(frame)
            return decoded_text

        except Exception as e:
            print(f"Screen scan error: {e}")
            return None
