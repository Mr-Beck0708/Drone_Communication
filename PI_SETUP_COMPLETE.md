# Raspberry Pi Drone Server - Setup Complete! ✅

## Your Configuration

**Raspberry Pi (Drone Server)**:
- IP Address: `192.168.29.123`
- Port: `8443`
- Role: SERVER (waits for control station to connect)

---

## How to Run

### On Raspberry Pi (Drone):

```bash
cd ~/Documents/Project/Drone_Communication

# Option 1: Use quick run script
./run_drone.sh

# Option 2: Manual command
source venv/bin/activate
python3 drone_app.py
```

Expected output:
```
=== Drone Application (SERVER MODE) ===
Drone ID: DRONE-RASPI-01
Listening on: 0.0.0.0:8443
WiFi Scanner: nmcli
========================================

📡 Drone Server listening on 0.0.0.0:8443
   Drone IP: Use this in control station config
   Waiting for control station connection...
```

---

### On Laptop (Control Station):

```bash
cd ~/Documents/Project/Drone_Communication
source venv/bin/activate

# Connect to your Pi
python3 control_station_app.py --host 192.168.29.123
```

---

## What Data Will Be Shared

The drone (Pi) will scan for WiFi networks and send:
- **SSID** (network names)
- **Signal Strength** (dBm)
- **Encryption Type** (WPA2, WPA3, Open)
- **BSSID** (MAC addresses)
- **Channel** and **Frequency**

All data is:
- ✅ **Encrypted** with ChaCha20-Poly1305
- ✅ **Signed** with Dilithium (post-quantum)
- ✅ **Transmitted** over your local network

---

## Network Architecture

```
┌─────────────────────────────┐
│  Raspberry Pi (DRONE)       │
│  192.168.29.123:8443        │
│  ├─ WiFi Scanner            │
│  ├─ TCP Server              │
│  └─ Sends encrypted data  ──┼───┐
└─────────────────────────────┘   │
                                  │ Encrypted
                                  │ Network Data
                                  │
┌─────────────────────────────┐   │
│  Laptop (CONTROL STATION)   │   │
│  192.168.29.XXX             │   │
│  ├─ TCP Client              │ ◄─┘
│  ├─ Receives & decrypts     │
│  └─ Displays network table  │
└─────────────────────────────┘
```

---

## Verifications Completed ✅

- ✅ WiFi Scanner: Working (found 4 networks)
- ✅ Cryptography: Post-quantum keys generated
- ✅ Dependencies: All installed
- ✅ Configuration: Updated for server mode
- ✅ Scripts: Executable and ready

---

## Quick Commands

### Start Drone Server:
```bash
./run_drone.sh
```

### Test Setup:
```bash
python3 test_drone_setup.py
```

### View Configuration:
```bash
cat config/drone_config.json
```

---

## Troubleshooting

**Problem**: "Permission denied" for WiFi scanning

**Solution**: NetworkManager should work without sudo. If issues persist:
```bash
sudo python3 drone_app.py
```

**Problem**: Connection refused from laptop

**Solution**: Check firewall on Pi:
```bash
sudo ufw allow 8443/tcp
# Or disable: sudo ufw disable
```

---

## Next Steps

1. ✅ **Pi Setup Complete** - Already done!
2. 📱 **Run Drone**: `./run_drone.sh`
3. 💻 **On Laptop**: Install dependencies and run control station
4. 🎯 **Demo**: Use for professor presentation

Your Raspberry Pi is  ready to act as a drone server! 🚁🔐
