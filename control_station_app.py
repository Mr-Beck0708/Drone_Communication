#!/usr/bin/env python3
"""
Control Station Application - Laptop Side

Receives encrypted WiFi network scan data from drone (Raspberry Pi)
and displays it in real-time with post-quantum secure communication.
"""

import socket
import json
import argparse
import sys
import signal
from threading import Thread, Lock
from typing import Optional, Dict, List
from datetime import datetime
import os

from src.crypto import HybridKeyExchange, DilithiumSignature
from src.communication import Session, SecureChannel
from src.utils import Config, setup_logger


class ControlStationApplication:
    """Control station - receives and displays network scan data from drone."""
    
    def __init__(self, config: Config):
        self.config = config
        self.operator_id = config.get("operator_id", "OP-001")
        self.logger = setup_logger(f"control_station_{self.operator_id}")
        
        # Cryptographic components
        self.kex = HybridKeyExchange()
        self.sig = DilithiumSignature()
        self.session: Optional[Session] = None
        self.channel: Optional[SecureChannel] = None
        
        # Network components
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.connected = False
        
        # Data storage
        self.latest_scan: Optional[Dict] = None
        self.scan_history: List[Dict] = []
        self.data_lock = Lock()
        
        # Display control
        self.running = False
        
    def initialize_crypto(self):
        """Initialize cryptographic keys."""
        self.logger.info("Initializing cryptographic keys...")
        self.x448_pk, self.kyber_pk = self.kex.generate_keypair()
        self.sign_pk = self.sig.generate_keypair()
        self.logger.info("Cryptographic keys generated", operator_id=self.operator_id)
    
    def connect_to_drone(self, host: str, port: int):
        """Connect to drone server."""
        self.logger.info("Connecting to drone", host=host, port=port)
        
        try:
            print(f"\n📡 Connecting to Drone at {host}:{port}...")
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)
            self.client_socket.connect((host, port))
            self.connected = True
            
            print(f"✓ Connected to drone\n")
            self.logger.info("Connected to drone")
            
        except Exception as e:
            self.logger.error("Failed to connect to drone", error=str(e))
            raise
    
    def perform_key_exchange(self):
        """Perform hybrid key exchange with drone."""
        self.logger.info("Starting key exchange...")
        
        try:
            # Receive drone's public keys
            drone_data = self._receive_json()
            drone_x448_pk = bytes.fromhex(drone_data["x448_pk"])
            drone_kyber_pk = bytes.fromhex(drone_data["kyber_pk"])
            drone_sign_pk = bytes.fromhex(drone_data["sign_pk"])
            
            # Initiate key exchange
            kyber_ct, shared_secret = self.kex.initiate_exchange(drone_x448_pk, drone_kyber_pk)
            
            # Send our keys and ciphertext to drone
            cs_data = {
                "x448_pk": self.x448_pk.hex(),
                "kyber_ct": kyber_ct.hex(),
                "sign_pk": self.sign_pk.hex()
            }
            self._send_json(cs_data)
            
            # Setup secure channel and session
            self.session = Session(f"{self.operator_id}_session")
            self.session.complete_handshake(shared_secret, "drone")
            self.channel = SecureChannel(shared_secret, self.sig)
            
            # Store drone's signing key
            self.drone_sign_pk = drone_sign_pk
            
            print("✓ Secure connection established with post-quantum cryptography\n")
            self.logger.info("Key exchange completed successfully")
            
        except Exception as e:
            self.logger.error("Key exchange failed", error=str(e))
            raise
    
    def send_command(self, command_type: str, **kwargs):
        """Send command to drone."""
        try:
            cmd_data = {
                "type": command_type,
                **kwargs
            }
            self._send_json(cmd_data)
            self.logger.info("Command sent", command=command_type)
            
        except Exception as e:
            self.logger.error("Failed to send command", error=str(e))
    
    def receive_data_loop(self):
        """Main loop to receive data from drone."""
        self.running = True
        self.logger.info("Starting data receive loop...")
        
        print("=" * 80)
        print("Receiving WiFi scan data from drone...")
        print("=" * 80 + "\n")
        
        try:
            while self.running and self.connected:
                try:
                    self.client_socket.settimeout(1.0)
                    data = self._receive_json()
                    self._handle_drone_message(data)
                    
                except socket.timeout:
                    continue
                    
        except Exception as e:
            if self.running:
                self.logger.error("Data receive error", error=str(e))
                print(f"\nError receiving data: {e}")
    
    def _handle_drone_message(self, data: dict):
        """Handle message from drone."""
        msg_type = data.get("type")
        
        if msg_type == "scan_data":
            self._handle_scan_data(data)
        elif msg_type == "ack":
            message = data.get("message", "")
            print(f"✓ Drone: {message}")
        else:
            self.logger.warning("Unknown message type", type=msg_type)
    
    def _handle_scan_data(self, data: dict):
        """Handle scan data from drone."""
        try:
            # Decrypt and verify
            payload = data["payload"]
            
            # Reconstruct message for SecureChannel
            encrypted_msg = {
                "nonce": bytes.fromhex(payload["nonce"]),
                "ciphertext": bytes.fromhex(payload["ciphertext"]),
                "counter": payload["counter"]
            }
            if "signature" in payload:
                encrypted_msg["signature"] = bytes.fromhex(payload["signature"])
            
            decrypted_data = self.channel.receive(encrypted_msg, self.drone_sign_pk)
            
            # Parse scan result
            scan_result = json.loads(decrypted_data.decode('utf-8'))
            
            # Store data
            with self.data_lock:
                self.latest_scan = scan_result
                self.scan_history.append(scan_result)
                
                # Keep only last 100 scans
                if len(self.scan_history) > 100:
                    self.scan_history.pop(0)
            
            # Display results
            self._display_scan_results(scan_result)
            
            # Optionally save to file
            if self.config.get("telemetry.log_to_file", False):
                self._save_to_file(scan_result)
            
        except Exception as e:
            self.logger.error("Failed to process scan data", error=str(e))
    
    def _display_scan_results(self, scan_result: dict):
        """Display scan results in formatted table."""
        timestamp = scan_result.get("timestamp", "")
        networks = scan_result.get("networks", [])
        total = scan_result.get("total_networks", 0)
        duration = scan_result.get("scan_duration", 0)
        error = scan_result.get("error")
        
        # Clear previous output (simple approach)
        print("\n" + "=" * 80)
        print(f"📡 WiFi Scan Results - {timestamp}")
        print(f"Networks Found: {total} | Scan Duration: {duration}s")
        
        if error:
            print(f"⚠️  Error: {error}")
            print("=" * 80)
            return
        
        if not networks:
            print("No networks detected")
            print("=" * 80)
            return
        
        print("=" * 80)
        
        # Table header
        print(f"{'SSID':<30} {'Signal':<10} {'Security':<15} {'Channel':<10}")
        print("-" * 80)
        
        # Sort by signal strength (strongest first)
        sorted_networks = sorted(networks, key=lambda n: n.get("signal_strength", -100), reverse=True)
        
        # Display each network
        for net in sorted_networks[:20]:  # Show top 20
            ssid = net.get("ssid", "Hidden")[:29]
            signal = net.get("signal_strength", -100)
            encryption = net.get("encryption", "Unknown")[:14]
            channel = net.get("channel", "?")
            
            # Signal strength bar
            signal_bar = self._signal_bar(signal)
            
            # Color code encryption (using symbols)
            if encryption == "Open":
                sec_icon = "🔓"
            elif "WPA3" in encryption:
                sec_icon = "🔒"
            elif "WPA2" in encryption:
                sec_icon = "🔐"
            else:
                sec_icon = "🔑"
            
            print(f"{ssid:<30} {signal_bar:<10} {sec_icon} {encryption:<13} {channel:<10}")
        
        if total > 20:
            print(f"\n... and {total - 20} more networks")
        
        print("=" * 80)
    
    def _signal_bar(self, signal_dbm: int) -> str:
        """Convert signal strength to visual bar."""
        if signal_dbm >= -50:
            return "████ " + str(signal_dbm)
        elif signal_dbm >= -60:
            return "███  " + str(signal_dbm)
        elif signal_dbm >= -70:
            return "██   " + str(signal_dbm)
        elif signal_dbm >= -80:
            return "█    " + str(signal_dbm)
        else:
            return "▌    " + str(signal_dbm)
    
    def _save_to_file(self, scan_result: dict):
        """Save scan results to JSON file."""
        try:
            log_file = self.config.get("telemetry.log_file", "network_scans.json")
            
            # Append to file
            with open(log_file, 'a') as f:
                json.dump(scan_result, f)
                f.write('\n')
                
        except Exception as e:
            self.logger.error("Failed to save to file", error=str(e))
    
    def _send_json(self, data: dict):
        """Send JSON data over socket."""
        if not self.client_socket:
            raise RuntimeError("Not connected")
        
        json_str = json.dumps(data)
        message = json_str.encode('utf-8')
        length = len(message)
        
        # Send length prefix (4 bytes) then message
        self.client_socket.sendall(length.to_bytes(4, 'big') + message)
    
    def _receive_json(self) -> dict:
        """Receive JSON data from socket."""
        if not self.client_socket:
            raise RuntimeError("Not connected")
        
        # Receive length prefix
        length_bytes = self._recv_exact(4)
        length = int.from_bytes(length_bytes, 'big')
        
        # Receive message
        message = self._recv_exact(length)
        json_str = message.decode('utf-8')
        
        return json.loads(json_str)
    
    def _recv_exact(self, n: int) -> bytes:
        """Receive exactly n bytes from socket."""
        data = b''
        while len(data) < n:
            chunk = self.client_socket.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data
    
    def shutdown(self):
        """Graceful shutdown."""
        self.logger.info("Shutting down control station...")
        
        self.running = False
        self.connected = False
        
        # Send shutdown command to drone
        try:
            if self.client_socket:
                self.send_command("SHUTDOWN")
        except:
            pass
        
        # Close socket
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        print("\n" + "=" * 80)
        print("Control station shutdown complete")
        print("=" * 80)
        
        self.logger.info("Control station shutdown complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Control Station Application")
    parser.add_argument("--host", type=str,
                       help="Drone IP address to connect to")
    parser.add_argument("--port", type=int, help="Drone port")
    parser.add_argument("--config", type=str, default="config/control_station_config.json",
                       help="Configuration file path")
    parser.add_argument("--operator-id", type=str, help="Operator identifier")
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = Config(args.config)
    except Exception:
        print(f"Warning: Could not load config file {args.config}, using defaults")
        config = Config()
    
    # Override with CLI arguments
    if args.host:
        config.set("network.drone_host", args.host)
    if args.port:
        config.set("network.port", args.port)
    if args.operator_id:
        config.set("operator_id", args.operator_id)
    
    # Get server parameters
    host = config.get("network.drone_host")
    port = config.get("network.port", 8443)
    
    if not host:
        print("Error: Drone host not specified!")
        print("Use --host <DRONE_IP> or set in config file")
        print(f"\nExample: python3 {sys.argv[0]} --host 192.168.29.123")
        sys.exit(1)
    
    # Create and run control station
    control_station = ControlStationApplication(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\n\nShutdown signal received...")
        control_station.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("\n" + "=" * 80)
        print("CONTROL STATION - WiFi Network Intelligence (CLIENT MODE)")
        print("=" * 80)
        print(f"Operator ID: {control_station.operator_id}")
        print(f"Connecting to Drone: {host}:{port}")
        print(f"Post-Quantum Cryptography: ENABLED")
        print(f"  - Hybrid Key Exchange: X448 + Kyber768")
        print(f"  - Signatures: Dilithium3")
        print(f"  - Encryption: ChaCha20-Poly1305")
        print("=" * 80)
        
        control_station.initialize_crypto()
        control_station.connect_to_drone(host, port)
        control_station.perform_key_exchange()
        
        # Send start scan command
        control_station.send_command("START_SCAN")
        
        # Receive and display data
        control_station.receive_data_loop()
        
    except KeyboardInterrupt:
        print("\n\nShutdown requested...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        control_station.shutdown()


if __name__ == "__main__":
    main()
