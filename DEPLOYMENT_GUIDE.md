# Deployment Guide: Raspberry Pi Drone ↔ Laptop Control Station

Complete guide for deploying and running the WiFi scanning drone system.

---

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Raspberry Pi** | Pi 3B+ | Pi 4/5 (2GB+ RAM) |
| **Laptop** | Any with WiFi | Linux laptop |
| **Network** | WiFi or Ethernet | Same WiFi network |
| **SD Card** | 16GB | 32GB+, Class 10 |

### Software Requirements

**Raspberry Pi**:
- Raspberry Pi OS (Bookworm or newer)
- Python 3.9+
- Git, CMake, OpenSSL

**Laptop**:
- Linux (Ubuntu/Debian/Kali recommended)
- Python 3.9+
- All dependencies from `requirements.txt`

---

## Part 1: Laptop Setup (Control Station)

### 1.1 Find Your Laptop's IP Address

On your laptop, run:
```bash
# Method 1: ip command
ip addr show | grep "inet "

# Method 2: hostname command
hostname -I

# Look for an IP like: 192.168.1.XXX or 10.0.0.XXX
```

**Write down this IP address** - you'll need it for the Pi configuration.

### 1.2 Install Dependencies (if not already done)

```bash
cd ~/Documents/Project/Drone_Communication

# Activate virtual environment
source venv/bin/activate

# Verify installation
python3 -c "from src.crypto import HybridKeyExchange; print('✓ Dependencies OK')"
```

### 1.3 Test Control Station Locally

```bash
# Run control station
python3 control_station_app.py --port 8443

# You should see:
# 📡 Control Station listening on 0.0.0.0:8443
# Waiting for drone connection...
```

Press `Ctrl+C` to stop for now.

---

## Part 2: Raspberry Pi Setup (Drone)

### 2.1 Prepare Raspberry Pi

1. **Install Raspberry Pi OS**:
   - Download from https://www.raspberrypi.com/software/
   - Flash to SD card using Raspberry Pi Imager
   - Enable SSH during setup (Recommended)

2. **Boot and Connect**:
   ```bash
   # Connect Pi to your network (WiFi or Ethernet)
   # Find Pi's IP address:
   # Method 1: On Pi directly
   hostname -I
   
   # Method 2: From laptop
   nmap -sn 192.168.1.0/24  # Scan your network
   ```

3. **SSH to Pi** (from your laptop):
   ```bash
   ssh pi@<PI_IP_ADDRESS>
   # Default password: raspberry (change this!)
   ```

### 2.2 Deploy Project to Raspberry Pi

**Option A: Using Deployment Script** (Recommended)

From your laptop:
```bash
cd ~/Documents/Project/Drone_Communication

# Deploy to Pi
./deploy_to_raspi.sh pi@<PI_IP_ADDRESS>

# Example:
# ./deploy_to_raspi.sh pi@192.168.1.50
```

The script will:
- Copy all project files to Pi
- Offer to run setup automatically
- Test the connection

**Option B: Manual Copy**

```bash
# From laptop
rsync -avz --exclude='venv' --exclude='.git' \
  ~/Documents/Project/Drone_Communication/ \
  pi@<PI_IP>:~/Drone_Communication/
```

### 2.3 Run Setup on Raspberry Pi

SSH to Pi and run:
```bash
cd ~/Drone_Communication
chmod +x setup_raspi.sh
./setup_raspi.sh
```

This will:
- Install system dependencies (nmcli, wireless-tools, etc.)
- Build and install liboqs library
- Create Python virtual environment
- Install Python packages
- Test WiFi scanner

**Time required**: 15-30 minutes (liboqs compilation is slow on Pi)

### 2.4 Configure Drone with Your Laptop IP

Edit the configuration file:
```bash
nano config/drone_config.json
```

Change the `control_station_host` to **your laptop's IP**:
```json
{
  "network": {
    "control_station_host": "192.168.1.100",  ← CHANGE THIS
    "port": 8443
  }
}
```

Save and exit (`Ctrl+X`, `Y`, `Enter`)

---

## Part 3: Running the Demonstration

### 3.1 Start Control Station (Laptop)

Open a terminal on your laptop:

```bash
cd ~/Documents/Project/Drone_Communication
source venv/bin/activate

# Start control station
python3 control_station_app.py

# Or with specific port:
# python3 control_station_app.py --port 8443
```

You should see:
```
================================================================================
CONTROL STATION - WiFi Network Intelligence
================================================================================
Operator ID: OP-001
Post-Quantum Cryptography: ENABLED
  - Hybrid Key Exchange: X448 + Kyber768
  - Signatures: Dilithium3
  - Encryption: ChaCha20-Poly1305
================================================================================

📡 Control Station listening on 0.0.0.0:8443
Waiting for drone connection...
```

### 3.2 Start Drone (Raspberry Pi)

In a separate SSH session to Pi:

```bash
cd ~/Drone_Communication
source venv/bin/activate

# Start drone (using config file)
python3 drone_app.py

# OR specify laptop IP via command line:
# python3 drone_app.py --host 192.168.1.100
```

