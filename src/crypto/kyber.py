"""
CRYSTALS-Kyber post-quantum key encapsulation mechanism (KEM).
"""

import oqs


class KyberKEM:
    """CRYSTALS-Kyber KEM for post-quantum security."""
    
    def __init__(self, variant: str = "Kyber768"):
        """
        Initialize Kyber KEM.
        
        Args:
            variant: Kyber variant (Kyber512, Kyber768, Kyber1024)
        """
        self.variant = variant
        self.kem = oqs.KeyEncapsulation(variant)
        self.public_key = None
        self.secret_key = None
    
    def generate_keypair(self):
        """Generate a new Kyber key pair."""
        self.public_key = self.kem.generate_keypair()
        self.secret_key = self.kem.export_secret_key()
        return self.public_key
    
    def encapsulate(self, peer_public_key: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulate a shared secret.
        
        Args:
            peer_public_key: Peer's public key
            
        Returns:
            Tuple of (ciphertext, shared_secret)
        """
        ciphertext, shared_secret = self.kem.encap_secret(peer_public_key)
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes) -> bytes:
        """
        Decapsulate to recover shared secret.
        
        Args:
            ciphertext: Encapsulated secret
            
        Returns:
            Shared secret
        """
        if self.secret_key is None:
            raise ValueError("No secret key available. Generate keypair first.")
        
        shared_secret = self.kem.decap_secret(ciphertext)
        return shared_secret
