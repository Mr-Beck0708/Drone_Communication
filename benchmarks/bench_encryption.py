"""
Benchmark encryption and signature operations.
"""

import time
from src.crypto import ChaCha20Poly1305Cipher, DilithiumSignature


def benchmark_chacha20poly1305():
    """Benchmark ChaCha20-Poly1305 encryption."""
    iterations = 1000
    message_sizes = [64, 256, 1024, 4096, 16384]  # bytes
    
    print("Benchmarking ChaCha20-Poly1305 Encryption...")
    print(f"{'Size (bytes)':<15} {'Encrypt (ms)':<15} {'Decrypt (ms)':<15} {'Throughput (MB/s)':<20}")
    print("-" * 65)
    
    for size in message_sizes:
        plaintext = b"A" * size
        cipher = ChaCha20Poly1305Cipher()
        
        # Encryption
        start = time.time()
        for _ in range(iterations):
            nonce, ciphertext = cipher.encrypt(plaintext)
        encrypt_time = (time.time() - start) / iterations
        
        # Decryption
        nonce, ciphertext = cipher.encrypt(plaintext)
        start = time.time()
        for _ in range(iterations):
            cipher.decrypt(nonce, ciphertext)
        decrypt_time = (time.time() - start) / iterations
        
        # Throughput (MB/s)
        throughput = (size / 1024 / 1024) / encrypt_time
        
        print(f"{size:<15} {encrypt_time*1000:<15.3f} {decrypt_time*1000:<15.3f} {throughput:<20.2f}")
    
    print()


def benchmark_dilithium():
    """Benchmark Dilithium signatures."""
    iterations = 100
    
    print("Benchmarking CRYSTALS-Dilithium Signatures...")
    
    # Key generation
    start = time.time()
    for _ in range(iterations):
        sig = DilithiumSignature()
        sig.generate_keypair()
    keygen_time = (time.time() - start) / iterations
    
    # Signing
    sig = DilithiumSignature()
    public_key = sig.generate_keypair()
    message = b"Test message for signing"
    
    start = time.time()
    for _ in range(iterations):
        sig.sign(message)
    sign_time = (time.time() - start) / iterations
    
    # Verification
    signature = sig.sign(message)
    
    start = time.time()
    for _ in range(iterations):
        sig.verify(message, signature, public_key)
    verify_time = (time.time() - start) / iterations
    
    print(f"  Key generation: {keygen_time*1000:.2f} ms")
    print(f"  Signing:        {sign_time*1000:.2f} ms")
    print(f"  Verification:   {verify_time*1000:.2f} ms")
    print(f"  Total:          {(keygen_time + sign_time + verify_time)*1000:.2f} ms\n")


if __name__ == "__main__":
    print("=" * 70)
    print("Encryption and Signature Performance Benchmarks")
    print("=" * 70 + "\n")
    
    benchmark_chacha20poly1305()
    benchmark_dilithium()
    
    print("=" * 70)
