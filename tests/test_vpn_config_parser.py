import pytest
import platform
from unittest.mock import patch
from src.vpn_config_parser import VPNConfigParser

def test_run_command_success():
    """Test successful command execution."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "test output\n"
        mock_run.return_value.returncode = 0
        
        result = VPNConfigParser.run_command(["echo", "test"])
        assert result == "test output"

def test_run_command_failure():
    """Test command execution failure."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Command failed")
        
        with pytest.raises(Exception):
            VPNConfigParser.run_command(["invalid_command"])

@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS specific test")
def test_macos_vpn_config_parsing():
    """Test VPN configuration parsing on macOS."""
    with patch.object(VPNConfigParser, 'run_command') as mock_run:
        mock_run.side_effect = [
            "(1) VPN (Service)\n(2) Wi-Fi (Built-in)",
            "Connected: VPN Service"
        ]
        
        config = VPNConfigParser.parse_macos_vpn_config()
        assert "VPN (Service)" in config["vpn_services"]
        assert config["active_vpn"] is not None

@pytest.mark.skipif(platform.system() != "Linux", reason="Linux specific test")
def test_linux_vpn_config_parsing():
    """Test VPN configuration parsing on Linux."""
    with patch.object(VPNConfigParser, 'run_command') as mock_run:
        mock_run.side_effect = [
            "tun0: tun\ntun1: tun",
            "default via 192.168.1.1 dev tun0"
        ]
        
        config = VPNConfigParser.parse_linux_vpn_config()
        assert len(config["vpn_interfaces"]) > 0
        assert config["active_vpn"] is not None

def test_detect_vpn_config():
    """Test VPN configuration detection across platforms."""
    config = VPNConfigParser.detect_vpn_config()
    assert "platform" in config
    assert "active_vpn" in config
    assert "vpn_type" in config