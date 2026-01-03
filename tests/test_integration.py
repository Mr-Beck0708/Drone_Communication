"""
Integration tests for end-to-end workflows.
"""

import pytest
from src.crypto import HybridKeyExchange, DilithiumSignature
from src.communication import Session, SecureChannel


class TestEndToEndCommunication:
    """Integration tests for complete communication flow."""
    
    def test_complete_handshake_and_message_exchange(self):
        """Test complete handshake and message exchange between two parties."""
        # Setup operator and drone
        operator_kex = HybridKeyExchange()
        drone_kex = HybridKeyExchange()
        
        operator_sig = DilithiumSignature()
        drone_sig = DilithiumSignature()
        
        # Generate keys
        op_x448_pk, op_kyber_pk = operator_kex.generate_keypair()
        drone_x448_pk, drone_kyber_pk = drone_kex.generate_keypair()
        
        op_sign_pk = operator_sig.generate_keypair()
        drone_sign_pk = drone_sig.generate_keypair()
        
        # Perform key exchange
        kyber_ct, op_secret = operator_kex.initiate_exchange(drone_x448_pk, drone_kyber_pk)
        drone_secret = drone_kex.complete_exchange(op_x448_pk, kyber_ct)
        
        assert op_secret == drone_secret
        
        # Create sessions
        op_session = Session("operator-session")
        drone_session = Session("drone-session")
        
        op_session.complete_handshake(op_secret, "drone")
        drone_session.complete_handshake(drone_secret, "operator")
        
        # Create secure channels
        op_channel = SecureChannel(op_secret, operator_sig)
        drone_channel = SecureChannel(drone_secret, drone_sig)
        
        # Operator sends message to drone
        message = b"Return to base"
        encrypted_msg = op_channel.send(message, sign=True)
        
        # Drone receives message
        decrypted_msg = drone_channel.receive(encrypted_msg, op_sign_pk)
        assert decrypted_msg == message
        
        # Drone sends response
        response = b"Acknowledged, returning to base"
        encrypted_response = drone_channel.send(response, sign=True)
        
        # Operator receives response
        decrypted_response = op_channel.receive(encrypted_response, drone_sign_pk)
        assert decrypted_response == response
    
    def test_session_management(self):
        """Test session creation and management."""
        session = Session("integration-test-session")
        
        # Start handshake
        session.start_handshake()
        assert session.state.value == "handshake"
        
        # Complete handshake
        shared_secret = b"test_shared_secret_32_bytes_long"
        session.complete_handshake(shared_secret, "peer-drone")
        
        assert session.is_active()
        assert session.peer_id == "peer-drone"
        
        # Get session info
        info = session.get_session_info()
        assert info["session_id"] == "integration-test-session"
        assert info["peer_id"] == "peer-drone"
        assert info["state"] == "active"
