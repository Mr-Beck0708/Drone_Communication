"""
Operator-Drone communication scenario demonstration.
"""

import time
from src.crypto import HybridKeyExchange, DilithiumSignature
from src.communication import Session, SecureChannel, TelemetryLogger, NetworkMonitor
from src.utils import setup_logger


class Operator:
    """Represents the ground station operator."""
    
    def __init__(self, operator_id: str):
        self.operator_id = operator_id
        self.kex = HybridKeyExchange()
        self.sig = DilithiumSignature()
        self.session = None
        self.channel = None
        self.logger = setup_logger(f"operator_{operator_id}")
        
    def initialize(self):
        """Initialize operator's cryptographic keys."""
        self.x448_pk, self.kyber_pk = self.kex.generate_keypair()
        self.sign_pk = self.sig.generate_keypair()
        self.logger.info("Operator initialized", operator_id=self.operator_id)
        
    def establish_connection(self, drone_x448_pk, drone_kyber_pk):
        """Establish connection with drone."""
        kyber_ct, shared_secret = self.kex.initiate_exchange(drone_x448_pk, drone_kyber_pk)
        
        self.session = Session(f"{self.operator_id}_session")
        self.session.complete_handshake(shared_secret, "drone")
        
        self.channel = SecureChannel(shared_secret, self.sig)
        
        self.logger.info("Connection established with drone")
        return kyber_ct
        
    def send_command(self, command: str, drone_sign_pk):
        """Send command to drone."""
        message = command.encode()
        encrypted_msg = self.channel.send(message, sign=True)
        self.logger.info("Command sent", command=command)
        return encrypted_msg
        
    def receive_telemetry(self, encrypted_msg, drone_sign_pk):
        """Receive telemetry from drone."""
        telemetry = self.channel.receive(encrypted_msg, drone_sign_pk)
        self.logger.info("Telemetry received", data=telemetry.decode())
        return telemetry


class Drone:
    """Represents the unmanned aerial vehicle."""
    
    def __init__(self, drone_id: str):
        self.drone_id = drone_id
        self.kex = HybridKeyExchange()
        self.sig = DilithiumSignature()
        self.session = None
        self.channel = None
        self.logger = setup_logger(f"drone_{drone_id}")
        self.monitor = NetworkMonitor()
        
    def initialize(self):
        """Initialize drone's cryptographic keys."""
        self.x448_pk, self.kyber_pk = self.kex.generate_keypair()
        self.sign_pk = self.sig.generate_keypair()
        self.logger.info("Drone initialized", drone_id=self.drone_id)
        
    def accept_connection(self, operator_x448_pk, kyber_ct):
        """Accept connection from operator."""
        shared_secret = self.kex.complete_exchange(operator_x448_pk, kyber_ct)
        
        self.session = Session(f"{self.drone_id}_session")
        self.session.complete_handshake(shared_secret, "operator")
        
        self.channel = SecureChannel(shared_secret, self.sig)
        
        self.logger.info("Connection accepted from operator")
        
    def receive_command(self, encrypted_msg, operator_sign_pk):
        """Receive command from operator."""
        command = self.channel.receive(encrypted_msg, operator_sign_pk)
        self.logger.info("Command received", command=command.decode())
        self.monitor.record_packet_sent()
        return command
        
    def send_telemetry(self, telemetry_data: dict):
        """Send telemetry to operator."""
        import json
        message = json.dumps(telemetry_data).encode()
        encrypted_msg = self.channel.send(message, sign=True)
        self.logger.info("Telemetry sent", data=telemetry_data)
        self.monitor.record_packet_sent()
        return encrypted_msg


