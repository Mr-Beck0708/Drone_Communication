"""
CRYSTALS-Dilithium post-quantum digital signature scheme.
"""

import oqs


class DilithiumSignature:
    """CRYSTALS-Dilithium signature scheme for post-quantum authentication."""
    
    def __init__(self, variant: str = "Dilithium3"):
        """
        Initialize Dilithium signature.
        
        Args:
            variant: Dilithium variant (Dilithium2, Dilithium3, Dilithium5)
        """
        self.variant = variant
        self.signer = oqs.Signature(variant)
        self.public_key = None
        self.secret_key = None
    
    def generate_keypair(self):
        """Generate a new Dilithium key pair."""
        self.public_key = self.signer.generate_keypair()
        self.secret_key = self.signer.export_secret_key()
        return self.public_key
    
    def sign(self, message: bytes) -> bytes:
        """
        Sign a message.
        
        Args:
            message: Message to sign
            
        Returns:
            Signature
        """
        if self.secret_key is None:
            raise ValueError("No secret key available. Generate keypair first.")
        
        signature = self.signer.sign(message)
        return signature
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes = None) -> bool:
        """
        Verify a signature.
        
        Args:
            message: Original message
            signature: Signature to verify
            public_key: Public key (uses own if None)
            
        Returns:
            True if signature is valid
        """
        verify_key = public_key if public_key else self.public_key
        if verify_key is None:
            raise ValueError("No public key available.")
        
        is_valid = self.signer.verify(message, signature, verify_key)
        return is_valid
