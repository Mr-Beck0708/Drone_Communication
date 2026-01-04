#!/bin/bash
# Setup script for Raspberry Pi
# Run this ON the Raspberry Pi after deploying files

set -e

echo "========================================"
echo "Raspberry Pi Drone Setup"
echo "========================================"
echo ""

# Check if running on Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Update system
echo "[1/7] Updating system packages..."
sudo apt-get update

# Step 2: Install system dependencies
echo ""
echo "[2/7] Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    cmake \
    ninja-build \
    libssl-dev \
    git \
    network-manager \
    wireless-tools \
    net-tools

# Step 3: Check if liboqs is installed
echo ""
echo "[3/7] Checking for liboqs..."
if ! ldconfig -p | grep -q liboqs; then
    echo "liboqs not found. Installing..."
    
    # Build and install liboqs
    cd /tmp
    if [ ! -d "liboqs" ]; then
        git clone --depth 1 --branch 0.14.0 https://github.com/open-quantum-safe/liboqs.git
    fi
    
    cd liboqs
    mkdir -p build && cd build
    cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr/local -DBUILD_SHARED_LIBS=ON ..
    ninja
    sudo ninja install
    sudo ldconfig
    
    echo "✓ liboqs installed"
else
    echo "✓ liboqs already installed"
fi

# Step 4: Create Python virtual environment
echo ""
echo "[4/7] Creating Python virtual environment..."
cd $(dirname "$0")
python3 -m venv venv
source venv/bin/activate

# Step 5: Install Python dependencies
echo ""
echo "[5/7] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .

# Step 6: Test WiFi scanner
echo ""
echo "[6/7] Testing WiFi scanner..."
echo "Available WiFi tools:"
command -v nmcli && echo "  ✓ nmcli found" || echo "  ✗ nmcli not found"
command -v iwlist && echo "  ✓ iwlist found" || echo "  ✗ iwlist not found"

# Test scan (non-root)
echo ""
echo "Testing WiFi scan..."
python3 -c "from src.utils.wifi_scanner import WiFiScanner; s = WiFiScanner(); print(f'Scanner ready: {s.scan_tool}')"

# Step 7: Configuration
echo ""
echo "[7/7] Configuration..."
echo ""
echo "========================================"
echo "✓ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Update configuration file:"
echo "   nano config/drone_config.json"
echo "   # Change 'control_station_host' to your laptop's IP address"
echo ""
echo "3. Find your laptop's IP:"
echo "   # On your laptop, run: ip addr"
echo ""
echo "4. Run the drone application:"
echo "   python3 drone_app.py --host <LAPTOP_IP>"
echo ""
echo "   Or use config file:"
echo "   python3 drone_app.py"
echo ""
echo "Enjoy secure drone communication! 🚁🔐"
echo ""
