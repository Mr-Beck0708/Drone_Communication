"""
Network monitoring for connection status and quality metrics.
"""

import time
import psutil
from typing import Dict, List, Optional


class NetworkMonitor:
    """Monitors network connectivity and performance."""
    
    def __init__(self):
        """Initialize network monitor."""
        self.start_time = time.time()
        self.latency_samples: List[float] = []
        self.packet_loss_count = 0
        self.packet_sent_count = 0
    
    def get_network_stats(self) -> Dict[str, any]:
        """
        Get current network statistics.
        
        Returns:
            Dictionary with network stats
        """
        net_io = psutil.net_io_counters()
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errors_in": net_io.errin,
            "errors_out": net_io.errout,
            "drops_in": net_io.dropin,
            "drops_out": net_io.dropout,
        }
    
    def record_latency(self, latency: float):
        """
        Record a latency sample.
        
        Args:
            latency: Latency in seconds
        """
        self.latency_samples.append(latency)
        
        # Keep only last 100 samples
        if len(self.latency_samples) > 100:
            self.latency_samples.pop(0)
    
    def record_packet_sent(self):
        """Record a packet sent."""
        self.packet_sent_count += 1
    
    def record_packet_loss(self):
        """Record a packet loss."""
        self.packet_loss_count += 1
    
    def get_average_latency(self) -> Optional[float]:
        """Get average latency in milliseconds."""
        if not self.latency_samples:
            return None
        return (sum(self.latency_samples) / len(self.latency_samples)) * 1000
    
    def get_packet_loss_rate(self) -> float:
        """Get packet loss rate as percentage."""
        if self.packet_sent_count == 0:
            return 0.0
        return (self.packet_loss_count / self.packet_sent_count) * 100
    
    def get_connection_quality(self) -> str:
        """
        Get connection quality assessment.
        
        Returns:
            Quality rating: 'excellent', 'good', 'fair', 'poor'
        """
        avg_latency = self.get_average_latency()
        loss_rate = self.get_packet_loss_rate()
        
        if avg_latency is None:
            return "unknown"
        
        if avg_latency < 50 and loss_rate < 1:
            return "excellent"
        elif avg_latency < 100 and loss_rate < 3:
            return "good"
        elif avg_latency < 200 and loss_rate < 5:
            return "fair"
        else:
            return "poor"
    
    def get_monitor_summary(self) -> Dict[str, any]:
        """Get monitoring summary."""
        return {
            "uptime_seconds": time.time() - self.start_time,
            "average_latency_ms": self.get_average_latency(),
            "packet_loss_rate": self.get_packet_loss_rate(),
            "connection_quality": self.get_connection_quality(),
            "total_packets_sent": self.packet_sent_count,
            "total_packets_lost": self.packet_loss_count,
        }
