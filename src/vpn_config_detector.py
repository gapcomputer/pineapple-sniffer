import logging
import subprocess
import platform
from typing import Dict, Optional, List, Any

class VPNConfigurationError(Exception):
    """Custom exception for VPN configuration detection errors."""
    pass

class VPNConfigDetector:
    """
    A comprehensive VPN configuration detection and analysis class.
    
    Handles error detection, logging, and retrieval of VPN connection details.
    """
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize VPN configuration detector with logging.
        
        Args:
            log_level (int): Logging level, defaults to INFO
        """
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_vpn_connections(self) -> List[Dict[str, Any]]:
        """
        Detect active VPN connections across different interfaces.
        
        Returns:
            List of dictionaries containing VPN connection details
        
        Raises:
            VPNConfigurationError: If detection fails
        """
        try:
            # Detect OS and use appropriate method
            os_name = platform.system().lower()
            
            if os_name == 'darwin':  # macOS
                return self._detect_vpn_macos()
            elif os_name == 'linux':
                return self._detect_vpn_linux()
            else:
                self.logger.warning(f"Unsupported OS: {os_name}")
                return []
        
        except Exception as e:
            self.logger.error(f"Unexpected error during VPN detection: {e}")
            raise VPNConfigurationError(f"Unexpected VPN detection error: {e}")
    
    def _detect_vpn_macos(self) -> List[Dict[str, Any]]:
        """
        Detect VPN connections on macOS.
        
        Returns:
            List of VPN connection details
        """
        try:
            result = subprocess.run(
                ['scutil', '--nc', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Basic parsing of scutil output
            vpn_connections = []
            for line in result.stdout.split('\n'):
                if 'VPN' in line or 'Connected' in line:
                    vpn_connections.append({
                        'interface': 'utun',
                        'status': 'active',
                        'protocol': 'Unknown'
                    })
            
            if not vpn_connections:
                self.logger.info("No VPN connections detected on macOS")
            
            return vpn_connections
        
        except subprocess.TimeoutExpired:
            self.logger.error("macOS VPN detection timed out")
            return []
        except Exception as e:
            self.logger.error(f"macOS VPN detection error: {e}")
            return []
    
    def _detect_vpn_linux(self) -> List[Dict[str, Any]]:
        """
        Detect VPN connections on Linux.
        
        Returns:
            List of VPN connection details
        """
        try:
            # Check for typical VPN interface names
            vpn_interfaces = ['tun', 'tap', 'ppp']
            vpn_connections = []
            
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                for interface in vpn_interfaces:
                    if interface in line.lower():
                        vpn_connections.append({
                            'interface': line.split(':')[1].strip(),
                            'status': 'active',
                            'protocol': 'OpenVPN' if 'tun' in interface else 'Unknown'
                        })
            
            if not vpn_connections:
                self.logger.info("No VPN connections detected on Linux")
            
            return vpn_connections
        
        except subprocess.TimeoutExpired:
            self.logger.error("Linux VPN detection timed out")
            return []
        except Exception as e:
            self.logger.error(f"Linux VPN detection error: {e}")
            return []
    
    def validate_vpn_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate VPN configuration for potential security issues.
        
        Args:
            config (Dict[str, Any]): VPN configuration to validate
        
        Returns:
            bool: Whether configuration passes basic security checks
        """
        try:
            if not config:
                self.logger.warning("Empty VPN configuration")
                return False
            
            # Add specific validation checks
            if config.get('protocol') not in ['OpenVPN', 'WireGuard', 'IPSec', 'Unknown']:
                self.logger.warning(f"Unsupported VPN protocol: {config.get('protocol')}")
                return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False

# Configure default logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)