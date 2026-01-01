
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
        """
        if not qr_string.startswith("WIFI:"):
            raise ValueError("Invalid WiFi QR code format")

        data = {}
        # Simple regex based parsing
        # Matches key:value; where value can be anything except ; (basic impl)
        # Note: Escape characters exist in standard but basic impl for now.
        
        # SSID
        ssid_match = re.search(r"S:([^;]+);", qr_string)
        if ssid_match:
            data['ssid'] = ssid_match.group(1)
        
        # Type (WPA, WEP, nopass)
        type_match = re.search(r"T:([^;]+);", qr_string)
        data['type'] = type_match.group(1) if type_match else 'nopass'
        
        # Password
        pass_match = re.search(r"P:([^;]+);", qr_string)
        data['password'] = pass_match.group(1) if pass_match else ''
        
        # Hidden
        hidden_match = re.search(r"H:([^;]+);", qr_string)
        data['hidden'] = hidden_match.group(1).lower() == 'true' if hidden_match else False

        if 'ssid' not in data:
            raise ValueError("No SSID found in QR code")
            
        return data

class NetworkManager:
    def __init__(self, interface: str = "en0"):
        self.interface = interface
        if platform.system() != "Darwin":
            raise RuntimeError("This application only supports macOS")

    def _run_command(self, cmd: list) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def get_current_network(self) -> Optional[str]:
        """Returns the SSID of the currently connected network."""
        # /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I
        # But allow using networksetup
        success, output = self._run_command(['networksetup', '-getairportnetwork', self.interface])
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
        
        ns_security = "WPA2" # Default
        if security_type.upper() == "WEP":
            ns_security = "WEP"
        elif security_type.upper() == "NOPASS":
            ns_security = "OPEN"
        
        cmd = [
            'networksetup', '-addpreferredwirelessnetworkatindex',
            self.interface, ssid, '0', ns_security
        ]
        if password:
            cmd.append(password)
        
        return self._run_command(cmd)

    def connect_network(self, ssid: str, password: str):
        """
        Attempts to connect to the network.
        Uses -setairportnetwork
        """
        cmd = ['networksetup', '-setairportnetwork', self.interface, ssid]
        if password:
            cmd.append(password)
            
        return self._run_command(cmd)
