import pytest
from qr_network.qr.parser import WiFiQRParser


@pytest.mark.parametrize(
    "qr_string,expected",
    [
        # Basic
        (
            "WIFI:S:MyNetwork;T:WPA;P:password123;;",
            {
                "ssid": "MyNetwork",
                "type": "WPA",
                "password": "password123",
                "hidden": False,
            },
        ),
        (
            "WIFI:S:OpenNet;T:nopass;;",
            {"ssid": "OpenNet", "type": "nopass", "password": "", "hidden": False},
        ),
        # Order independence
        (
            "WIFI:T:WPA;P:pass;S:MyNet;;",
            {"ssid": "MyNet", "type": "WPA", "password": "pass", "hidden": False},
        ),
        # Escaping
        (
            r"WIFI:S:My\;Net;T:WPA;P:Pa\\ss;;",
            {"ssid": r"My;Net", "type": "WPA", "password": r"Pa\ss", "hidden": False},
        ),
        (
            r"WIFI:S:My\,Net;T:WPA;P:Pa\:ss;;",
            {"ssid": "My,Net", "type": "WPA", "password": "Pa:ss", "hidden": False},
        ),
        # Lowercase keys (s:, t:, p:)
        (
            "wifi:s:lowernam;t:wpa;p:lowerpass;;",
            {
                "ssid": "lowernam",
                "type": "wpa",
                "password": "lowerpass",
                "hidden": False,
            },
        ),
        # Mixed case keys
        (
            "WIFI:S:Mixed;t:WPA;p:Pass;;",
            {"ssid": "Mixed", "type": "WPA", "password": "Pass", "hidden": False},
        ),
        # Unicode / Spaces
        (
            "WIFI:S:🦄 Uni Net;T:WPA;P:  spaces  ;;",
            {
                "ssid": "🦄 Uni Net",
                "type": "WPA",
                "password": "  spaces  ",
                "hidden": False,
            },
        ),
        (
            "WIFI:S: LeadingSpace;T:nopass;;",
            {
                "ssid": " LeadingSpace",
                "type": "nopass",
                "password": "",
                "hidden": False,
            },
        ),
        # Hex SSIDs (some generators use this, probably out of scope for strict QR spec but good to test normal handling)
        # Actually strictly the spec allows hex but our parser expects string. Let's stick to string extraction mostly.
        # Missing Type (defaults to nopass?) Or just empty string?
        # Standard says: If T is omitted, assume nopass.
        (
            "WIFI:S:DefaultType;;",
            {"ssid": "DefaultType", "type": "nopass", "password": "", "hidden": False},
        ),
        # Hidden
        (
            "WIFI:S:Hid;T:WPA;P:p;H:true;;",
            {"ssid": "Hid", "type": "WPA", "password": "p", "hidden": True},
        ),
        (
            "WIFI:S:Vis;T:WPA;P:p;H:false;;",
            {"ssid": "Vis", "type": "WPA", "password": "p", "hidden": False},
        ),
    ],
)
def test_parser_valid_cases(qr_string, expected):
    data = WiFiQRParser.parse(qr_string)
    # Normalize for comparison (default None/False handled in parser or here)
    assert data["ssid"] == expected["ssid"]
    assert data.get("type", "nopass") == expected["type"]
    assert data.get("password", "") == expected["password"]
    assert data.get("hidden", False) == expected["hidden"]


def test_parser_invalid_format():
    with pytest.raises(ValueError, match="Invalid WiFi QR code format"):
        WiFiQRParser.parse("INVALID:S:MyNet;")


def test_parser_missing_ssid():
    with pytest.raises(ValueError, match="No SSID found"):
        WiFiQRParser.parse("WIFI:T:WPA;P:pass;;")


def test_parser_empty_ssid():
    with pytest.raises(ValueError, match="SSID cannot be empty"):
        WiFiQRParser.parse("WIFI:S:   ;T:nopass;;")


def test_parser_invalid_type():
    with pytest.raises(ValueError, match="Unsupported security type"):
        WiFiQRParser.parse("WIFI:S:MyNet;T:INVALID_TYPE;;")


def test_parser_missing_password_wpa():
    with pytest.raises(ValueError, match="Password is required"):
        WiFiQRParser.parse("WIFI:S:MyNet;T:WPA;;")


def test_parser_empty_password_wpa():
    with pytest.raises(ValueError, match="Password is required"):
        WiFiQRParser.parse("WIFI:S:MyNet;T:WPA;P:;;")
