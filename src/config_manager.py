"""
Configuration Manager
Handles loading and managing system configuration from YAML file.
"""

import yaml
import os
from typing import Dict, Any, List


class ConfigManager:
    """Manages system configuration."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def reload(self):
        """Reload configuration from file."""
        self.config = self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation).
        
        Args:
            key: Configuration key (e.g., 'detection.method')
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
    
    def get_cameras(self) -> List[Dict[str, Any]]:
        """Get list of configured cameras."""
        return self.config.get('cameras', [])
    
    def get_enabled_cameras(self) -> List[Dict[str, Any]]:
        """Get list of enabled cameras only."""
        return [cam for cam in self.get_cameras() if cam.get('enabled', False)]
    
    def get_absence_timeout(self) -> int:
        """Get absence timeout in seconds."""
        return self.get('tracking.absence_timeout', 1200)
    
    def get_presence_buffer(self) -> int:
        """Get presence buffer in seconds."""
        return self.get('tracking.presence_buffer', 30)
    
    def get_detection_method(self) -> str:
        """Get detection method."""
        return self.get('detection.method', 'face')
    
    def get_alert_settings(self) -> Dict[str, Any]:
        """Get alert configuration."""
        return self.get('alerts', {})
    
    def update(self, key: str, value: Any):
        """
        Update configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: New value
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
