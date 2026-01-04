#!/usr/bin/env python3
"""
Test script for Raspberry Pi Drone setup
Verifies all components work before connecting to control station
"""

import sys

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("Testing Imports...")
    print("=" * 60)
    
    try:
        from src.crypto import HybridKeyExchange, DilithiumSignature
        print("✓ Cryptography modules imported")
    except Exception as e:
        print(f"✗ Cryptography import failed: {e}")
        return False
    
    try:
        from src.communication import Session, SecureChannel
        print("✓ Communication modules imported")
    except Exception as e:
        print(f"✗ Communication import failed: {e}")
        return False
    
    try:
        from src.utils import Config, setup_logger
        print("✓ Utility modules imported")
    except Exception as e:
        print(f"✗ Utility import failed: {e}")
        return False
    
    try:
        from src.utils.wifi_scanner import WiFiScanner
        print("✓ WiFi scanner imported")
    except Exception as e:
        print(f"✗ WiFi scanner import failed: {e}")
        return False
    
    print()
    return True


def test_wifi_scanner():
    """Test WiFi scanning functionality."""
    print("=" * 60)
    print("Testing WiFi Scanner...")
    print("=" * 60)
    
    try:
        from src.utils.wifi_scanner import WiFiScanner
        
        scanner = WiFiScanner()
        print(f"✓ Scanner initialized: {scanner.scan_tool}")
        
        print("Scanning for networks (this may take a few seconds)...")
        result = scanner.scan(max_networks=5)
        
        networks = result.get("networks", [])
        total = result.get("total_networks", 0)
        duration = result.get("scan_duration", 0)
        
        print(f"✓ Scan completed: {total} networks found in {duration}s")
        
        if networks:
            print("\nDetected Networks:")
            print("-" * 60)
            for net in networks[:3]:
                ssid = net.get("ssid", "Hidden")[:30]
                signal = net.get("signal_strength", -100)
                encryption = net.get("encryption", "Unknown")
                print(f"  - {ssid:<30} {signal:>4} dBm  {encryption}")
            
            if total > 3:
                print(f"  ... and {total - 3} more")
        print()
        return True
        
    except Exception as e:
        print(f"✗ WiFi scanner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cryptography():
    """Test cryptographic functions."""
    print("=" * 60)
    print("Testing Cryptography...")
    print("=" * 60)
    
    try:
        from src.crypto import HybridKeyExchange, DilithiumSignature
        
        # Test key exchange
        kex = HybridKeyExchange()
        x448_pk, kyber_pk = kex.generate_keypair()
        print(f"✓ Key generation: X448={len(x448_pk)} bytes, Kyber={len(kyber_pk)} bytes")
        
        # Test signatures
        sig = DilithiumSignature()
        pub_key = sig.generate_keypair()
        print(f"✓ Signature key generation: {len(pub_key)} bytes")
        
        # Test signing
        message = b"Test message for drone"
        signature = sig.sign(message)
        verified = sig.verify(message, signature, pub_key)
        print(f"✓ Signature verification: {verified}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Cryptography test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration loading."""
    print("=" * 60)
    print("Testing Configuration...")
    print("=" * 60)
    
    try:
        from src.utils import Config
        
        # Load drone config
        config = Config("config/drone_config.json")
        
        drone_id = config.get("drone_id")
        print(f"✓ Drone ID: {drone_id}")
        
        cs_host = config.get("network.control_station_host")
        port = config.get("network.port")
        print(f"✓ Control Station: {cs_host}:{port}")
        
        scan_interval = config.get("wifi_scanner.scan_interval")
        print(f"✓ Scan interval: {scan_interval}s")
        
        
        if cs_host == "192.168.1.100":
            print("\n⚠️  WARNING: Using default control station IP (192.168.1.100)")
            print("   Update config/drone_config.json with your laptop's actual IP")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RASPBERRY PI DRONE - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("WiFi Scanner", test_wifi_scanner),
        ("Cryptography", test_cryptography),
        ("Configuration", test_configuration),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:<30} {status}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("=" * 60)
        print("✓ ALL TESTS PASSED - Drone is ready!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Find your laptop's IP address")
        print("2. Update config/drone_config.json with laptop IP")
        print("3. On laptop, run: python3 control_station_app.py")
        print("4. On Pi, run: python3 drone_app.py")
        print()
        return 0
    else:
        print("=" * 60)
        print("✗ SOME TESTS FAILED - Check errors above")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
