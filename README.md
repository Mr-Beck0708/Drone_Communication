# Drone Communication - Post-Quantum Secure Communication System

## Overview
Real-Time Secure Communication and Post-Quantum Authentication in Small Unmanned Systems.

This project implements a hybrid post-quantum cryptographic framework for secure drone-to-operator communication using X448, CRYSTALS-Kyber, CRYSTALS-Dilithium, and ChaCha20-Poly1305.

## Features
- Hybrid key exchange (X448 + CRYSTALS-Kyber)
- Post-quantum digital signatures (CRYSTALS-Dilithium)
- Authenticated encryption (ChaCha20-Poly1305)
- Session management and telemetry logging
- Network monitoring capabilities

## Installation
```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start
See `examples/basic_demo.py` for a basic usage example.

## Documentation
- [Architecture](docs/architecture.md)
- [API Reference](docs/api_reference.md)
- [Deployment Guide](docs/deployment_guide.md)

## License
TBD
