# Drone Communication System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Post-Quantum](https://img.shields.io/badge/Security-Post--Quantum-brightgreen.svg)](https://openquantumsafe.org/)

**A post-quantum secure communication system for drone-to-operator communication**, implementing hybrid cryptography to protect against both classical and future quantum computer attacks.

## 🎯 Features

- **🔐 Hybrid Post-Quantum Cryptography**: Combines X448 elliptic curve with CRYSTALS-Kyber for defense-in-depth
- **✍️ Post-Quantum Signatures**: CRYSTALS-Dilithium for message authentication
- **🔒 Authenticated Encryption**: ChaCha20-Poly1305 AEAD for confidentiality and integrity
- **📡 Secure Communication Channels**: Session management with replay protection
- **📊 Network Monitoring**: Real-time telemetry and performance metrics
- **🚁 Drone-Ready**: Optimized for resource-constrained environments (Raspberry Pi 5)

## 🏗️ Architecture

```
┌─────────────────────┐
│ Ground Station      │
│ Operator            │
└──────────┬──────────┘
           │
           │ Encrypted & Authenticated
           │ (Hybrid PQC + Signatures)
           │
┌──────────▼──────────┐
│ Cryptographic Layer │
│ • X448 + Kyber      │
│ • Dilithium Sigs    │
│ • ChaCha20-Poly1305 │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Drone (UAV)         │
│ Flight Control      │
└─────────────────────┘
```

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Testing](#-testing)
- [Benchmarks](#-benchmarks)
- [Documentation](#-documentation)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Prerequisites

**System Requirements:**
- Python 3.9 or higher
- CMake 3.12+
- Ninja build system
- OpenSSL development headers
- Git

**Supported Platforms:**
- Linux (x86_64, ARM64/aarch64)
- macOS
- Windows (WSL recommended)

### 1. Install System Dependencies

#### Ubuntu/Debian/Kali:
```bash
sudo apt-get update
sudo apt-get install -y cmake ninja-build libssl-dev git python3-venv
```

#### macOS:
```bash
brew install cmake ninja openssl
```

### 2. Build and Install liboqs

```bash
# Clone liboqs library
git clone --depth 1 --branch 0.14.0 https://github.com/open-quantum-safe/liboqs.git /tmp/liboqs

# Build
cd /tmp/liboqs
mkdir -p build && cd build
cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr/local -DBUILD_SHARED_LIBS=ON ..
ninja

# Install
sudo ninja install
sudo ldconfig  # Linux only
```

### 3. Install Python Package

```bash
# Clone this repository
git clone https://github.com/Mr-Beck0708/Drone_Communication.git
cd Drone_Communication

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## ⚡ Quick Start

### Basic Encryption Example

```python
from src.crypto import ChaCha20Poly1305Cipher

# Create cipher
cipher = ChaCha20Poly1305Cipher()

# Encrypt message
plaintext = b"Secret drone command: RETURN_TO_BASE"
nonce, ciphertext = cipher.encrypt(plaintext)

# Decrypt message
decrypted = cipher.decrypt(nonce, ciphertext)
print(decrypted.decode())  # "Secret drone command: RETURN_TO_BASE"
```

### Hybrid Key Exchange

```python
from src.crypto import HybridKeyExchange

# Operator and Drone create key exchange objects
operator = HybridKeyExchange()
drone = HybridKeyExchange()

# Generate keypairs
op_x448_pk, op_kyber_pk = operator.generate_keypair()
dr_x448_pk, dr_kyber_pk = drone.generate_keypair()

# Operator initiates exchange
kyber_ct, operator_secret = operator.initiate_exchange(dr_x448_pk, dr_kyber_pk)

# Drone completes exchange
drone_secret = drone.complete_exchange(op_x448_pk, kyber_ct)

# Both now share the same secret
assert operator_secret == drone_secret  # ✓ Success!
```

### Complete Operator-Drone Demo

```bash
# Run the full demonstration
python examples/operator_drone_demo.py
```

This demonstrates:
- Key generation and exchange
- Secure session establishment
- Command transmission with signatures
- Telemetry collection
- Network monitoring

## 📚 Usage Examples

### Digital Signatures

```python
from src.crypto import DilithiumSignature

# Create signature object
sig = DilithiumSignature()
public_key = sig.generate_keypair()

# Sign a message
message = b"Drone status: Battery 85%, Altitude 100m"
signature = sig.sign(message)

# Verify signature
is_valid = sig.verify(message, signature, public_key)
print(f"Signature valid: {is_valid}")  # True
```

### Secure Communication Channel

```python
from src.crypto import ChaCha20Poly1305Cipher, DilithiumSignature
from src.communication import SecureChannel

# Setup
shared_secret = b"0" * 32  # In real use, from key exchange
signing_key = DilithiumSignature()
signing_key.generate_keypair()

# Create secure channel
channel = SecureChannel(shared_secret, signing_key)

# Send encrypted and signed message
encrypted_msg = channel.send(b"Execute landing sequence", sign=True)

# Receive and verify
plaintext = channel.receive(encrypted_msg, signing_key.public_key)
```

### Session Management

```python
from src.communication import Session

# Create session
session = Session("drone-001-session")

# Start handshake
session.start_handshake()

# Complete handshake
shared_secret = b"..." # from key exchange
session.complete_handshake(shared_secret, "operator-001")

# Check session status
print(session.is_active())  # True
print(session.get_session_info())
```

## 🧪 Testing

Run the complete test suite:

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test files
pytest tests/test_crypto.py -v
pytest tests/test_communication.py -v
pytest tests/test_integration.py -v
```

**Test Coverage:**
- ✅ Cryptographic primitives (X448, Kyber, Dilithium, ChaCha20-Poly1305)
- ✅ Hybrid key exchange
- ✅ Secure channels and sessions
- ✅ Network monitoring and telemetry
- ✅ End-to-end integration tests

## ⚡ Benchmarks

Measure performance on your system:

```bash
# Encryption and signature performance
python benchmarks/bench_encryption.py

# Key exchange performance
python benchmarks/bench_key_exchange.py

# Network layer performance
python benchmarks/bench_network.py
```

**Expected Performance** (Raspberry Pi 5, ARM Cortex-A76):
- **ChaCha20-Poly1305**: ~50-200 MB/s throughput
- **Dilithium Sign**: ~1-2 ms
- **Dilithium Verify**: ~1-2 ms
- **Hybrid Key Exchange**: ~10-20 ms
- **Kyber Encapsulation**: ~0.5-1 ms

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/architecture.md)**: System design and security architecture
- **[API Reference](docs/api_reference.md)**: Detailed API documentation
- **[Deployment Guide](docs/deployment_guide.md)**: Production deployment instructions

## 🔒 Security

### Cryptographic Algorithms

| Component | Algorithm | Security Level | Purpose |
|-----------|-----------|---------------|---------|
| Key Exchange (Classical) | X448 | 224-bit | Current protection |
| Key Exchange (PQC) | CRYSTALS-Kyber768 | NIST Level 3 | Quantum resistance |
| Signatures | CRYSTALS-Dilithium3 | NIST Level 3 | Authentication |
| Encryption | ChaCha20-Poly1305 | 256-bit | Confidentiality & integrity |

### Security Properties

✅ **Confidentiality**: All messages encrypted with ChaCha20-Poly1305  
✅ **Integrity**: Poly1305 MAC prevents tampering  
✅ **Authentication**: Dilithium signatures verify sender identity  
✅ **Forward Secrecy**: New session keys for each connection  
✅ **Quantum Resistance**: Kyber and Dilithium protect against quantum attacks  
✅ **Replay Protection**: Message counters prevent replay attacks  

### Security Considerations

⚠️ **This is research/educational code**
- Conduct security audit before production use
- Implement proper key management
- Use secure random number generation
- Follow deployment best practices (see [Deployment Guide](docs/deployment_guide.md))

### Reporting Security Issues

Please report security vulnerabilities to: **[security contact needed]**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run code formatters
black src/ tests/ examples/ benchmarks/
flake8 src/ tests/

# Run type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Open Quantum Safe](https://openquantumsafe.org/)** for liboqs library
- **NIST** for standardizing post-quantum cryptography
- **Cryptography** and **PyCryptodome** Python libraries

## 📞 Contact

- **GitHub**: [Mr-Beck0708/Drone_Communication](https://github.com/Mr-Beck0708/Drone_Communication)
- **Issues**: [Report bugs or request features](https://github.com/Mr-Beck0708/Drone_Communication/issues)

---

**Built with ❤️ for secure drone communication**