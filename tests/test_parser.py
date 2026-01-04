import pytest
from qr_network.network import WiFiQRParser


def test_parser_valid_wpa():
    qr = "WIFI:S:MyNetwork;T:WPA;P:password123;;"
    data = WiFiQRParser.parse(qr)
    assert data["ssid"] == "MyNetwork"
    assert data["type"] == "WPA"
    assert data["password"] == "password123"


def test_parser_valid_nopass():
    qr = "WIFI:S:OpenNet;T:nopass;;"
    data = WiFiQRParser.parse(qr)
    assert data["ssid"] == "OpenNet"
    assert data["type"] == "nopass"
    assert data["password"] == ""


def test_parser_hidden():
    qr = "WIFI:S:HiddenNet;T:WPA;P:pass;H:true;;"
    data = WiFiQRParser.parse(qr)
    assert data["hidden"] is True


def test_parser_invalid_format():
    with pytest.raises(ValueError):
        WiFiQRParser.parse("INVALID:S:MyNet;")


def test_parser_missing_ssid():
    with pytest.raises(ValueError):
        WiFiQRParser.parse("WIFI:T:WPA;P:pass;;")
