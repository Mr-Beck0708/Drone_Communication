# Deployment Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Deployment on Raspberry Pi 5](#deployment-on-raspberry-pi-5)
5. [Testing](#testing)
6. [Performance Tuning](#performance-tuning)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Raspberry Pi OS)
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM (4GB recommended)
- **Storage**: 500MB available space
- **Network**: WiFi or Ethernet connectivity

### Recommended Hardware

- **Raspberry Pi 5**: 8GB RAM variant
- **Ground Station**: Desktop or laptop with 8GB+ RAM
- **Network**: 802.11ac WiFi or better

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/drone-communication.git
cd drone-communication
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the Package

```bash
python setup.py install
```

### 5. Install liboqs (Post-Quantum Cryptography Library)

#### On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install cmake ninja-build libssl-dev
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr/local ..
ninja
sudo ninja install
```

#### On Raspberry Pi OS:

```bash
sudo apt-get update
sudo apt-get install cmake ninja-build libssl-dev
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr/local ..
ninja
sudo ninja install
```

### 6. Install liboqs-python

```bash
pip install liboqs-python
```

## Configuration

### Default Configuration

The system includes default configuration in `src/utils/config.py`. To customize:

1. Create a configuration file:

```bash
mkdir -p config
cp config/default_config.json config/local_config.json
```

2. Edit `config/local_config.json`:

```json
{
  "crypto": {
    "kyber_variant": "Kyber768",
    "dilithium_variant": "Dilithium3"
  },
  "communication": {
    "session_timeout": 3600,
    "max_message_size": 1048576,
    "retry_attempts": 3
  },
  "network": {
    "host": "0.0.0.0",
    "port": 8443,
    "keepalive_interval": 30
  },
  "logging": {
    "level": "INFO",
    "telemetry_enabled": true,
    "telemetry_file": "telemetry.log"
  }
}
```

### Using Configuration

```python
from src.utils import Config

config = Config("config/local_config.json")
kyber_variant = config.get("crypto.kyber_variant")
```

## Deployment on Raspberry Pi 5

### 1. Prepare Raspberry Pi

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.9+
sudo apt-get install python3-pip python3-venv -y
```

### 2. Transfer Files

```bash
# From your development machine
scp -r drone-communication pi@raspberrypi.local:~/
```

### 3. Install on Raspberry Pi

```bash
ssh pi@raspberrypi.local
cd ~/drone-communication
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py install
```

### 4. Set Up as System Service

Create `/etc/systemd/system/drone-comm.service`:

```ini
[Unit]
Description=Drone Communication Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/drone-communication
Environment="PATH=/home/pi/drone-communication/venv/bin"
ExecStart=/home/pi/drone-communication/venv/bin/python examples/operator_drone_demo.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable drone-comm.service
sudo systemctl start drone-comm.service
```

Check status:

```bash
sudo systemctl status drone-comm.service
```

## Testing

### Run Unit Tests

```bash
# All tests
pytest tests/

# Specific test module
pytest tests/test_crypto.py

# With coverage
pytest --cov=src tests/
```

### Run Integration Tests

```bash
pytest tests/test_integration.py -v
```

### Run Examples

```bash
# Basic demo
python examples/basic_demo.py

# Operator-drone demo
python examples/operator_drone_demo.py
```

### Run Benchmarks

```bash
# Key exchange benchmarks
python benchmarks/bench_key_exchange.py

# Encryption benchmarks
python benchmarks/bench_encryption.py

# Network benchmarks
python benchmarks/bench_network.py
```

## Performance Tuning

### 1. Optimize Cryptographic Operations

For Raspberry Pi 5, enable ARM Crypto Extensions:

```python
# Ensure liboqs is compiled with optimizations
export CFLAGS="-O3 -march=armv8-a+crypto"
```

### 2. Adjust Session Timeout

For battery-powered drones, reduce session timeout:

```json
{
  "communication": {
    "session_timeout": 1800
  }
}
```

### 3. Enable Compression

For bandwidth-constrained environments, consider adding compression (future enhancement).

### 4. Batch Processing

Process multiple messages in batches to reduce overhead:

```python
messages = [msg1, msg2, msg3]
for msg in messages:
    encrypted = channel.send(msg)
```

## Troubleshooting

### Issue: liboqs not found

**Solution:**
```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
# Add to ~/.bashrc for persistence
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
```

### Issue: Import errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall package in development mode
pip install -e .
```

### Issue: Slow performance on Raspberry Pi

**Solution:**
1. Use Kyber512 instead of Kyber768 for faster operation
2. Disable telemetry logging if not needed
3. Reduce session timeout
4. Ensure sufficient cooling (RPi 5 can throttle when hot)

### Issue: Network connectivity issues

**Solution:**
1. Check firewall settings: `sudo ufw status`
2. Verify port availability: `sudo netstat -tulpn | grep 8443`
3. Test network interface: `ifconfig`

### Issue: Memory errors

**Solution:**
```bash
# Increase swap space on Raspberry Pi
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## Security Considerations

### 1. Key Management

- Never commit private keys to version control
- Use secure key storage mechanisms
- Rotate keys periodically

### 2. Network Security

- Use VPN or secure network for ground station communication
- Implement IP whitelisting
- Enable firewall rules

### 3. Access Control

- Restrict file permissions:
```bash
chmod 600 config/local_config.json
chmod 700 logs/
```

### 4. Monitoring

- Regularly review telemetry logs
- Set up alerts for suspicious activity
- Monitor system resources

## Production Deployment Checklist

- [ ] Install all dependencies
- [ ] Configure system settings
- [ ] Set up logging and monitoring
- [ ] Test all cryptographic operations
- [ ] Verify network connectivity
- [ ] Enable system service
- [ ] Configure automatic backups
- [ ] Set up log rotation
- [ ] Document custom configuration
- [ ] Establish incident response plan
- [ ] Schedule regular security audits

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/drone-communication/issues
- Documentation: See `docs/` directory
- Email: your.email@example.com
