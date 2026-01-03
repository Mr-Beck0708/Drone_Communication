# System Architecture

## Overview

The Drone Communication System implements a hybrid post-quantum cryptographic framework for secure communication between ground station operators and unmanned aerial vehicles (UAVs). The system combines classical and post-quantum cryptographic primitives to ensure both current security and future-proofing against quantum computing threats.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Ground Station Operator                  │
├─────────────────────────────────────────────────────────────┤
│  • Command Interface                                         │
│  • Telemetry Monitoring                                      │
│  • Session Management                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Secure Channel (Encrypted & Signed)
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Cryptographic Layer                             │
├─────────────────────────────────────────────────────────────┤
│  Hybrid Key Exchange:  X448 + CRYSTALS-Kyber               │
│  Digital Signatures:   CRYSTALS-Dilithium                   │
│  Encryption:          ChaCha20-Poly1305                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Network Layer
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Unmanned Aerial Vehicle                     │
├─────────────────────────────────────────────────────────────┤
│  • Flight Control                                            │
│  • Telemetry Collection                                      │
│  • Command Execution                                         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Cryptographic Module (`src/crypto/`)

#### X448 Key Exchange (`x448.py`)
- **Purpose**: Classical elliptic curve Diffie-Hellman key exchange
- **Security Level**: 224-bit classical security
- **Key Size**: 56 bytes (448 bits)
- **Usage**: Provides immediate protection against classical attacks

#### CRYSTALS-Kyber KEM (`kyber.py`)
- **Purpose**: Post-quantum key encapsulation mechanism
- **Security Level**: NIST Level 3 (Kyber768)
- **Resistance**: Quantum computer resistant
- **Usage**: Future-proofs key exchange against quantum attacks

#### CRYSTALS-Dilithium Signatures (`dilithium.py`)
- **Purpose**: Post-quantum digital signatures
- **Security Level**: NIST Level 3 (Dilithium3)
- **Usage**: Authenticates messages and prevents tampering

#### ChaCha20-Poly1305 AEAD (`chacha20poly1305.py`)
- **Purpose**: Authenticated encryption with associated data
- **Features**: Fast, secure, constant-time
- **Usage**: Encrypts all communication payload

#### Hybrid Key Exchange (`hybrid_kex.py`)
- **Purpose**: Combines X448 and Kyber for defense-in-depth
- **Process**:
  1. Perform X448 key exchange
  2. Perform Kyber encapsulation
  3. Combine secrets using SHA-256
- **Security**: Protected against both classical and quantum attacks

### 2. Communication Module (`src/communication/`)

#### Session Management (`session.py`)
- Tracks connection state (initialized, handshake, active, closed)
- Manages session timeouts and expiration
- Stores session metadata and peer information

#### Telemetry Logger (`telemetry.py`)
- Logs all communication events
- Records performance metrics
- Enables post-mission analysis

#### Network Monitor (`network_monitor.py`)
- Tracks network statistics
- Measures latency and packet loss
- Assesses connection quality

#### Secure Channel (`secure_channel.py`)
- Manages encrypted communication
- Implements message counters for replay protection
- Optional digital signatures for authentication

### 3. Utility Module (`src/utils/`)

#### Configuration (`config.py`)
- Centralized configuration management
- JSON-based configuration files
- Support for environment-specific settings

#### Logger (`logger.py`)
- Structured logging using `structlog`
- JSON-formatted logs for easy parsing
- Multiple output handlers

## Security Architecture

### Defense-in-Depth Strategy

1. **Hybrid Key Exchange**: Even if quantum computers break one algorithm, the other protects the communication
2. **Digital Signatures**: Ensures message authenticity and non-repudiation
3. **Authenticated Encryption**: Protects confidentiality and integrity
4. **Session Management**: Limits exposure through timeouts and state tracking

### Security Properties

- **Confidentiality**: All messages encrypted with ChaCha20-Poly1305
- **Integrity**: Poly1305 MAC prevents message tampering
- **Authentication**: Dilithium signatures verify sender identity
- **Forward Secrecy**: New session keys for each connection
- **Quantum Resistance**: Kyber and Dilithium protect against quantum attacks

## Data Flow

### Handshake Process

```
Operator                                  Drone
   │                                        │
   │ 1. Generate X448 + Kyber keypairs      │
   │◄───────────────────────────────────────│
   │                                        │
   │ 2. Exchange public keys                │
   ├───────────────────────────────────────►│
   │                                        │
   │ 3. Perform hybrid key exchange         │
   │    - X448 shared secret                │
   │    - Kyber encapsulated secret         │
   │    - Combine using SHA-256             │
   │◄──────────────────────────────────────►│
   │                                        │
   │ 4. Establish secure session            │
   │    ✓ Shared secret established         │
   │    ✓ Session active                    │
   │                                        │
```

### Message Exchange

```
Operator                                  Drone
   │                                        │
   │ Command (plaintext)                    │
   ├──► Encrypt with ChaCha20-Poly1305     │
   ├──► Sign with Dilithium                │
   ├──► Send encrypted + signature ────────►│
   │                                        │
   │                            Verify signature ◄──┤
   │                            Decrypt message ◄───┤
   │                            Execute command     │
   │                                        │
   │◄──── Send telemetry (encrypted + signed)│
   │                                        │
```

## Performance Considerations

### Optimization Strategies

1. **Pre-computation**: Generate keys during initialization
2. **Batch Processing**: Process multiple messages efficiently
3. **Caching**: Cache frequently used cryptographic objects
4. **Resource Management**: Proper cleanup of sensitive data

### Target Platform: Raspberry Pi 5

- **CPU**: ARM Cortex-A76 (4 cores, 2.4 GHz)
- **Memory**: 8GB RAM
- **Cryptographic Acceleration**: ARM Crypto Extensions support

## Deployment Architecture

```
┌──────────────────────────────────────────────────┐
│            Ground Station (Desktop/Server)        │
│  • More computational resources                  │
│  • Persistent storage for logs                   │
│  • UI for operator                               │
└──────────────────┬───────────────────────────────┘
                   │
                   │ WiFi / Radio Link
                   │
┌──────────────────▼───────────────────────────────┐
│         Drone (Raspberry Pi 5)                   │
│  • Resource-constrained                          │
│  • Real-time requirements                        │
│  • Flight control integration                    │
└──────────────────────────────────────────────────┘
```

## Future Enhancements

1. **Multi-Drone Support**: Manage multiple simultaneous connections
2. **Redundancy**: Backup communication channels
3. **Compression**: Reduce bandwidth usage
4. **Rate Limiting**: Prevent resource exhaustion
5. **Hardware Acceleration**: Utilize crypto accelerators
