#!/bin/bash
# Quick run script for Control Station (Laptop)

echo "================================================"
echo "Control Station - WiFi Network Intelligence"
echo "================================================"
echo ""
echo "Connecting to Raspberry Pi Drone"
echo "Drone IP: 192.168.29.123"
echo "Port: 8443"
echo ""
echo "================================================"
echo "Starting Control Station..."
echo "================================================"
echo ""

cd "$(dirname "$0")"
source venv/bin/activate
python3 control_station_app.py --host 192.168.29.123 --port 8443
