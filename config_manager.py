"""
Configuration Manager for SmartHome System
Handles loading, validating, and accessing configuration settings.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages configuration settings for the SmartHome system."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()
        self._setup_logging()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file with fallback to defaults."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self.config = yaml.safe_load(file)
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Configuration file {self.config_path} not found. Using defaults.")
                self._create_default_config()
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing configuration file: {e}")
            self._create_default_config()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration if file is missing or invalid."""
        self.config = {
            'voice': {
                'rate': 160,
                'voice_index': 16,
                'volume': 1.0
            },
            'camera': {
                'source': 0,
                'framerate': 2,
                'width': 500,
                'detection_confidence': 0.8
            },
            'smart_lights': {
                'kasa_host': '192.168.12.238',
                'kasa_port': 9999,
                'default_brightness': 80,
                'colors': {
                    'red': [0, 100, 80],
                    'green': [123, 86, 80],
                    'blue': [245, 84, 70],
                    'white': [0, 0, 100]
                }
            },
            'weather': {
                'api_url': 'https://api.meteomatics.com',
                'location': {
                    'latitude': 41.8781,
                    'longitude': -87.6298,
                    'city': 'Chicago'
                },
                'cache_duration': 300,
                'use_mock_data': True
            },
            'facial_recognition': {
                'encodings_file': 'facial_recognition/encodings.pickle',
                'tolerance': 0.6,
                'detection_interval': 1.0
            },
            'music': {
                'default_file': 'music.mp3',
                'player': 'mpg123',
                'volume': 80
            },
            'system': {
                'log_level': 'INFO',
                'log_file': 'smartHome.log',
                'max_users': 5,
                'session_timeout': 3600
            },
            'hand_gestures': {
                'enabled': False,
                'detection_confidence': 0.8,
                'max_hands': 1
            }
        }
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = self.get('system.log_level', 'INFO')
        log_file = self.get('system.log_file', 'smartHome.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'voice.rate')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            self.logger.warning(f"Configuration key '{key}' not found, using default: {default}")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'voice.rate')
            value: Value to set
        """
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
        except Exception as e:
            self.logger.error(f"Error setting configuration key '{key}': {e}")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def validate_config(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate required sections
            required_sections = ['voice', 'camera', 'smart_lights', 'weather', 
                               'facial_recognition', 'music', 'system']
            
            for section in required_sections:
                if section not in self.config:
                    self.logger.error(f"Missing required configuration section: {section}")
                    return False
            
            # Validate specific values
            if not isinstance(self.get('voice.rate'), (int, float)):
                self.logger.error("Voice rate must be a number")
                return False
            
            if not isinstance(self.get('camera.source'), int):
                self.logger.error("Camera source must be an integer")
                return False
            
            # Validate file paths
            encodings_file = self.get('facial_recognition.encodings_file')
            if not os.path.exists(encodings_file):
                self.logger.warning(f"Facial recognition encodings file not found: {encodings_file}")
            
            self.logger.info("Configuration validation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice configuration settings."""
        return {
            'rate': self.get('voice.rate', 160),
            'voice_index': self.get('voice.voice_index', 16),
            'volume': self.get('voice.volume', 1.0)
        }
    
    def get_camera_settings(self) -> Dict[str, Any]:
        """Get camera configuration settings."""
        return {
            'source': self.get('camera.source', 0),
            'framerate': self.get('camera.framerate', 2),
            'width': self.get('camera.width', 500),
            'detection_confidence': self.get('camera.detection_confidence', 0.8)
        }
    
    def get_smart_light_settings(self) -> Dict[str, Any]:
        """Get smart light configuration settings."""
        return {
            'kasa_host': self.get('smart_lights.kasa_host', '192.168.12.238'),
            'kasa_port': self.get('smart_lights.kasa_port', 9999),
            'default_brightness': self.get('smart_lights.default_brightness', 80),
            'colors': self.get('smart_lights.colors', {})
        }
    
    def get_weather_settings(self) -> Dict[str, Any]:
        """Get weather configuration settings."""
        return {
            'api_url': self.get('weather.api_url', 'https://api.meteomatics.com'),
            'location': self.get('weather.location', {}),
            'cache_duration': self.get('weather.cache_duration', 300),
            'use_mock_data': self.get('weather.use_mock_data', True)
        }


# Global configuration instance
config = ConfigManager() 