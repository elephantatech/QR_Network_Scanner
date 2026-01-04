import re
from typing import Dict


class WiFiQRParser:
    @staticmethod
    def parse(qr_string: str) -> Dict[str, str]:
        """
        Parses a WIFI QR code string.
        Format: WIFI:S:MySSID;T:WPA;P:MyPassword;;
        Supports escaping (\\;, \\,, \\\\) and case-insensitive keys.
        """
        if not qr_string.upper().startswith("WIFI:"):
            raise ValueError("Invalid WiFi QR code format")

        # Remove prefix
        content = qr_string[5:]
        data = {}

        # Regex to match Key:Value; where Value handles escaping
        pattern = re.compile(r"([A-Za-z]+):((?:[^;\\]|\\.)*);")

        for match in pattern.finditer(content):
            key = match.group(1).upper()
            raw_value = match.group(2)

            # Unescape special characters
            value = re.sub(r"\\(.)", r"\1", raw_value)

            if key == "S":
                data["ssid"] = value
            elif key == "T":
                data["type"] = value
            elif key == "P":
                data["password"] = value
            elif key == "H":
                data["hidden"] = value.lower() == "true"

        # --- Validation ---

        # 1. SSID Validation
        if "ssid" not in data:
            raise ValueError("No SSID found in QR code")

        if not data["ssid"].strip():
            raise ValueError("SSID cannot be empty or whitespace only")

        # 2. Security Type Validation
        # Default to nopass if not specified
        sec_type = data.get("type", "nopass").upper()
        valid_types = {"WPA", "WEP", "NOPASS", "OPEN"}

        if sec_type not in valid_types:
            raise ValueError(f"Unsupported security type: {data['type']}")

        # 3. Password Validation
        # If WPA or WEP, password is generally required.
        if sec_type in {"WPA", "WEP"}:
            password = data.get("password", "")
            if not password:
                raise ValueError(f"Password is required for security type {sec_type}")

        return data
