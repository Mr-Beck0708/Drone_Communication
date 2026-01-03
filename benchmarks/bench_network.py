"""
Benchmark network and communication operations.
"""

import time
from src.communication import Session, SecureChannel, NetworkMonitor
from src.crypto import ChaCha20Poly1305Cipher


def benchmark_session_management():
    """Benchmark session operations."""
    iterations = 10000
    
    print("Benchmarking Session Management...")
    
    # Session creation
    start = time.time()
    for i in range(iterations):
        session = Session(f"session-{i}")
    create_time = (time.time() - start) / iterations
    
    # Handshake completion
    sessions = [Session(f"session-{i}") for i in range(iterations)]
    start = time.time()
    for session in sessions:
        session.complete_handshake(b"shared_secret", "peer")
    handshake_time = (time.time() - start) / iterations
    
    print(f"  Session creation:       {create_time*1000000:.2f} μs")
    print(f"  Handshake completion:   {handshake_time*1000000:.2f} μs\n")


def benchmark_secure_channel():
    """Benchmark secure channel operations."""
    iterations = 1000
    message_sizes = [64, 256, 1024, 4096]
    
    print("Benchmarking Secure Channel...")
    print(f"{'Size (bytes)':<15} {'Send (ms)':<15} {'Receive (ms)':<15}")
    print("-" * 45)
    
    for size in message_sizes:
        plaintext = b"A" * size
        shared_secret = ChaCha20Poly1305Cipher.generate_key()
        channel = SecureChannel(shared_secret)
        
        # Send
        start = time.time()
        messages = []
        for _ in range(iterations):
            msg = channel.send(plaintext)
            messages.append(msg)
        send_time = (time.time() - start) / iterations
        
        # Receive
        start = time.time()
        for msg in messages:
            channel.receive(msg)
        receive_time = (time.time() - start) / iterations
        
        print(f"{size:<15} {send_time*1000:<15.3f} {receive_time*1000:<15.3f}")
    
    print()


def benchmark_network_monitor():
    """Benchmark network monitoring."""
    iterations = 10000
    
    print("Benchmarking Network Monitor...")
    
    monitor = NetworkMonitor()
    
    # Latency recording
    start = time.time()
    for i in range(iterations):
        monitor.record_latency(0.05 + (i % 10) * 0.01)
    latency_time = (time.time() - start) / iterations
    
    # Statistics calculation
    start = time.time()
    for _ in range(iterations):
        monitor.get_average_latency()
        monitor.get_packet_loss_rate()
        monitor.get_connection_quality()
    stats_time = (time.time() - start) / iterations
    
    print(f"  Latency recording:  {latency_time*1000000:.2f} μs")
    print(f"  Statistics calc:    {stats_time*1000000:.2f} μs\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Network and Communication Performance Benchmarks")
    print("=" * 50 + "\n")
    
    benchmark_session_management()
    benchmark_secure_channel()
    benchmark_network_monitor()
    
    print("=" * 50)
