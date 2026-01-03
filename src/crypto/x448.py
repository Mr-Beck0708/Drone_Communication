"""
X448 Elliptic Curve Diffie-Hellman key exchange implementation.
"""

from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives import serialization


class X448KeyExchange:
    """X448 key exchange for classical cryptographic security."""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        
    def generate_keypair(self):
        """Generate a new X448 key pair."""
        self.private_key = x448.X448PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        return self.get_public_key_bytes()
    
    def get_public_key_bytes(self):
        """Get public key as bytes."""
        if self.public_key is None:
            raise ValueError("No public key available. Generate keypair first.")
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def compute_shared_secret(self, peer_public_key_bytes: bytes) -> bytes:
        """Compute shared secret from peer's public key."""
        if self.private_key is None:
            raise ValueError("No private key available. Generate keypair first.")
        
        peer_public_key = x448.X448PublicKey.from_public_bytes(peer_public_key_bytes)
        shared_secret = self.private_key.exchange(peer_public_key)
        return shared_secret
