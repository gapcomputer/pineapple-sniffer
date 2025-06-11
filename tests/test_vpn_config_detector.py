import pytest
import logging
from src.vpn_config_detector import VPNConfigDetector, VPNConfigurationError

def test_vpn_config_detector_initialization():
    """Test VPN configuration detector initialization."""
    detector = VPNConfigDetector()
    assert detector is not None
    assert detector.logger is not None

def test_detect_vpn_connections_empty():
    """Test VPN connection detection with no connections."""
    detector = VPNConfigDetector(log_level=logging.DEBUG)
    connections = detector.detect_vpn_connections()
    assert isinstance(connections, list)

def test_validate_vpn_configuration():
    """Test VPN configuration validation."""
    detector = VPNConfigDetector()
    
    # Test valid configuration
    valid_config = {
        'protocol': 'OpenVPN',
        'interface': 'tun0'
    }
    assert detector.validate_vpn_configuration(valid_config) is True
    
    # Test invalid configuration
    invalid_config = {
        'protocol': 'UnknownProtocol'
    }
    assert detector.validate_vpn_configuration(invalid_config) is False
    assert detector.validate_vpn_configuration({}) is False