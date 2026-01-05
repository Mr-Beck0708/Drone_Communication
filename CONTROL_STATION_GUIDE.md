# Control Station (Laptop) - Quick Start Guide

## 🚀 Running the Control Station

The control station connects to your Raspberry Pi drone and displays WiFi network data.

### **Prerequisites:**
1. Raspberry Pi drone server must be running
2. Both laptop and Pi must be on the same network
3. Dependencies installed (`pip install -r requirements.txt`)

---

## **Option 1: Quick Run Script** (Easiest)

```bash
cd ~/Documents/Project/Drone_Communication
./run_control_station.sh
```

---

## **Option 2: Manual Command**

```bash
cd ~/Documents/Project/Drone_Communication
source venv/bin/activate
python3 control_station_app.py --host 192.168.29.123
```

Replace `192.168.29.123` with your actual Raspberry Pi IP if it changed.

---

## **What You'll See:**

### **Connection Phase:**
```
================================================================================
CONTROL STATION - WiFi Network Intelligence (CLIENT MODE)
================================================================================
Operator ID: OP-001
Connecting to Drone: 192.168.29.123:8443
Post-Quantum Cryptography: ENABLED
  - Hybrid Key Exchange: X448 + Kyber768
  - Signatures: Dilithium3
  - Encryption: ChaCha20-Poly1305
================================================================================

📡 Connecting to Drone at 192.168.29.123:8443...
✓ Connected to drone

✓ Secure connection established with post-quantum cryptography
```

### **Live Network Display:**
```
================================================================================
📡 WiFi Scan Results - 2026-01-05T13:30:00Z
Networks Found: 4 | Scan Duration: 2.3s
================================================================================
SSID                           Signal     Security        Channel   
--------------------------------------------------------------------------------
YourHomeWiFi                   ████ -45   🔒 WPA2        6         
NeighborNetwork                ███  -58   🔐 WPA3        11        
CoffeeShop_Guest               ██   -68   🔓 Open        1         
...
================================================================================
```

The table updates **every 5 seconds** with fresh WiFi scan data from the Raspberry Pi! 📡

---

## **To Stop:**

Press `Ctrl+C` in the terminal

This will:
- Send shutdown command to drone
- Close the encrypted connection
- Clean up resources

---

## **Troubleshooting:**

### **"Connection refused"**
- Check that drone is running on Pi: `./run_drone.sh`
- Verify Pi IP: Run `hostname -I` on the Pi
- Check firewall: `sudo ufw allow 8443/tcp` on Pi

### **"No module named 'oqs'"**
```bash
pip install -r requirements.txt
```

### **"Drone host not specified"**
```bash
python3 control_station_app.py --host <RASPBERRY_PI_IP>
```

---

## **Command Options:**

```bash
# Specify custom drone IP
python3 control_station_app.py --host 192.168.29.123

# Specify custom port
python3 control_station_app.py --host 192.168.29.123 --port 8443

# Use config file
python3 control_station_app.py --config config/control_station_config.json

# Specify operator ID
python3 control_station_app.py --host 192.168.29.123 --operator-id OP-002
```

---

**Your control station is ready to receive encrypted WiFi intelligence!** 🔐💻
