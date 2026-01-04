"""
WiFi Network Scanner Utility

Scans for nearby WiFi networks and collects network information.
Supports multiple scanning backends (nmcli, iwlist).
"""

import subprocess
import json
import re
import time
from typing import List, Dict, Optional
from datetime import datetime


class WiFiScanner:
    """WiFi network scanner that collects information about nearby networks."""
    
    def __init__(self, scan_tool: str = "auto"):
        """
        Initialize WiFi scanner.
        
        Args:
            scan_tool: Scanning tool to use ("nmcli", "iwlist", or "auto" for auto-detect)
        """
        self.scan_tool = scan_tool
        if scan_tool == "auto":
            self.scan_tool = self._detect_scan_tool()
        
    def _detect_scan_tool(self) -> str:
        """Auto-detect available scanning tool."""
        # Try nmcli first (more modern)
        try:
            subprocess.run(["nmcli", "--version"], 
                          capture_output=True, check=True, timeout=2)
            return "nmcli"
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try iwlist as fallback
        try:
            subprocess.run(["iwlist", "--version"], 
                          capture_output=True, check=True, timeout=2)
            return "iwlist"
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # No tool available
        raise RuntimeError("No WiFi scanning tool found. Install NetworkManager (nmcli) or wireless-tools (iwlist)")
    
    def scan(self, max_networks: int = 50, include_hidden: bool = False) -> Dict:
        """
        Scan for WiFi networks.
        
        Args:
            max_networks: Maximum number of networks to return
            include_hidden: Include hidden networks (SSID not broadcast)
        
        Returns:
            Dictionary containing scan results with metadata
        """
        start_time = time.time()
        
        try:
            if self.scan_tool == "nmcli":
                networks = self._scan_nmcli()
            elif self.scan_tool == "iwlist":
                networks = self._scan_iwlist()
            else:
                raise ValueError(f"Unsupported scan tool: {self.scan_tool}")
            
            # Filter hidden networks if requested
            if not include_hidden:
                networks = [n for n in networks if n.get("ssid", "").strip()]
            
            # Limit number of networks
            networks = networks[:max_networks]
            
            scan_duration = time.time() - start_time
            
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "scan_tool": self.scan_tool,
                "networks": networks,
                "total_networks": len(networks),
                "scan_duration": round(scan_duration, 2)
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "scan_tool": self.scan_tool,
                "networks": [],
                "total_networks": 0,
                "scan_duration": round(time.time() - start_time, 2),
                "error": str(e)
            }
    
    def _scan_nmcli(self) -> List[Dict]:
        """Scan using nmcli (NetworkManager)."""
        # Rescan for fresh data
        try:
            subprocess.run(["nmcli", "device", "wifi", "rescan"], 
                          capture_output=True, timeout=10)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass  # Continue even if rescan fails
        
        # Get network list
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,BSSID,CHAN,FREQ", "device", "wifi", "list"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"nmcli failed: {result.stderr}")
        
        networks = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split(':')
            if len(parts) < 6:
                continue
            
            ssid, signal, security, bssid, channel, freq = parts[:6]
            
            # Parse frequency
            freq_ghz = ""
            if freq:
                try:
                    freq_mhz = int(freq)
                    freq_ghz = f"{freq_mhz / 1000:.2f} GHz"
                except ValueError:
                    freq_ghz = freq
            
            # Calculate signal strength in dBm (nmcli gives percentage)
            try:
                signal_pct = int(signal)
                # Rough conversion: 100% ≈ -30 dBm, 0% ≈ -90 dBm
                signal_dbm = int(-90 + (signal_pct * 0.6))
            except ValueError:
                signal_dbm = -100
            
            networks.append({
                "ssid": ssid,
                "signal_strength": signal_dbm,
                "signal_quality": signal,  # percentage
                "encryption": self._parse_security(security),
                "bssid": bssid,
                "channel": int(channel) if channel.isdigit() else None,
                "frequency": freq_ghz
            })
        
        return networks
    
    def _scan_iwlist(self) -> List[Dict]:
        """Scan using iwlist (wireless-tools)."""
        # Find wireless interface
        interface = self._find_wireless_interface()
        if not interface:
            raise RuntimeError("No wireless interface found")
        
        # Run scan
        result = subprocess.run(
            ["sudo", "iwlist", interface, "scan"],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"iwlist failed: {result.stderr}")
        
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            # New cell (network)
            if line.startswith("Cell "):
                if current_network:
                    networks.append(current_network)
                match = re.search(r'Address: ([\w:]+)', line)
                current_network = {
                    "bssid": match.group(1) if match else "",
                    "ssid": "",
                    "signal_strength": -100,
                    "encryption": "Unknown",
                    "channel": None,
                    "frequency": ""
                }
            
            # SSID
            elif "ESSID:" in line:
                match = re.search(r'ESSID:"([^"]*)"', line)
                if match:
                    current_network["ssid"] = match.group(1)
            
            # Frequency and channel
            elif "Frequency:" in line:
                match = re.search(r'Frequency:([\d.]+) GHz.*Channel (\d+)', line)
                if match:
                    current_network["frequency"] = f"{match.group(1)} GHz"
                    current_network["channel"] = int(match.group(2))
            
            # Signal level
            elif "Signal level=" in line:
                match = re.search(r'Signal level=([-\d]+) dBm', line)
                if match:
                    current_network["signal_strength"] = int(match.group(1))
            
            # Encryption
            elif "Encryption key:" in line:
                if "off" in line.lower():
                    current_network["encryption"] = "Open"
                else:
                    current_network["encryption"] = "Encrypted"
            
            # WPA/WPA2/WPA3
            elif "IEEE 802.11i/WPA2" in line or "WPA2" in line:
                current_network["encryption"] = "WPA2"
            elif "WPA3" in line:
                current_network["encryption"] = "WPA3"
            elif "WPA Version 1" in line:
                current_network["encryption"] = "WPA"
        
        # Add last network
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def _find_wireless_interface(self) -> Optional[str]:
        """Find first wireless interface."""
        try:
            result = subprocess.run(
                ["iw", "dev"],
                capture_output=True, text=True, timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if "Interface" in line:
                    return line.split()[-1]
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback: common interface names
        for iface in ["wlan0", "wlp2s0", "wlp3s0", "wlo1"]:
            try:
                result = subprocess.run(
                    ["ip", "link", "show", iface],
                    capture_output=True, timeout=2
                )
                if result.returncode == 0:
                    return iface
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
        
        return None
    
    def _parse_security(self, security: str) -> str:
        """Parse security type from nmcli output."""
        if not security or security == "--":
            return "Open"
        
        security = security.upper()
        
        if "WPA3" in security:
            return "WPA3"
        elif "WPA2" in security:
            return "WPA2"
        elif "WPA" in security:
            return "WPA"
        elif "WEP" in security:
            return "WEP"
        else:
            return "Encrypted"


# Example usage
if __name__ == "__main__":
    scanner = WiFiScanner()
    print(f"Using scanner: {scanner.scan_tool}")
    
    scan_result = scanner.scan(max_networks=10)
    print(json.dumps(scan_result, indent=2))
