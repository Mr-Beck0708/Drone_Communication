"""
ChaCha20-Poly1305 authenticated encryption with associated data (AEAD).
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


class ChaCha20Poly1305Cipher:
    """ChaCha20-Poly1305 AEAD cipher for secure communication."""
    
    def __init__(self, key: bytes = None):
        """
        Initialize cipher with optional key.
        
        Args:
            key: 256-bit (32-byte) encryption key
        """
        if key is not None:
            if len(key) != 32:
                raise ValueError("Key must be 32 bytes (256 bits)")
            self.key = key
        else:
            self.key = ChaCha20Poly1305.generate_key()
        
        self.cipher = ChaCha20Poly1305(self.key)
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> tuple[bytes, bytes]:
        """
        Encrypt plaintext with optional associated data.
        
        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data (AAD)
            
        Returns:
            Tuple of (nonce, ciphertext)
        """
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = self.cipher.encrypt(nonce, plaintext, associated_data)
        return nonce, ciphertext
    
    def decrypt(self, nonce: bytes, ciphertext: bytes, associated_data: bytes = None) -> bytes:
        """
        Decrypt ciphertext with optional associated data.
        
        Args:
            nonce: Nonce used during encryption
            ciphertext: Encrypted data
            associated_data: Additional authenticated data (AAD)
            
        Returns:
            Decrypted plaintext
            
        Raises:
            InvalidTag: If authentication fails
        """
        plaintext = self.cipher.decrypt(nonce, ciphertext, associated_data)
        return plaintext
    
    def get_key(self) -> bytes:
        """Get the encryption key."""
        return self.key
