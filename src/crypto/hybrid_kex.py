"""
Hybrid key exchange combining X448 and CRYSTALS-Kyber.
"""

import hashlib
from .x448 import X448KeyExchange
from .kyber import KyberKEM


class HybridKeyExchange:
    """Hybrid key exchange for both classical and post-quantum security."""
    
    def __init__(self):
        self.x448 = X448KeyExchange()
        self.kyber = KyberKEM()
        self.combined_secret = None
    
    def generate_keypair(self) -> tuple[bytes, bytes]:
        """
        Generate hybrid key pair.
        
        Returns:
            Tuple of (x448_public_key, kyber_public_key)
        """
        x448_pk = self.x448.generate_keypair()
        kyber_pk = self.kyber.generate_keypair()
        return x448_pk, kyber_pk
    
    def initiate_exchange(self, peer_x448_pk: bytes, peer_kyber_pk: bytes) -> tuple[bytes, bytes]:
        """
        Initiate key exchange (client side).
        
        Args:
            peer_x448_pk: Peer's X448 public key
            peer_kyber_pk: Peer's Kyber public key
            
        Returns:
            Tuple of (kyber_ciphertext, combined_secret)
        """
        # X448 key exchange
        x448_secret = self.x448.compute_shared_secret(peer_x448_pk)
        
        # Kyber encapsulation
        kyber_ct, kyber_secret = self.kyber.encapsulate(peer_kyber_pk)
        
        # Combine secrets using SHA-256
        self.combined_secret = self._combine_secrets(x448_secret, kyber_secret)
        
        return kyber_ct, self.combined_secret
    
    def complete_exchange(self, peer_x448_pk: bytes, kyber_ciphertext: bytes) -> bytes:
        """
        Complete key exchange (server side).
        
        Args:
            peer_x448_pk: Peer's X448 public key
            kyber_ciphertext: Kyber encapsulated secret
            
        Returns:
            Combined shared secret
        """
        # X448 key exchange
        x448_secret = self.x448.compute_shared_secret(peer_x448_pk)
        
        # Kyber decapsulation
        kyber_secret = self.kyber.decapsulate(kyber_ciphertext)
        
        # Combine secrets using SHA-256
        self.combined_secret = self._combine_secrets(x448_secret, kyber_secret)
        
        return self.combined_secret
    
    def _combine_secrets(self, x448_secret: bytes, kyber_secret: bytes) -> bytes:
        """
        Combine X448 and Kyber secrets using hash-based key derivation.
        
        Args:
            x448_secret: X448 shared secret
            kyber_secret: Kyber shared secret
            
        Returns:
            Combined 256-bit secret
        """
        combined = x448_secret + kyber_secret
        derived_key = hashlib.sha256(combined).digest()
        return derived_key
    
    def get_shared_secret(self) -> bytes:
        """Get the combined shared secret."""
        if self.combined_secret is None:
            raise ValueError("Key exchange not completed yet.")
        return self.combined_secret
