# Cross-Network Setup Guide

This guide helps you connect your Raspberry Pi (drone) and Laptop (control station) when they're on **different networks**.

---

## Method 1: Mobile Hotspot (Recommended for Demos) ⭐

**Best for**: Demonstrations, testing, portability

### **Step-by-Step:**

#### 1. **Enable Hotspot on Your Phone**
- **Android**: Settings → Network & Internet → Hotspot & Tethering → WiFi Hotspot
- **iPhone**: Settings → Personal Hotspot → Toggle ON

Set a name (e.g., `MyDrone_Demo`) and password.

#### 2. **Connect Raspberry Pi to Hotspot**

**Via GUI** (if you have monitor):
- Click WiFi icon → Select your hotspot → Enter password

**Via Command Line** (SSH):
```bash
# On Raspberry Pi
sudo nmcli device wifi connect "MyDrone_Demo" password "your_password"
```

Check connection:
```bash
hostname -I
# Note the new IP (e.g., 192.168.43.123)
```

#### 3. **Connect Laptop to Same Hotspot**
Connect your laptop to the same phone hotspot.

Check your laptop IP:
```bash
ip addr show | grep "inet "
# You should be on same subnet (e.g., 192.168.43.xxx)
```

#### 4. **Update Control Station Config**

Edit the run script or use command line:
```bash
# On laptop
python3 control_station_app.py --host <NEW_PI_IP>
# Example: python3 control_station_app.py --host 192.168.43.123
```

Or update `config/control_station_config.json`:
```json
{
  "network": {
    "drone_host": "192.168.43.123"
  }
}
```

#### 5. **Test Connection**
```bash
# From laptop, ping the Pi
ping 192.168.43.123

# If successful, run the applications
# On Pi:
./run_drone.sh

# On Laptop:
python3 control_station_app.py --host 192.168.43.123
```

✅ **Advantages:**
- Simple and fast setup
- Portable (works anywhere)
- No router configuration needed
- Perfect for demos

❌ **Disadvantages:**
- Uses phone battery/data
- Phone must stay on during demo

---

## Method 2: Port Forwarding (Remote Access)

**Best for**: Permanent remote access, Pi at home

### **Requirements:**
- Raspberry Pi with static local IP
- Access to router admin panel
- Router with port forwarding support

### **Setup:**

#### 1. **Give Pi a Static IP**

On Raspberry Pi:
```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add at the end (adjust to your network):
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

Reboot:
```bash
sudo reboot
```

#### 2. **Configure Router Port Forwarding**

1. Access router admin (usually `192.168.1.1` or `192.168.0.1`)
2. Find "Port Forwarding" or "Virtual Server" section
3. Add rule:
   - **External Port**: 8443
   - **Internal IP**: 192.168.1.100 (Pi's IP)
   - **Internal Port**: 8443
   - **Protocol**: TCP

#### 3. **Find Your Public IP**

On Raspberry Pi:
```bash
curl ifconfig.me
# Returns something like: 203.0.113.45
```

#### 4. **Connect from Laptop**

From anywhere (different network):
```bash
python3 control_station_app.py --host <PUBLIC_IP>
# Example: python3 control_station_app.py --host 203.0.113.45
```

#### 5. **Security Considerations** ⚠️

**Add firewall rules on Pi:**
```bash
# Allow only specific IP (your laptop)
sudo ufw allow from <LAPTOP_PUBLIC_IP> to any port 8443

# Or allow all (less secure)
sudo ufw allow 8443/tcp
sudo ufw enable
```

**Better: Use SSH Tunnel:**
```bash
# On laptop, create SSH tunnel
ssh -L 8443:localhost:8443 pi@<PUBLIC_IP>

# Then connect to localhost
python3 control_station_app.py --host localhost
```

✅ **Advantages:**
- Access from anywhere
- Pi can be at home, laptop anywhere

❌ **Disadvantages:**
- Security risk (exposed to internet)
- Requires router access
- Dynamic IP may change
- Not recommended without VPN/SSH tunnel

---

## Method 3: VPN (Most Secure) 🔒

**Best for**: Long-term remote access, maximum security

### **Option A: Tailscale** (Easiest)

#### 1. **Install Tailscale**

**On Raspberry Pi:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Follow the URL to authenticate
```

**On Laptop:**
Download from https://tailscale.com/download

#### 2. **Find Tailscale IPs**

**On Pi:**
```bash
tailscale ip -4
# Example: 100.101.102.103
```

#### 3. **Connect**

```bash
# On laptop
python3 control_station_app.py --host 100.101.102.103
```

✅ **Advantages:**
- Extremely secure (encrypted mesh network)
- Easy setup
- Works across any network
- No port forwarding needed
- No public IP exposure

❌ **Disadvantages:**
- Requires Tailscale account
- Both devices need Tailscale installed

---

### **Option B: WireGuard VPN**

More complex but flexible. See: https://www.wireguard.com/install/

---

## Quick Comparison Table

| Method | Setup Time | Security | Works Remotely | Best For |
|--------|-----------|----------|----------------|----------|
| **Mobile Hotspot** | 5 min | ⭐⭐⭐ (Local) | ❌ No | Demos, Testing |
| **Port Forwarding** | 20 min | ⭐ (Risky) | ✅ Yes | Quick remote access |
| **VPN (Tailscale)** | 10 min | ⭐⭐⭐⭐⭐ | ✅ Yes | Production, Security |

---

## Recommendation for Your Demo

**Use Mobile Hotspot!** 📱

Why:
- ✅ Quick setup (5 minutes)
- ✅ No network admin needed
- ✅ Works in any location
- ✅ Secure (local connection only)
- ✅ Perfect for professor demonstration

**Before Demo Day:**
1. Test with hotspot once
2. Note the Pi's hotspot IP
3. Update your demo script with that IP
4. Bring phone charger to demo! 🔋

---

## Troubleshooting

### Can't connect after switching networks?

```bash
# Check if devices are on same subnet
# Pi:
hostname -I  # e.g., 192.168.43.123

# Laptop:
ip addr show | grep "inet "  # Should be 192.168.43.xxx

# If different subnets, they can't communicate
```

### Firewall blocking?

```bash
# On Pi, temporarily disable to test
sudo ufw disable

# If that works, add rule instead
sudo ufw allow 8443/tcp
sudo ufw enable
```

### Pi keeps disconnecting from hotspot?

```bash
# On Pi, disable power management
sudo iwconfig wlan0 power off
```

---

**Need help with setup? Let me know which method you want to use!** 🚀
