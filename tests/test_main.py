import unittest
from unittest.mock import patch
import sys
from qr_network.main import entry_point


class TestMain(unittest.TestCase):
    @patch("qr_network.cli.app")
    def test_entry_point_cli(self, mock_cli_app):
        """Test that arguments trigger CLI."""
        with patch.object(sys, "argv", ["qr-network", "list-cameras"]):
            entry_point()
            mock_cli_app.assert_called_once()

    @patch("qr_network.ui.app.main")
    def test_entry_point_gui(self, mock_gui_main):
        """Test that no arguments trigger GUI."""
        with patch.object(sys, "argv", ["qr-network"]):
            entry_point()
            mock_gui_main.assert_called_once()
