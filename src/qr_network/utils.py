import re
import logging


class RedactedLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # Regex to match "P:password;" pattern in Wi-Fi strings
        self.wifi_password_pattern = re.compile(r"(P:)([^;]+)(;)")

    def redact(self, message: str) -> str:
        """Redacts sensitive information from the message."""
        if not isinstance(message, str):
            return message

        # Redact Wi-Fi password in QR string
        return self.wifi_password_pattern.sub(r"\1***\3", message)

    def info(self, msg, *args, **kwargs):
        self.logger.info(self.redact(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self.redact(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self.redact(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(self.redact(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(self.redact(msg), *args, **kwargs)


def get_camera_names() -> list[str]:
    """
    Returns a list of connected camera names on macOS using system_profiler.
    Indices correspond to OpenCV camera indices (usually).
    """
    try:
        import subprocess

        # Run system_profiler
        result = subprocess.run(
            ["system_profiler", "SPCameraDataType"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout

        cameras = []
        lines = output.split("\n")

        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue

            # Header "Camera:" or "SPCameraDataType:"
            if line_strip.lower() == "camera:" or "date:" in line_strip:
                continue

            # If line ends with colon and isn't a property
            if (
                line.endswith(":")
                and not line_strip.startswith("Model ID")
                and not line_strip.startswith("Unique ID")
            ):
                # Check indentation (approx 4 spaces)
                if line.startswith("    ") and not line.startswith("      "):
                    cameras.append(line_strip[:-1])  # Remove colon

        if not cameras:
            return ["Camera 0"]

        return cameras

    except Exception as e:
        print(f"Error listing cameras: {e}")
        return ["Camera 0", "Camera 1"]
