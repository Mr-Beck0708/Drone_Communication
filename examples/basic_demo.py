"""
Basic demonstration of the drone communication system.
"""

from src.crypto import HybridKeyExchange, DilithiumSignature
from src.communication import Session, SecureChannel
from src.utils import setup_logger


def main():
    """Run basic demo."""
    logger = setup_logger("basic_demo")
    
    print("=" * 60)
    print("Drone Communication System - Basic Demo")
    print("=" * 60 + "\n")
    
    # 1. Initialize cryptographic components
    print("1. Initializing cryptographic components...")
    
    alice_kex = HybridKeyExchange()
    bob_kex = HybridKeyExchange()
    
    alice_sig = DilithiumSignature()
    bob_sig = DilithiumSignature()
    
    print("   ✓ Hybrid key exchange initialized")
    print("   ✓ Digital signatures initialized\n")
    
    # 2. Generate keys
    print("2. Generating cryptographic keys...")
    
    alice_x448_pk, alice_kyber_pk = alice_kex.generate_keypair()
    bob_x448_pk, bob_kyber_pk = bob_kex.generate_keypair()
    
    alice_sign_pk = alice_sig.generate_keypair()
    bob_sign_pk = bob_sig.generate_keypair()
    
    print(f"   ✓ Alice's X448 public key: {len(alice_x448_pk)} bytes")
    print(f"   ✓ Alice's Kyber public key: {len(alice_kyber_pk)} bytes")
    print(f"   ✓ Bob's X448 public key: {len(bob_x448_pk)} bytes")
    print(f"   ✓ Bob's Kyber public key: {len(bob_kyber_pk)} bytes\n")
    
    # 3. Perform hybrid key exchange
    print("3. Performing hybrid key exchange...")
    
    # Alice initiates
    kyber_ct, alice_secret = alice_kex.initiate_exchange(bob_x448_pk, bob_kyber_pk)
    print("   ✓ Alice initiated key exchange")
    
    # Bob completes
    bob_secret = bob_kex.complete_exchange(alice_x448_pk, kyber_ct)
    print("   ✓ Bob completed key exchange")
    
    # Verify secrets match
    assert alice_secret == bob_secret, "Shared secrets don't match!"
    print(f"   ✓ Shared secret established: {len(alice_secret)} bytes\n")
    
    # 4. Create sessions
    print("4. Creating communication sessions...")
    
    alice_session = Session("alice-session")
    bob_session = Session("bob-session")
    
    alice_session.complete_handshake(alice_secret, "bob")
    bob_session.complete_handshake(bob_secret, "alice")
    
    print(f"   ✓ Alice's session: {alice_session.get_session_info()['state']}")
    print(f"   ✓ Bob's session: {bob_session.get_session_info()['state']}\n")
    
    # 5. Create secure channels
    print("5. Creating secure communication channels...")
    
    alice_channel = SecureChannel(alice_secret, alice_sig)
    bob_channel = SecureChannel(bob_secret, bob_sig)
    
    print("   ✓ Secure channels established\n")
    
    # 6. Exchange messages
    print("6. Exchanging encrypted and signed messages...")
    
    # Alice sends to Bob
    message1 = b"Hello Bob, this is Alice!"
    encrypted_msg1 = alice_channel.send(message1, sign=True)
    print(f"   → Alice sent: {message1.decode()}")
    
    decrypted_msg1 = bob_channel.receive(encrypted_msg1, alice_sign_pk)
    print(f"   ← Bob received: {decrypted_msg1.decode()}")
    
    # Bob sends to Alice
    message2 = b"Hi Alice! Message received and verified."
    encrypted_msg2 = bob_channel.send(message2, sign=True)
    print(f"   → Bob sent: {message2.decode()}")
    
    decrypted_msg2 = alice_channel.receive(encrypted_msg2, bob_sign_pk)
    print(f"   ← Alice received: {decrypted_msg2.decode()}\n")
    
    # 7. Summary
    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print("\nKey features demonstrated:")
    print("  ✓ Hybrid post-quantum key exchange (X448 + Kyber)")
    print("  ✓ Post-quantum digital signatures (Dilithium)")
    print("  ✓ Authenticated encryption (ChaCha20-Poly1305)")
    print("  ✓ Session management")
    print("  ✓ Secure bidirectional communication")
    
    logger.info("Basic demo completed successfully")


if __name__ == "__main__":
    main()
