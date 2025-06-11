import subprocess
import re
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VPNConfigParser:
    """
    A utility class for parsing VPN configuration details from system commands.
    
    Supports multiple platforms and VPN types with modular parsing strategies.
    """
    
    @staticmethod
    def run_command(command: List[str]) -> str:
        """
        Execute a system command and return its output.
        
        Args:
            command (List[str]): Command to execute as a list of strings
        
        Returns:
            str: Command output
        
        Raises:
            subprocess.CalledProcessError: If command execution fails
        """
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Command execution failed: {e}")
            raise

    @classmethod
    def parse_macos_vpn_config(cls) -> Dict[str, Optional[str]]:
        """
        Parse VPN configuration on macOS using system commands.
        
        Returns:
            Dict[str, Optional[str]]: VPN configuration details
        """
        try:
            # Retrieve network service configurations
            network_services_output = cls.run_command(
                ["networksetup", "-listnetworkserviceorder"]
            )
            
            # Search for VPN-related services
            vpn_services = re.findall(
                r'\(\d+\)\s+(.*\(VPN\))', 
                network_services_output
            )
            
            # Detailed configuration parsing
            config = {
                "vpn_services": vpn_services,
                "active_vpn": None,
                "vpn_type": None
            }
            
            # Check active VPN connections
            try:
                scutil_output = cls.run_command(
                    ["scutil", "--nc", "status"]
                )
                active_vpns = [
                    line.split(":")[0].strip() 
                    for line in scutil_output.split("\n") 
                    if "Connected" in line
                ]
                config["active_vpn"] = active_vpns[0] if active_vpns else None
            except Exception as e:
                logger.warning(f"Could not retrieve active VPN: {e}")
            
            return config
        
        except Exception as e:
            logger.error(f"macOS VPN config parsing failed: {e}")
            return {"vpn_services": [], "active_vpn": None, "vpn_type": None}

    @classmethod
    def parse_linux_vpn_config(cls) -> Dict[str, Optional[str]]:
        """
        Parse VPN configuration on Linux systems.
        
        Returns:
            Dict[str, Optional[str]]: VPN configuration details
        """
        try:
            # Retrieve network interfaces
            ip_output = cls.run_command(["ip", "tuntap", "show"])
            
            # Look for VPN-related interfaces
            vpn_interfaces = re.findall(r'(tun\d+)', ip_output)
            
            config = {
                "vpn_interfaces": vpn_interfaces,
                "active_vpn": None,
                "vpn_type": None
            }
            
            # Check for active connections via routing table
            try:
                route_output = cls.run_command(["ip", "route", "show", "table", "all"])
                vpn_routes = [
                    line for line in route_output.split("\n") 
                    if "tun" in line
                ]
                config["active_vpn"] = vpn_routes[0] if vpn_routes else None
            except Exception as e:
                logger.warning(f"Could not retrieve active VPN routes: {e}")
            
            return config
        
        except Exception as e:
            logger.error(f"Linux VPN config parsing failed: {e}")
            return {"vpn_interfaces": [], "active_vpn": None, "vpn_type": None}

    @classmethod
    def detect_vpn_config(cls) -> Dict[str, Optional[str]]:
        """
        Detect VPN configuration based on the current platform.
        
        Returns:
            Dict[str, Optional[str]]: Parsed VPN configuration
        """
        import platform
        
        os_name = platform.system().lower()
        
        if os_name == "darwin":
            return cls.parse_macos_vpn_config()
        elif os_name == "linux":
            return cls.parse_linux_vpn_config()
        else:
            logger.warning(f"Unsupported platform: {os_name}")
            return {"platform": os_name, "active_vpn": None, "vpn_type": None}