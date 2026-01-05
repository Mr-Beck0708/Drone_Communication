# Web Dashboard - Quick Start Guide

## 🚀 Professional WiFi Intelligence Dashboard

The web dashboard provides a **Wireshark-style interface** for viewing WiFi network data from your Raspberry Pi drone in real-time through your browser.

---

## Features

✅ **Real-Time Updates** - Live WebSocket connection, no page refresh needed  
✅ **Signal Strength Graphs** - Visual charts with Chart.js  
✅ **Advanced Filtering** - Search by SSID, filter by security/signal  
✅ **Statistics Panel** - Total networks, average signal, strongest/weakest  
✅ **Export Data** - Download network data as CSV  
✅ **Dark Theme** - Professional Wireshark-inspired design  
✅ **Responsive** - Works on desktop, tablet, and mobile  

---

## Quick Start

### 1. Start the Drone (Raspberry Pi)

```bash
cd ~/Documents/Project/Drone_Communication
./run_drone.sh
```

### 2. Start the Web Dashboard (Laptop)

```bash
cd ~/Documents/Project/Drone_Communication
./run_web_dashboard.sh
```

**OR manually:**

```bash
source venv/bin/activate
python3 control_station_app.py --host 192.168.29.123 --web --web-port 5000
```

### 3. Open Your Browser

Navigate to:
```
http://localhost:5000
```

Or from any device on the same network:
```
http://<YOUR_LAPTOP_IP>:5000
```

---

## What You'll See

### Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│ 🚁 WiFi Network Intelligence Dashboard              │
│ Status: Drone Connected | Dashboard Connected       │
├─────────────────────────────────────────────────────┤
│ Statistics Panel                                     │
│ [Total: 12] [Avg: -62 dBm] [Strongest: HomeWiFi]   │
├─────────────────────────────────────────────────────┤
│ Filters & Search                                     │
│ [🔍 Search] [Security ▼] [Signal ▼] [💾 Export]    │
├─────────────────────────────────────────────────────┤
│ Live Network Table (Updates every 5 seconds)        │
│ SSID          Signal   Security  Channel  BSSID     │
│ HomeWiFi_5G   ████-45  🔒WPA2    36       AA:BB:... │
│ OfficeNet     ███ -58  🔐WPA3    6        CC:DD:... │
│ ...                                                  │
├─────────────────────────────────────────────────────┤
│ Charts: Signal Distribution | Security Types        │
└─────────────────────────────────────────────────────┘
```

---

## Dashboard Features

### 📊 Statistics Panel
- **Total Networks**: Unique networks detected across all scans
- **Avg Signal**: Average signal strength in dBm
- **Strongest**: Network with best signal
- **Total Scans**: Number of scan cycles completed

### 🔍 Filters
- **Search**: Type SSID name (fuzzy search)
- **Security**: Filter by WPA3, WPA2, WEP, or Open
- **Signal**: Filter by Strong (>-60), Medium (-60 to -75), Weak (<-75)

### 📈 Charts
- **Signal Distribution**: Bar chart showing network count by signal strength
- **Security Types**: Pie chart showing WPA3/WPA2/Open distribution

### 💾 Export
- Click "Export CSV" to download current network list
- File includes SSID, signal, security, channel, BSSID, frequency

---

## Command Line Options

```bash
# Basic web mode
python3 control_station_app.py --host <DRONE_IP> --web

# Custom port
python3 control_station_app.py --host <DRONE_IP> --web --web-port 8080

# Traditional CLI mode (no web)
python3 control_station_app.py --host <DRONE_IP>
```

---

## Troubleshooting

### "Cannot GET /" or blank page
- Check that all files exist:
  - `templates/dashboard.html`
  - `static/css/dashboard.css`
  - `static/js/dashboard.js`
- Restart the application

### "WebSocket disconnected"
- Flask server may have crashed - check terminal for errors
- Reinstall dependencies: `pip install flask flask-socketio flask-cors eventlet`

### No data appearing
- Ensure drone is connected and sending data
- Check browser console (F12) for JavaScript errors
- Verify drone is scanning: check Pi terminal for "WiFi scan completed" messages

### Charts not showing
- Chart.js failed to load - check internet connection (CDN)
- Look for console errors in browser (F12 → Console)

---

## Architecture

```
Browser ←→ Flask Web Server ←→ Control Station ←→ Raspberry Pi Drone
        WebSocket/HTTP        Python Integration      Encrypted Link
```

**Data Flow:**
1. Pi scans WiFi networks
2. Pi encrypts data (ChaCha20-Poly1305)
3. Data sent to control station
4. Control station decrypts data
5. Web server broadcasts to browser via WebSocket
6. Dashboard updates in real-time

---

## Security

- ✅ All drone↔control station data is **post-quantum encrypted**
- ✅ Web dashboard is **local only** by default (localhost:5000)
- ⚠️ To access from other devices, server binds to `0.0.0.0:5000`
- 🔒 For production: Add authentication, HTTPS, firewall rules

---

## Performance

- **Update Frequency**: Every 5 seconds (configurable on drone)
- **Max History**: Last 100 scans stored
- **Browser Requirements**: Modern browser with JavaScript enabled
- **Network**: Works on same WiFi as laptop, or via mobile hotspot

---

## Customization

### Change Update Interval
On Raspberry Pi, edit `config/drone_config.json`:
```json
{
  "wifi_scanner": {
    "scan_interval": 3.0  ← Change to 3 seconds
  }
}
```

### Change Web Port
```bash
python3 control_station_app.py --host <DRONE_IP> --web --web-port 8080
```

### Modify Theme Colors
Edit `static/css/dashboard.css`, change CSS variables:
```css
:root {
    --accent-blue: #4285f4;  ← Your color here
    --bg-primary: #1a1d23;   ← Your background
}
```

---

## Files Structure

```
Drone_Communication/
├── web_dashboard.py           # Flask web server
├── templates/
│   └── dashboard.html         # Main dashboard page
├── static/
│   ├── css/
│   │   └── dashboard.css      # Wireshark-style theme
│   └── js/
│       └── dashboard.js       # Real-time updates & charts
└── run_web_dashboard.sh       # Quick start script
```

---

## Demo for Professors

**Best approach:**
1. Connect both Pi and laptop to same WiFi (or mobile hotspot)
2. Start drone on Pi
3. Start web dashboard on laptop
4. Open browser and project it on screen/TV
5. Show live WiFi networks being detected
6. Demonstrate filters and export
7. Explain post-quantum encryption in footer

**Talk Points:**
- "Real-time data from actual WiFi scanning"
- "All communication is post-quantum encrypted"
- "Professional interface similar to Wireshark"
- "Can filter and export data for analysis"

---

**Enjoy your professional WiFi intelligence dashboard!** 🚁📡🌐
