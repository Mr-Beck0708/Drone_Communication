"""
Telemetry logging for communication monitoring and analysis.
"""

import time
import json
from pathlib import Path
from typing import Any, Dict


class TelemetryLogger:
    """Logs telemetry data for analysis and monitoring."""
    
    def __init__(self, log_file: str = "telemetry.log"):
        """
        Initialize telemetry logger.
        
        Args:
            log_file: Path to telemetry log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log a telemetry event.
        
        Args:
            event_type: Type of event (e.g., 'handshake', 'message', 'error')
            data: Event data dictionary
        """
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_handshake(self, session_id: str, duration: float, success: bool):
        """Log handshake event."""
        self.log_event("handshake", {
            "session_id": session_id,
            "duration_ms": duration * 1000,
            "success": success
        })
    
    def log_message(self, session_id: str, direction: str, size: int, latency: float = None):
        """
        Log message transmission.
        
        Args:
            session_id: Session identifier
            direction: 'sent' or 'received'
            size: Message size in bytes
            latency: Optional latency in seconds
        """
        data = {
            "session_id": session_id,
            "direction": direction,
            "size_bytes": size
        }
        
        if latency is not None:
            data["latency_ms"] = latency * 1000
        
        self.log_event("message", data)
    
    def log_error(self, session_id: str, error_type: str, error_message: str):
        """Log error event."""
        self.log_event("error", {
            "session_id": session_id,
            "error_type": error_type,
            "error_message": error_message
        })
    
    def log_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None):
        """
        Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            metadata: Additional metadata
        """
        data = {
            "operation": operation,
            "duration_ms": duration * 1000
        }
        
        if metadata:
            data.update(metadata)
        
        self.log_event("performance", data)
