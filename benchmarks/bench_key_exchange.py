"""
Benchmark key exchange operations.
"""

import time
from memory_profiler import profile
from src.crypto import X448KeyExchange, KyberKEM, HybridKeyExchange


def benchmark_x448():
    """Benchmark X448 key exchange."""
    iterations = 100
    
    print("Benchmarking X448 Key Exchange...")
    
    # Key generation
    start = time.time()
    for _ in range(iterations):
        kex = X448KeyExchange()
        kex.generate_keypair()
    keygen_time = (time.time() - start) / iterations
    
    # Shared secret computation
    alice = X448KeyExchange()
    bob = X448KeyExchange()
    alice_pk = alice.generate_keypair()
    bob_pk = bob.generate_keypair()
    
    start = time.time()
    for _ in range(iterations):
        alice.compute_shared_secret(bob_pk)
    exchange_time = (time.time() - start) / iterations
    
    print(f"  Key generation: {keygen_time*1000:.2f} ms")
    print(f"  Shared secret:  {exchange_time*1000:.2f} ms")
    print(f"  Total:          {(keygen_time + exchange_time)*1000:.2f} ms\n")


def benchmark_kyber():
    """Benchmark Kyber KEM."""
    iterations = 100
    
    print("Benchmarking CRYSTALS-Kyber KEM...")
    
    # Key generation
    start = time.time()
    for _ in range(iterations):
        kem = KyberKEM()
        kem.generate_keypair()
    keygen_time = (time.time() - start) / iterations
    
    # Encapsulation
    kem = KyberKEM()
    public_key = kem.generate_keypair()
    
    start = time.time()
    for _ in range(iterations):
        kem.encapsulate(public_key)
    encap_time = (time.time() - start) / iterations
    
    # Decapsulation
    ciphertext, _ = kem.encapsulate(public_key)
    
    start = time.time()
    for _ in range(iterations):
        kem.decapsulate(ciphertext)
    decap_time = (time.time() - start) / iterations
    
    print(f"  Key generation:  {keygen_time*1000:.2f} ms")
    print(f"  Encapsulation:   {encap_time*1000:.2f} ms")
    print(f"  Decapsulation:   {decap_time*1000:.2f} ms")
    print(f"  Total:           {(keygen_time + encap_time + decap_time)*1000:.2f} ms\n")


def benchmark_hybrid():
    """Benchmark hybrid key exchange."""
    iterations = 100
    
    print("Benchmarking Hybrid Key Exchange (X448 + Kyber)...")
    
    # Setup
    alice = HybridKeyExchange()
    bob = HybridKeyExchange()
    
    # Key generation
    start = time.time()
    for _ in range(iterations):
        hybrid = HybridKeyExchange()
        hybrid.generate_keypair()
    keygen_time = (time.time() - start) / iterations
    
    # Exchange
    alice_x448_pk, alice_kyber_pk = alice.generate_keypair()
    bob_x448_pk, bob_kyber_pk = bob.generate_keypair()
    
    start = time.time()
    for _ in range(iterations):
        alice.initiate_exchange(bob_x448_pk, bob_kyber_pk)
    initiate_time = (time.time() - start) / iterations
    
    kyber_ct, _ = alice.initiate_exchange(bob_x448_pk, bob_kyber_pk)
    
    start = time.time()
    for _ in range(iterations):
        bob.complete_exchange(alice_x448_pk, kyber_ct)
    complete_time = (time.time() - start) / iterations
    
    print(f"  Key generation: {keygen_time*1000:.2f} ms")
    print(f"  Initiate:       {initiate_time*1000:.2f} ms")
    print(f"  Complete:       {complete_time*1000:.2f} ms")
    print(f"  Total:          {(keygen_time + initiate_time + complete_time)*1000:.2f} ms\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Key Exchange Performance Benchmarks")
    print("=" * 60 + "\n")
    
    benchmark_x448()
    benchmark_kyber()
    benchmark_hybrid()
    
    print("=" * 60)