def main():
    """Run operator-drone communication demo."""
    print("=" * 70)
    print("Operator-Drone Communication Demonstration")
    print("=" * 70 + "\n")
    
    telemetry_logger = TelemetryLogger("operator_drone_telemetry.log")
    
    # Initialize operator and drone
    print("1. Initializing Operator and Drone...")
    operator = Operator("OP-001")
    drone = Drone("DRONE-UAV-01")
    
    operator.initialize()
    drone.initialize()
    print("   ✓ Operator and Drone initialized\n")
    
    # Establish secure connection
    print("2. Establishing secure connection...")
    start_time = time.time()
    
    kyber_ct = operator.establish_connection(drone.x448_pk, drone.kyber_pk)
    drone.accept_connection(operator.x448_pk, kyber_ct)
    
    handshake_duration = time.time() - start_time
    telemetry_logger.log_handshake("op_drone_session", handshake_duration, True)
    
    print(f"   ✓ Secure connection established in {handshake_duration*1000:.2f} ms\n")
    
    # Mission scenario
    print("3. Mission Scenario: Reconnaissance Flight")
    print("-" * 70)
    
    # Command 1: Takeoff
    print("\n   [OPERATOR] Sending takeoff command...")
    cmd1 = operator.send_command("TAKEOFF:ALTITUDE=100", drone.sign_pk)
    received_cmd1 = drone.receive_command(cmd1, operator.sign_pk)
    print(f"   [DRONE] Executing: {received_cmd1.decode()}")
    
    time.sleep(0.5)
    
    # Telemetry 1
    print("\n   [DRONE] Sending telemetry...")
    telemetry1 = {
        "altitude": 100,
        "speed": 15,
        "battery": 95,
        "status": "airborne",
        "gps": {"lat": 37.7749, "lon": -122.4194}
    }
    telem_msg1 = drone.send_telemetry(telemetry1)
    received_telem1 = operator.receive_telemetry(telem_msg1, drone.sign_pk)
    print(f"   [OPERATOR] Telemetry: Altitude={telemetry1['altitude']}m, Battery={telemetry1['battery']}%")
    
    time.sleep(0.5)
    
    # Command 2: Navigate to waypoint
    print("\n   [OPERATOR] Sending navigation command...")
    cmd2 = operator.send_command("NAVIGATE:LAT=37.7849,LON=-122.4094", drone.sign_pk)
    received_cmd2 = drone.receive_command(cmd2, operator.sign_pk)
    print(f"   [DRONE] Executing: {received_cmd2.decode()}")
    
    time.sleep(0.5)
    
    # Telemetry 2
    print("\n   [DRONE] Sending telemetry...")
    telemetry2 = {
        "altitude": 100,
        "speed": 20,
        "battery": 88,
        "status": "navigating",
        "gps": {"lat": 37.7849, "lon": -122.4094}
    }
    telem_msg2 = drone.send_telemetry(telemetry2)
    received_telem2 = operator.receive_telemetry(telem_msg2, drone.sign_pk)
    print(f"   [OPERATOR] Telemetry: Speed={telemetry2['speed']}m/s, Battery={telemetry2['battery']}%")
    
    time.sleep(0.5)
    
    # Command 3: Return to base
    print("\n   [OPERATOR] Sending return command...")
    cmd3 = operator.send_command("RETURN_TO_BASE", drone.sign_pk)
    received_cmd3 = drone.receive_command(cmd3, operator.sign_pk)
    print(f"   [DRONE] Executing: {received_cmd3.decode()}")
    
    time.sleep(0.5)
    
    # Final telemetry
    print("\n   [DRONE] Sending final telemetry...")
    telemetry3 = {
        "altitude": 0,
        "speed": 0,
        "battery": 76,
        "status": "landed",
        "gps": {"lat": 37.7749, "lon": -122.4194}
    }
    telem_msg3 = drone.send_telemetry(telemetry3)
    received_telem3 = operator.receive_telemetry(telem_msg3, drone.sign_pk)
    print(f"   [OPERATOR] Telemetry: Status={telemetry3['status']}, Battery={telemetry3['battery']}%")
    
    print("\n" + "-" * 70)
    
    # Network statistics
    print("\n4. Network Statistics:")
    monitor_summary = drone.monitor.get_monitor_summary()
    print(f"   • Connection quality: {monitor_summary['connection_quality']}")
    print(f"   • Total packets sent: {monitor_summary['total_packets_sent']}")
    print(f"   • Packet loss rate: {monitor_summary['packet_loss_rate']:.2f}%")
    
    # Session information
    print("\n5. Session Information:")
    op_info = operator.session.get_session_info()
    drone_info = drone.session.get_session_info()
    print(f"   • Operator session: {op_info['state']} (duration: {op_info['duration']:.2f}s)")
    print(f"   • Drone session: {drone_info['state']} (duration: {drone_info['duration']:.2f}s)")
    
    print("\n" + "=" * 70)
    print("Mission completed successfully!")
    print("=" * 70)
    print("\nSecurity features verified:")
    print("  ✓ All commands encrypted and authenticated")
    print("  ✓ All telemetry encrypted and signed")
    print("  ✓ Post-quantum cryptography protecting communications")
    print("  ✓ Session management tracking connection state")


if __name__ == "__main__":
    main()
