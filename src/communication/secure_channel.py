"""
Secure channel for encrypted and authenticated data transmission.
"""

from typing import Optional
from ..crypto import ChaCha20Poly1305Cipher, DilithiumSignature


class SecureChannel:
    """Manages secure data transmission using encryption and signatures."""
    
    def __init__(self, shared_secret: bytes, signing_key: Optional[DilithiumSignature] = None):
        """
        Initialize secure channel.
        
        Args:
            shared_secret: Shared secret for encryption
            signing_key: Optional Dilithium instance for signatures
        """
        self.cipher = ChaCha20Poly1305Cipher(shared_secret)
        self.signing_key = signing_key
        self.message_counter = 0
    
    def send(self, plaintext: bytes, sign: bool = False) -> dict:
        """
        Encrypt and optionally sign a message.
        
        Args:
            plaintext: Message to send
            sign: Whether to sign the message
            
        Returns:
            Dictionary with nonce, ciphertext, and optional signature
        """
        # Prepare associated data with message counter
        associated_data = self.message_counter.to_bytes(8, byteorder='big')
        
        # Encrypt message
        nonce, ciphertext = self.cipher.encrypt(plaintext, associated_data)
        
        message = {
            "nonce": nonce,
            "ciphertext": ciphertext,
            "counter": self.message_counter
        }
        
        # Optionally sign
        if sign and self.signing_key:
            signature = self.signing_key.sign(ciphertext)
            message["signature"] = signature
        
        self.message_counter += 1
        return message
    
    def receive(self, message: dict, verify_key: Optional[bytes] = None) -> bytes:
        """
        Decrypt and optionally verify a message.
        
        Args:
            message: Dictionary with nonce, ciphertext, counter, and optional signature
            verify_key: Optional public key for signature verification
            
        Returns:
            Decrypted plaintext
            
        Raises:
            ValueError: If signature verification fails or decryption fails
        """
        nonce = message["nonce"]
        ciphertext = message["ciphertext"]
        counter = message["counter"]
        
        # Verify signature if present
        if "signature" in message:
            if not verify_key:
                raise ValueError("Signature present but no verification key provided")
            
            if not self.signing_key.verify(ciphertext, message["signature"], verify_key):
                raise ValueError("Signature verification failed")
        
        # Prepare associated data
        associated_data = counter.to_bytes(8, byteorder='big')
        
        # Decrypt message
        plaintext = self.cipher.decrypt(nonce, ciphertext, associated_data)
        
        return plaintext
    
    def reset_counter(self):
        """Reset message counter (use with caution)."""
        self.message_counter = 0
    
    def get_counter(self) -> int:
        """Get current message counter."""
        return self.message_counter
