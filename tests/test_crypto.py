"""
Unit tests for cryptographic modules.
"""

import pytest
from src.crypto import (
    X448KeyExchange,
    KyberKEM,
    DilithiumSignature,
    ChaCha20Poly1305Cipher,
    HybridKeyExchange
)


class TestX448KeyExchange:
    """Tests for X448 key exchange."""
    
    def test_keypair_generation(self):
        """Test X448 keypair generation."""
        kex = X448KeyExchange()
        public_key = kex.generate_keypair()
        assert len(public_key) == 56  # X448 public key is 56 bytes
    
    def test_shared_secret(self):
        """Test X448 shared secret computation."""
        alice = X448KeyExchange()
        bob = X448KeyExchange()
        
        alice_pk = alice.generate_keypair()
        bob_pk = bob.generate_keypair()
        
        alice_secret = alice.compute_shared_secret(bob_pk)
        bob_secret = bob.compute_shared_secret(alice_pk)
        
        assert alice_secret == bob_secret
        assert len(alice_secret) == 56


class TestKyberKEM:
    """Tests for CRYSTALS-Kyber KEM."""
    
    def test_keypair_generation(self):
        """Test Kyber keypair generation."""
        kem = KyberKEM()
        public_key = kem.generate_keypair()
        assert public_key is not None
        assert len(public_key) > 0
    
    def test_encapsulation_decapsulation(self):
        """Test Kyber encapsulation and decapsulation."""
        kem = KyberKEM()
        public_key = kem.generate_keypair()
        
        ciphertext, shared_secret_enc = kem.encapsulate(public_key)
        shared_secret_dec = kem.decapsulate(ciphertext)
        
        assert shared_secret_enc == shared_secret_dec


class TestDilithiumSignature:
    """Tests for CRYSTALS-Dilithium signatures."""
    
    def test_keypair_generation(self):
        """Test Dilithium keypair generation."""
        sig = DilithiumSignature()
        public_key = sig.generate_keypair()
        assert public_key is not None
        assert len(public_key) > 0
    
    def test_sign_verify(self):
        """Test signing and verification."""
        sig = DilithiumSignature()
        sig.generate_keypair()
        
        message = b"Test message"
        signature = sig.sign(message)
        
        assert sig.verify(message, signature)
        assert not sig.verify(b"Wrong message", signature)


class TestChaCha20Poly1305:
    """Tests for ChaCha20-Poly1305 cipher."""
    
    def test_encryption_decryption(self):
        """Test encryption and decryption."""
        cipher = ChaCha20Poly1305Cipher()
        plaintext = b"Secret message"
        
        nonce, ciphertext = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(nonce, ciphertext)
        
        assert decrypted == plaintext
    
    def test_authenticated_encryption(self):
        """Test AEAD with associated data."""
        cipher = ChaCha20Poly1305Cipher()
        plaintext = b"Secret message"
        aad = b"Additional data"
        
        nonce, ciphertext = cipher.encrypt(plaintext, aad)
        decrypted = cipher.decrypt(nonce, ciphertext, aad)
        
        assert decrypted == plaintext


class TestHybridKeyExchange:
    """Tests for hybrid key exchange."""
    
    def test_hybrid_key_exchange(self):
        """Test complete hybrid key exchange."""
        alice = HybridKeyExchange()
        bob = HybridKeyExchange()
        
        # Generate keypairs
        alice_x448_pk, alice_kyber_pk = alice.generate_keypair()
        bob_x448_pk, bob_kyber_pk = bob.generate_keypair()
        
        # Alice initiates exchange
        kyber_ct, alice_secret = alice.initiate_exchange(bob_x448_pk, bob_kyber_pk)
        
        # Bob completes exchange
        bob_secret = bob.complete_exchange(alice_x448_pk, kyber_ct)
        
        # Secrets should match
        assert alice_secret == bob_secret
        assert len(alice_secret) == 32  # SHA-256 output
