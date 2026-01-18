#!/usr/bin/env python3
"""
Web Dashboard for Control Station
Provides a professional Wireshark-style web interface for viewing WiFi network data
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'drone_dashboard_secret_key_change_in_production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global data storage
class DashboardData:
    def __init__(self):
        self.latest_scan: Optional[Dict] = None
        self.scan_history: List[Dict] = []
        self.statistics: Dict = {
            "total_scans": 0,
            "total_networks_seen": 0,
            "avg_signal": 0,
            "strongest_network": None,
            "weakest_network": None
        }
        self.connected_clients = 0
        self.drone_connected = False
        self.drone_id = "Unknown"
        
    def update_scan(self, scan_data: Dict):
        """Update with new scan data."""
        self.latest_scan = scan_data
        self.scan_history.append(scan_data)
        
        # Keep last 100 scans
        if len(self.scan_history) > 100:
            self.scan_history.pop(0)
        
        self._update_statistics()
    
    def _update_statistics(self):
        """Calculate statistics from scan data."""
        if not self.latest_scan:
            return
        
        self.statistics["total_scans"] += 1
        
        networks = self.latest_scan.get("networks", [])
        if not networks:
            return
        
        self.statistics["total_networks_seen"] = len(set(
            n["ssid"] for scan in self.scan_history 
            for n in scan.get("networks", [])
        ))
        
        # Average signal
        signals = [n.get("signal_strength", -100) for n in networks]
        if signals:
            self.statistics["avg_signal"] = sum(signals) / len(signals)
        
        # Strongest/weakest
        strongest = max(networks, key=lambda n: n.get("signal_strength", -100))
        weakest = min(networks, key=lambda n: n.get("signal_strength", -100))
        
        self.statistics["strongest_network"] = {
            "ssid": strongest.get("ssid"),
            "signal": strongest.get("signal_strength")
        }
        self.statistics["weakest_network"] = {
            "ssid": weakest.get("ssid"),
            "signal": weakest.get("signal_strength")
        }

dashboard_data = DashboardData()

# Routes
@app.route('/')
def index():
    """Serve main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get connection status."""
    return jsonify({
        "drone_connected": dashboard_data.drone_connected,
        "drone_id": dashboard_data.drone_id,
        "connected_clients": dashboard_data.connected_clients,
        "total_scans": dashboard_data.statistics["total_scans"]
    })

@app.route('/api/networks')
def get_networks():
    """Get latest network scan data."""
    if dashboard_data.latest_scan:
        return jsonify(dashboard_data.latest_scan)
    return jsonify({"networks": [], "total_networks": 0})

@app.route('/api/statistics')
def get_statistics():
    """Get network statistics."""
    return jsonify(dashboard_data.statistics)

@app.route('/api/history')
def get_history():
    """Get scan history."""
    limit = request.args.get('limit', 10, type=int)
    return jsonify(dashboard_data.scan_history[-limit:])

@app.route('/api/export')
def export_data():
    """Export data as JSON."""
    export = {
        "latest_scan": dashboard_data.latest_scan,
        "statistics": dashboard_data.statistics,
        "history": dashboard_data.scan_history[-50:]  # Last 50 scans
    }
    return jsonify(export)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    dashboard_data.connected_clients += 1
    emit('connection_response', {
        'status': 'connected',
        'message': 'Connected to dashboard'
    })
    print(f"Client connected. Total clients: {dashboard_data.connected_clients}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    dashboard_data.connected_clients -= 1
    print(f"Client disconnected. Total clients: {dashboard_data.connected_clients}")

@socketio.on('request_update')
def handle_update_request():
    """Client requests current data."""
    if dashboard_data.latest_scan:
        emit('scan_update', dashboard_data.latest_scan)
    emit('stats_update', dashboard_data.statistics)

# Helper function to broadcast updates
def broadcast_scan_update(scan_data: Dict):
    """Broadcast new scan data to all connected clients."""
    dashboard_data.update_scan(scan_data)
    socketio.emit('scan_update', scan_data)
    socketio.emit('stats_update', dashboard_data.statistics)

def broadcast_drone_status(connected: bool, drone_id: str = "Unknown"):
    """Broadcast drone connection status."""
    dashboard_data.drone_connected = connected
    dashboard_data.drone_id = drone_id
    socketio.emit('drone_status', {
        'connected': connected,
        'drone_id': drone_id
    })

def start_dashboard(control_station_obj, host='0.0.0.0', port=5000):
    """
    Start the web dashboard.
    
    Args:
        control_station_obj: ControlStationApplication instance
        host: Host to bind to (default: 0.0.0.0 for all interfaces)
        port: Port to bind to (default: 5000)
    """
    # Set up callback for scan data
    original_handle_scan_data = control_station_obj._handle_scan_data
    
    def enhanced_handle_scan_data(data: dict):
        """Enhanced scan data handler that also broadcasts to web clients."""
        # Call original handler
        original_handle_scan_data(data)
        
        # Broadcast to web dashboard
        if control_station_obj.latest_scan:
            broadcast_scan_update(control_station_obj.latest_scan)
    
    # Replace handler
    control_station_obj._handle_scan_data = enhanced_handle_scan_data
    
    # Broadcast drone status
    broadcast_drone_status(True, control_station_obj.config.get("operator_id", "OP-001"))
    
    print(f"\n{'='*80}")
    print(f"🌐 Web Dashboard Starting")
    print(f"{'='*80}")
    print(f"URL:  http://localhost:{port}")
    print(f"      http://{host}:{port}  (network access)")
    print(f"\nOpen this URL in your browser to view the dashboard")
    print(f"{'='*80}\n")
    
    # Start Flask in a separate thread
    def run_flask():
        socketio.run(app, host=host, port=port, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    return app, socketio

if __name__ == "__main__":
    # Standalone mode for testing
    print("Running dashboard in standalone mode...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
