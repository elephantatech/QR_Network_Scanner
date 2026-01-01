
import pytest
from unittest.mock import MagicMock, patch
from qr_network.network import NetworkManager
import platform

# Mock platform.system to return "Darwin" for these tests
@patch("platform.system", return_value="Darwin")
def test_network_manager_init(mock_platform):
    nm = NetworkManager()
    assert nm.interface == "en0"

@patch("platform.system", return_value="Windows")
def test_network_manager_init_non_mac(mock_platform):
    with pytest.raises(RuntimeError):
        NetworkManager()

@patch("subprocess.run")
@patch("platform.system", return_value="Darwin")
def test_add_network(mock_sys, mock_run):
    nm = NetworkManager()
    
    # Mock success
    mock_run.return_value = MagicMock(returncode=0, stdout="Success")
    
    success, output = nm.add_network("MySSID", "pass")
    
    assert success is True
    # Verify command
    cmd = mock_run.call_args[0][0]
    assert cmd == [
        'networksetup', '-addpreferredwirelessnetworkatindex', 
        'en0', 'MySSID', '0', 'WPA2', 'pass'
    ]

@patch("subprocess.run")
@patch("platform.system", return_value="Darwin")
def test_connect_network(mock_sys, mock_run):
    nm = NetworkManager()
    mock_run.return_value = MagicMock(returncode=0, stdout="Success")
    
    success, output = nm.connect_network("MySSID", "pass")
    assert success is True
    cmd = mock_run.call_args[0][0]
    assert cmd == ['networksetup', '-setairportnetwork', 'en0', 'MySSID', 'pass']
