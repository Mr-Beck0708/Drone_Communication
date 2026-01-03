"""
Configuration management for the drone communication system.
"""

import json
from pathlib import Path
from typing import Any, Dict


class Config:
    """Manages application configuration."""
    
    DEFAULT_CONFIG = {
        "crypto": {
            "kyber_variant": "Kyber768",
            "dilithium_variant": "Dilithium3",
        },
        "communication": {
            "session_timeout": 3600,  # 1 hour
            "max_message_size": 1048576,  # 1 MB
            "retry_attempts": 3,
        },
        "network": {
            "host": "0.0.0.0",
            "port": 8443,
            "keepalive_interval": 30,
        },
        "logging": {
            "level": "INFO",
            "telemetry_enabled": True,
            "telemetry_file": "telemetry.log",
        }
    }
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str):
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to JSON configuration file
        """
        path = Path(config_file)
        if path.exists():
            with open(path, 'r') as f:
                user_config = json.load(f)
                self._merge_config(user_config)
    
    def save_to_file(self, config_file: str):
        """
        Save configuration to JSON file.
        
        Args:
            config_file: Path to output JSON file
        """
        path = Path(config_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Recursively merge user configuration into default config."""
        for key, value in user_config.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'crypto.kyber_variant')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