You should see both applications connect and perform key exchange!

### 3.3 Expected Output

**On Laptop (Control Station)**:
```
✓ Drone connected from 192.168.1.50:XXXXX
✓ Secure connection established with post-quantum cryptography

================================================================================
Receiving WiFi scan data from drone...
================================================================================

📡 WiFi Scan Results - 2026-01-04T17:30:00Z
Networks Found: 12 | Scan Duration: 2.3s
================================================================================
SSID                           Signal     Security        Channel   
--------------------------------------------------------------------------------
MyHomeWiFi_5G                  ████ -45   🔒 WPA2        36        
OfficeNetwork                  ███  -58   🔐 WPA3        6         
NeighborWiFi                   ██   -68   🔒 WPA2        11        
CoffeeShop_Guest               █    -75   🔓 Open        1         
...
```

**On Raspberry Pi (Drone)**:
```
=== Drone Application ===
Drone ID: DRONE-RASPI-01
Control Station: 192.168.1.100:8443
WiFi Scanner: nmcli
========================================

✓ Connected and secured with post-quantum cryptography

WiFi scanning started...
```

---

## Part 4: Troubleshooting

### Connection Issues

**Problem**: "Connection refused"

**Solutions**:
1. Check laptop firewall:
   ```bash
   # On laptop
   sudo ufw allow 8443/tcp
   # Or disable firewall temporarily: sudo ufw disable
   ```

2. Verify laptop IP:
   ```bash
   ip addr show
   ```

3. Test network connectivity:
   ```bash
   # From Pi, ping laptop
   ping <LAPTOP_IP>
   ```

### WiFi Scanning Issues

**Problem**: "No WiFi scanning tool found"

**Solution**:
```bash
# On Pi, install NetworkManager
sudo apt-get install network-manager

# Or install wireless-tools
sudo apt-get install wireless-tools
```

**Problem**: Permission denied for scanning

**Solution**:
```bash
# Run with sudo for full access (not recommended for demo)
sudo python3 drone_app.py --host <LAPTOP_IP>

# Or configure sudo-free scanning:
sudo chmod u+s /usr/sbin/iw
```

### Cryptography Issues

**Problem**: "ModuleNotFoundError: No module named 'oqs'"

**Solution**:
```bash
# Reinstall liboqs-python
pip install --force-reinstall liboqs-python
```

**Problem**: liboqs shared library not found

**Solution**:
```bash
 sudo ldconfig
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

---

## Part 5: Stopping the Applications

To stop gracefully:

1. **Control Station**: Press `Ctrl+C` in the laptop terminal
2. **Drone**: Press `Ctrl+C` in the Pi SSH session

Both applications will:
- Stop scanning
- Close secure connections
- Clean up resources

---

## Part 6: Advanced Options

### Run as Background Service

Create systemd service on Pi:

```bash
sudo nano /etc/systemd/system/drone.service
```

Contents:
```ini
[Unit]
Description=Drone WiFi Scanner
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Drone_Communication
ExecStart=/home/pi/Drone_Communication/venv/bin/python3 drone_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable drone.service
sudo systemctl start drone.service
sudo systemctl status drone.service
```

### Change Scan Interval

```bash
# Via command line (not yet implemented)
# Send command from control station

# Via config file
nano config/drone_config.json
# Change "scan_interval": 5.0 to desired seconds
```

### Save Scan Data to File

Edit `config/control_station_config.json`:
```json
{
  "telemetry": {
    "log_to_file": true,
    "log_file": "network_scans.json"
  }
}
```

Scan data will be appended to the file for later analysis.

---

## Network Diagram

```
┌─────────────────────────┐
│  Laptop (Control)       │
│  192.168.1.100:8443     │
│  ├─ control_station_app │
│  └─ Receives & displays │
└────────────┬────────────┘
             │
       WiFi Network
       192.168.1.0/24
             │
┌────────────┴────────────┐
│  Raspberry Pi (Drone)   │
│  192.168.1.50           │
│  ├─ drone_app           │
│  ├─ WiFi scanner        │
│  └─ Encrypts & sends    │
└─────────────────────────┘
```

---

## Quick Reference Commands

### Laptop
```bash
# Find IP
ip addr show | grep "inet "

# Run control station
cd ~/Documents/Project/Drone_Communication
source venv/bin/activate
python3 control_station_app.py
```

### Raspberry Pi
```bash
# Deploy from laptop
./deploy_to_raspi.sh pi@<PI_IP>

# Setup on Pi (first time)
./setup_raspi.sh

# Run drone
cd ~/Drone_Communication
source venv/bin/activate
python3 drone_app.py --host <LAPTOP_IP>
```

---

## Security Notes

- ✅ All data is encrypted with ChaCha20-Poly1305
- ✅ All messages are signed with Dilithium signatures
- ✅ Post-quantum key exchange (X448 + Kyber768)
- ⚠️ This is a demonstration system - production use requires additional hardening
- 🔒 Change default Raspberry Pi password immediately

---

**Need Help?** Check the main [README.md](README.md) or open an issue on GitHub.
