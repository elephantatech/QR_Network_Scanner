import subprocess
import re
from typing import Optional, Tuple
import platform


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
        success, output = self._run_command(
            ["networksetup", "-getairportnetwork", self.interface]
        )
        if success:
            match = re.search(r"Current Wi-Fi Network: (.+)", output)
            if match:
                return match.group(1).strip()
        return None

    def add_network(
        self,
        ssid: str,
        password: str,
        security_type: str = "WPA2",
        hidden: bool = False,
    ):
        """
        Adds the network to the preferred list.

        Note: The 'hidden' parameter is currently unused because 'networksetup'
        on macOS does not require a specific flag for hidden networks when
        adding them to the preferred list. The OS handles probing automatically.
        """
        ns_security = "WPA2"  # Default
        if security_type.upper() == "WEP":
            ns_security = "WEP"
        elif security_type.upper() == "NOPASS":
            ns_security = "OPEN"
        elif security_type.upper() == "OPEN":  # Handle both NOPASS and OPEN
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
        """
        cmd = ["networksetup", "-setairportnetwork", self.interface, ssid]
        if password:
            cmd.append(password)

        return self._run_command(cmd)
