#!/bin/bash
# Quick test script for Raspberry Pi Drone Server

echo "================================================"
echo "Testing Drone Server Setup"
echo "================================================"
echo ""
echo "Your Raspberry Pi IP: 192.168.29.123"
echo "Drone will listen on port 8443"
echo ""
echo "On your laptop, run:"
echo "  python3 control_station_app.py --host 192.168.29.123"
echo ""
echo "================================================"
echo "Starting Drone Server..."
echo "================================================"
echo ""

cd "$(dirname "$0")"
source venv/bin/activate
python3 drone_app.py --host 0.0.0.0 --port 8443
