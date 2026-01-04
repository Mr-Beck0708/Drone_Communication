#!/usr/bin/env python3
"""
Drone Application - Raspberry Pi Side

WiFi network scanner that collects intelligence and transmits
encrypted data to control station using post-quantum cryptography.
"""

import socket
import json
import time
import argparse
import sys
import signal
from threading import Thread, Event
from typing import Optional

from src.crypto import HybridKeyExchange, DilithiumSignature
from src.communication import Session, SecureChannel
from src.utils import Config, setup_logger
from src.utils.wifi_scanner import WiFiScanner


class DroneApplication:
    """Drone brain - scans WiFi networks and sends data to control station."""
    
    def __init__(self, config: Config):
        self.config = config
        self.drone_id = config.get("drone_id", "DRONE-RASPI-01")
        self.logger = setup_logger(f"drone_{self.drone_id}")
        
        # Cryptographic components
        self.kex = HybridKeyExchange()
        self.sig = DilithiumSignature()
        self.session: Optional[Session] = None
        self.channel: Optional[SecureChannel] = None
        
        # Network components
        self.socket: Optional[socket.socket] = None
        self.connected = False
        
        # WiFi scanner
        scan_tool = config.get("wifi_scanner.scan_tool", "auto")
        self.scanner = WiFiScanner(scan_tool=scan_tool)
        self.logger.info(f"WiFi scanner initialized", tool=self.scanner.scan_tool)
        
        # Scanning control
        self.scanning = Event()
        self.scan_interval = config.get("wifi_scanner.scan_interval", 5.0)
        self.scan_thread: Optional[Thread] = None
        self.shutdown_event = Event()
        
    def initialize_crypto(self):
        """Initialize cryptographic keys."""
        self.logger.info("Initializing cryptographic keys...")
        self.x448_pk, self.kyber_pk = self.kex.generate_keypair()
        self.sign_pk = self.sig.generate_keypair()
        self.logger.info("Cryptographic keys generated", drone_id=self.drone_id)
        
    def connect_to_control_station(self, host: str, port: int):
        """Connect to control station server."""
        self.logger.info("Connecting to control station", host=host, port=port)
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))
            self.connected = True
            self.logger.info("Connected to control station")
            
        except Exception as e:
            self.logger.error("Failed to connect", error=str(e))
            raise
    
    def perform_key_exchange(self):
        """Perform hybrid key exchange with control station."""
        self.logger.info("Starting key exchange...")
        
        try:
            # Send our public keys to control station
            key_data = {
                "x448_pk": self.x448_pk.hex(),
                "kyber_pk": self.kyber_pk.hex(),
                "sign_pk": self.sign_pk.hex()
            }
            self._send_json(key_data)
            
            # Receive control station's keys and ciphertext
            cs_data = self._receive_json()
            cs_x448_pk = bytes.fromhex(cs_data["x448_pk"])
            kyber_ct = bytes.fromhex(cs_data["kyber_ct"])
            cs_sign_pk = bytes.fromhex(cs_data["sign_pk"])
            
            # Complete key exchange
            shared_secret = self.kex.complete_exchange(cs_x448_pk, kyber_ct)
            
            # Setup secure channel and session
            self.session = Session(f"{self.drone_id}_session")
            self.session.complete_handshake(shared_secret, "control_station")
            self.channel = SecureChannel(shared_secret, self.sig)
            
            # Store control station's signing key
            self.cs_sign_pk = cs_sign_pk
            
            self.logger.info("Key exchange completed successfully")
            
        except Exception as e:
            self.logger.error("Key exchange failed", error=str(e))
            raise
    
    def start_scanning(self):
        """Start WiFi scanning thread."""
        if self.scan_thread and self.scan_thread.is_alive():
            self.logger.warning("Scan thread already running")
            return
        
        self.scanning.set()
        self.scan_thread = Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        self.logger.info("WiFi scanning started", interval=self.scan_interval)
    
    def stop_scanning(self):
        """Stop WiFi scanning thread."""
        self.scanning.clear()
        self.logger.info("WiFi scanning stopped")
    
    def _scan_loop(self):
        """Main scanning loop - runs in separate thread."""
        while self.scanning.is_set() and not self.shutdown_event.is_set():
            try:
                # Perform WiFi scan
                max_networks = self.config.get("wifi_scanner.max_networks", 50)
                include_hidden = self.config.get("wifi_scanner.include_hidden", False)
                
                scan_result = self.scanner.scan(
                    max_networks=max_networks,
                    include_hidden=include_hidden
                )
                
                # Send encrypted data to control station
                if self.connected and self.channel:
                    self._send_scan_data(scan_result)
                
                # Log scan results
                network_count = scan_result.get("total_networks", 0)
                scan_duration = scan_result.get("scan_duration", 0)
                self.logger.info("WiFi scan completed", 
                               networks=network_count, 
                               duration_sec=scan_duration)
                
            except Exception as e:
                self.logger.error("Scan error", error=str(e))
            
            # Wait for next scan interval
            self.shutdown_event.wait(self.scan_interval)
    
    def _send_scan_data(self, scan_result: dict):
        """Send encrypted scan data to control station."""
        try:
            # Convert to JSON and encode
            data_json = json.dumps(scan_result)
            data_bytes = data_json.encode('utf-8')
            
            # Encrypt and sign
            encrypted_msg = self.channel.send(data_bytes, sign=True)
            
            # Send to control station
            msg_data = {
                "type": "scan_data",
                "drone_id": self.drone_id,
                "payload": encrypted_msg.hex()
            }
            self._send_json(msg_data)
            
        except Exception as e:
            self.logger.error("Failed to send scan data", error=str(e))
            raise
    
    def _send_json(self, data: dict):
        """Send JSON data over socket."""
        if not self.socket:
            raise RuntimeError("Not connected")
        
        json_str = json.dumps(data)
        message = json_str.encode('utf-8')
        length = len(message)
        
        # Send length prefix (4 bytes) then message
        self.socket.sendall(length.to_bytes(4, 'big') + message)
    
    def _receive_json(self) -> dict:
        """Receive JSON data from socket."""
        if not self.socket:
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
            chunk = self.socket.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data
    
    def listen_for_commands(self):
        """Listen for commands from control station."""
        self.logger.info("Listening for commands...")
        
        try:
            while self.connected and not self.shutdown_event.is_set():
                # Set timeout to check shutdown event periodically
                self.socket.settimeout(1.0)
                
                try:
                    cmd_data = self._receive_json()
                    self._handle_command(cmd_data)
                    
                except socket.timeout:
                    continue  # Check shutdown event and continue
                    
        except Exception as e:
            if not self.shutdown_event.is_set():
                self.logger.error("Command listening error", error=str(e))
    
    def _handle_command(self, cmd_data: dict):
        """Handle command from control station."""
        cmd_type = cmd_data.get("type")
        
        if cmd_type == "START_SCAN":
            self.start_scanning()
            self._send_ack("Scanning started")
            
        elif cmd_type == "STOP_SCAN":
            self.stop_scanning()
            self._send_ack("Scanning stopped")
            
        elif cmd_type == "SET_INTERVAL":
            interval = cmd_data.get("interval", 5.0)
            self.scan_interval = interval
            self.logger.info("Scan interval updated", interval=interval)
            self._send_ack(f"Interval set to {interval} seconds")
            
        elif cmd_type == "SHUTDOWN":
            self.logger.info("Shutdown command received")
            self._send_ack("Shutting down")
            self.shutdown()
            
        else:
            self.logger.warning("Unknown command", command=cmd_type)
    
    def _send_ack(self, message: str):
        """Send acknowledgment message."""
        try:
            ack_data = {
                "type": "ack",
                "drone_id": self.drone_id,
                "message": message
            }
            self._send_json(ack_data)
        except Exception as e:
            self.logger.error("Failed to send ACK", error=str(e))
    
    def shutdown(self):
        """Graceful shutdown."""
        self.logger.info("Shutting down drone application...")
        
        self.shutdown_event.set()
        self.stop_scanning()
        
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=2)
        
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.logger.info("Drone application shutdown complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Drone WiFi Scanner Application")
    parser.add_argument("--host", type=str, help="Control station IP address")
    parser.add_argument("--port", type=int, help="Control station port")
    parser.add_argument("--config", type=str, default="config/drone_config.json",
                       help="Configuration file path")
    parser.add_argument("--drone-id", type=str, help="Drone identifier")
    parser.add_argument("--scan-interval", type=float, help="Scan interval in seconds")
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = Config(args.config)
    except Exception:
        print(f"Warning: Could not load config file {args.config}, using defaults")
        config = Config()
    
    # Override with CLI arguments
    if args.host:
        config.set("network.control_station_host", args.host)
    if args.port:
        config.set("network.port", args.port)
    if args.drone_id:
        config.set("drone_id", args.drone_id)
    if args.scan_interval:
        config.set("wifi_scanner.scan_interval", args.scan_interval)
    
    # Get connection parameters
    host = config.get("network.control_station_host")
    port = config.get("network.port", 8443)
    
    if not host:
        print("Error: Control station host not specified!")
        print("Use --host <IP> or set in config file")
        sys.exit(1)
    
    # Create and run drone application
    drone = DroneApplication(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\n\nShutdown signal received...")
        drone.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize
        print(f"=== Drone Application ===")
        print(f"Drone ID: {drone.drone_id}")
        print(f"Control Station: {host}:{port}")
        print(f"WiFi Scanner: {drone.scanner.scan_tool}")
        print("=" * 40 + "\n")
        
        drone.initialize_crypto()
        drone.connect_to_control_station(host, port)
        drone.perform_key_exchange()
        
        print("✓ Connected and secured with post-quantum cryptography\n")
        
        # Auto-start scanning
        drone.start_scanning()
        
        # Listen for commands
        drone.listen_for_commands()
        
    except KeyboardInterrupt:
        print("\n\nShutdown requested...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        drone.shutdown()


if __name__ == "__main__":
    main()
