#!/bin/bash
# Quick run script for Control Station with Web Dashboard

echo "================================================"
echo "Control Station - Web Dashboard Mode"
echo "================================================"
echo ""
echo "🌐 Starting professional web interface..."
echo "📊 Features: Real-time graphs, filters, export"
echo ""
echo "Connecting to Drone: 192.168.29.123"
echo "Web URL: http://localhost:5000"
echo ""
echo "================================================"
echo ""

cd "$(dirname "$0")"
source venv/bin/activate
python3 control_station_app.py --host 192.168.29.123 --web --web-port 5000
