import subprocess
import re
from typing import Dict, Optional, Tuple
import platform


class WiFiQRParser:
    @staticmethod
    def parse(qr_string: str) -> Dict[str, str]:
        """
        Parses a WIFI QR code string.
        Format: WIFI:S:MySSID;T:WPA;P:MyPassword;;
        Supports escaping (\;, \,, \\) and case-insensitive keys.
        """
        if not qr_string.upper().startswith("WIFI:"):
            raise ValueError("Invalid WiFi QR code format")

        # Remove prefix
        content = qr_string[5:]
        data = {}

        # Regex to match Key:Value; where Value handles escaping
        # Keys are single characters (S, T, P, H) usually, but we match ^[A-Z]:
        # Values consume until an unescaped ;
        # We search iteratively

        # Pattern explanation:
        # ([A-Za-z]+):       Capture Key (case insensitive)
        # ((?:[^;\\]|\\.)*)  Capture Value: anything not ; or \, OR an escaped char
        # ;                  End with semicolon
        pattern = re.compile(r"([A-Za-z]+):((?:[^;\\]|\\.)*);")

        for match in pattern.finditer(content):
            key = match.group(1).upper()
            raw_value = match.group(2)

            # Unescape special characters
            # The spec says: special characters backslash, semicolon, comma and colon should be escaped
            # simple unescape: replace \(char) with char
            value = re.sub(r"\\(.)", r"\1", raw_value)

            if key == "S":
                data["ssid"] = value
            elif key == "T":
                data["type"] = value
            elif key == "P":
                data["password"] = value
            elif key == "H":
                data["hidden"] = value.lower() == "true"

        if "ssid" not in data:
            raise ValueError("No SSID found in QR code")

        return data


class NetworkManager:
    def __init__(self, interface: str = "en0"):
        self.interface = interface
        if platform.system() != "Darwin":
            raise RuntimeError("This application only supports macOS")

    def _run_command(self, cmd: list) -> Tuple[bool, str]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def get_current_network(self) -> Optional[str]:
        """Returns the SSID of the currently connected network."""
        # /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I
        # But allow using networksetup
        success, output = self._run_command(
            ["networksetup", "-getairportnetwork", self.interface]
        )
        if success:
            # "Current Wi-Fi Network: MySSID"
            match = re.search(r"Current Wi-Fi Network: (.+)", output)
            if match:
                return match.group(1).strip()
        return None

    def add_network(self, ssid: str, password: str, security_type: str = "WPA2"):
        """
        Adds the network to the preferred list.
        """
        # networksetup -addpreferredwirelessnetworkatindex hardwareport network index securitytype password
        # index 0 to put it at the top

        # Mapping QR type to networksetup security type
        # QR: WPA -> networksetup: WPA2 (usually)
        # QR: WEP -> WEP
        # QR: nopass -> OPEN

        ns_security = "WPA2"  # Default
        if security_type.upper() == "WEP":
            ns_security = "WEP"
        elif security_type.upper() == "NOPASS":
            ns_security = "OPEN"

        cmd = [
            "networksetup",
            "-addpreferredwirelessnetworkatindex",
            self.interface,
            ssid,
            "0",
            ns_security,
        ]
        if password:
            cmd.append(password)

        return self._run_command(cmd)

    def activate_network(self, ssid: str, password: str):
        """
        Attempts to connect to (activate) the network.
        Uses -setairportnetwork which joins and saves credentials if successful.
        """
        cmd = ["networksetup", "-setairportnetwork", self.interface, ssid]
        if password:
            cmd.append(password)

        return self._run_command(cmd)
