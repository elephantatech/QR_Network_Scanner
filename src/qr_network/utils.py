import re
import logging


class RedactedLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # Regex to match "P:password;" pattern in Wi-Fi strings
        self.wifi_password_pattern = re.compile(r"(P:)([^;]+)(;)")

    def _redact(self, message: str) -> str:
        """Redacts sensitive information from the message."""
        if not isinstance(message, str):
            return message

        # Redact Wi-Fi password in QR string
        return self.wifi_password_pattern.sub(r"\1***\3", message)

    def info(self, msg, *args, **kwargs):
        self.logger.info(self._redact(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._redact(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._redact(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(self._redact(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(self._redact(msg), *args, **kwargs)
