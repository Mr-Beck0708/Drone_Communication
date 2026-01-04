"""
Unit tests for communication modules.
"""

import pytest
import time
import os
from src.communication import Session, TelemetryLogger, NetworkMonitor, SecureChannel
from src.crypto import ChaCha20Poly1305Cipher, DilithiumSignature


class TestSession:
    """Tests for session management."""
    
    def test_session_initialization(self):
        """Test session initialization."""
        session = Session("test-session-1")
        assert session.session_id == "test-session-1"
        assert not session.is_active()
    
    def test_session_lifecycle(self):
        """Test complete session lifecycle."""
        session = Session("test-session-2")
        
        session.start_handshake()
        assert session.state.value == "handshake"
        
        session.complete_handshake(b"shared_secret", "peer-1")
        assert session.is_active()
        assert session.peer_id == "peer-1"
        
        session.close()
        assert not session.is_active()
    
    def test_session_expiration(self):
        """Test session expiration."""
        session = Session("test-session-3")
        assert not session.is_expired(timeout=1.0)
        
        time.sleep(1.1)
        assert session.is_expired(timeout=1.0)


class TestTelemetryLogger:
    """Tests for telemetry logging."""
    
    def test_log_event(self, tmp_path):
        """Test event logging."""
        log_file = tmp_path / "test_telemetry.log"
        logger = TelemetryLogger(str(log_file))
        
        logger.log_event("test_event", {"key": "value"})
        assert log_file.exists()
    
    def test_log_handshake(self, tmp_path):
        """Test handshake logging."""
        log_file = tmp_path / "test_handshake.log"
        logger = TelemetryLogger(str(log_file))
        
        logger.log_handshake("session-1", 0.5, True)
        assert log_file.exists()


class TestNetworkMonitor:
    """Tests for network monitoring."""
    
    def test_initialization(self):
        """Test monitor initialization."""
        monitor = NetworkMonitor()
        assert monitor.start_time > 0
    
    def test_latency_recording(self):
        """Test latency recording."""
        monitor = NetworkMonitor()
        
        monitor.record_latency(0.05)
        monitor.record_latency(0.10)
        
        avg = monitor.get_average_latency()
        assert avg == pytest.approx(75.0)  # (50ms + 100ms) / 2
    
    def test_packet_loss_tracking(self):
        """Test packet loss tracking."""
        monitor = NetworkMonitor()
        
        for _ in range(10):
            monitor.record_packet_sent()
        
        monitor.record_packet_loss()
        monitor.record_packet_loss()
        
        assert monitor.get_packet_loss_rate() == 20.0  # 2/10


class TestSecureChannel:
    """Tests for secure channel."""
    
    def test_send_receive(self):
        """Test sending and receiving messages."""
        shared_secret = os.urandom(32)  # Generate 256-bit key
        channel = SecureChannel(shared_secret)
        
        plaintext = b"Test message"
        message = channel.send(plaintext)
        
        received = channel.receive(message)
        assert received == plaintext
    
    def test_send_receive_with_signature(self):
        """Test signed messages."""
        shared_secret = os.urandom(32)  # Generate 256-bit key
        sig = DilithiumSignature()
        public_key = sig.generate_keypair()
        
        channel = SecureChannel(shared_secret, sig)
        
        plaintext = b"Test message"
        message = channel.send(plaintext, sign=True)
        
        assert "signature" in message
        
        received = channel.receive(message, public_key)
        assert received == plaintext
