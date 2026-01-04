import pytest
from unittest.mock import MagicMock, patch
from qr_network.network import NetworkManager
import subprocess


# --- Fixtures ---
@pytest.fixture
def nm():
    with patch("platform.system", return_value="Darwin"):
        return NetworkManager()


# --- Mocked Network Join Tests ---


@patch("subprocess.run")
def test_mock_add_fail(mock_run, nm):
    """
    Test when adding network profile fails.
    Scenario: 'networksetup -addpreferred...' returns non-zero or error.
    """
    # Simulate failure
    mock_run.side_effect = subprocess.CalledProcessError(
        1, cmd="networksetup", stderr="Error adding profile"
    )

    success, output = nm.add_network("MySSID", "pass")

    assert success is False
    assert "Error adding profile" in output


@patch("subprocess.run")
def test_mock_add_success_connect_fail(mock_run, nm):
    """
    Test when profile addition succeeds but connection activation fails.
    'Profile added' vs 'Connect failed' path.
    """
    # We need to simulate two calls:
    # 1. add_network -> Success
    # 2. connect -> Fail (simulated later if we tested the full flow, but we test unit methods here)

    # 1. Test add_network success
    mock_run.return_value = MagicMock(returncode=0, stdout="Added successfully")
    success_add, _ = nm.add_network("MySSID", "pass")
    assert success_add is True

    # 2. Test activate_network failure
    mock_run.side_effect = subprocess.CalledProcessError(
        1, cmd="networksetup", stderr="Failed to join network"
    )
    success_connect, output_connect = nm.activate_network("MySSID", "pass")

    assert success_connect is False
    assert "Failed to join network" in output_connect


@patch("subprocess.run")
def test_mock_permission_denied(mock_run, nm):
    """
    Test specific 'permission denied' error message handling.
    """
    error_msg = "Error: You are not authorized to perform this operation."
    mock_run.side_effect = subprocess.CalledProcessError(
        1, cmd="networksetup", stderr=error_msg
    )

    success, output = nm.activate_network("SecureNet", "pass")

    assert success is False
    assert "authorized" in output or "permission" in output.lower()
    # Ideally, we'd check if the GUI interprets this correctly,
    # but at the NetworkManager unit level, we ensure the error propagates correctly.


@patch("subprocess.run")
def test_mock_connect_success(mock_run, nm):
    """
    Happy path: Connect succeeds.
    """
    mock_run.return_value = MagicMock(returncode=0, stdout="")
    success, _ = nm.activate_network("MySSID", "pass")
    assert success is True


@patch("subprocess.run")
def test_add_network_security_mappings(mock_run, nm):
    """
    Verify that QR security types are correctly mapped to networksetup arguments.
    """
    mock_run.return_value = MagicMock(returncode=0, stdout="Added")

    # Test WEP
    nm.add_network("WEPNet", "pass", security_type="WEP")
    args_wep = mock_run.call_args[0][0]
    assert args_wep[5] == "WEP"

    # Test nopass -> OPEN
    nm.add_network("OpenNet", "", security_type="nopass")
    args_open = mock_run.call_args[0][0]
    assert args_open[5] == "OPEN"

    # Test WPA -> WPA2 (Default mapping in code)
    nm.add_network("WPANet", "pass", security_type="WPA")
    args_wpa = mock_run.call_args[0][0]
    assert args_wpa[5] == "WPA2"
