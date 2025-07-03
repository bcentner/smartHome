"""
User Management and Command Logic for SmartHome System
Handles user sessions, command processing, and device control.
"""

import threading
import requests
import subprocess
import logging
import os
from datetime import datetime
import time
from typing import Dict, Any, Optional, List

from error_handler import (
    SmartHomeError, SmartLightError, WeatherError, VoiceError,
    handle_errors, safe_execute
)


class WeatherService:
    """Handles weather data retrieval and caching."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.last_cache_time = {}
    
    @handle_errors
    def get_weather(self, format_type: str) -> str:
        """
        Get weather information for the specified format.
        
        Args:
            format_type: Type of weather data (temp, wind, precip, sunrise, sunset)
            
        Returns:
            Weather information as string
        """
        try:
            weather_settings = self.config.get_weather_settings()
            
            # Check cache first
            cache_key = f"weather_{format_type}"
            if self._is_cache_valid(cache_key, weather_settings['cache_duration']):
                return self.cache[cache_key]
            
            # Use mock data if configured
            if weather_settings['use_mock_data']:
                return self._get_mock_weather(format_type)
            
            # Get real weather data
            return self._get_real_weather(format_type, weather_settings)
            
        except Exception as e:
            raise WeatherError(f"Failed to get weather data: {str(e)}")
    
    def _get_mock_weather(self, format_type: str) -> str:
        """Get mock weather data for testing."""
        mock_data = {
            "temp": "72°F",
            "wind": "8 MPH",
            "precip": "0.1 inches",
            "sunrise": "6:30 AM",
            "sunset": "7:45 PM"
        }
        return mock_data.get(format_type, "Weather data not available")
    
    def _get_real_weather(self, format_type: str, settings: Dict[str, Any]) -> str:
        """Get real weather data from API."""
        try:
            # Map format types to API parameters
            format_mapping = {
                "temp": "t_2m:F",
                "wind": "wind_speed_10m:ms",
                "precip": "precip_24h:mm",
                "sunrise": "sunrise:sql",
                "sunset": "sunset:sql"
            }
            
            if format_type not in format_mapping:
                raise WeatherError(f"Unknown weather format: {format_type}")
            
            api_format = format_mapping[format_type]
            location = settings['location']
            
            # Build API URL
            cur_time = datetime.utcnow()
            formatted_datetime = cur_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            url = f"{settings['api_url']}/{formatted_datetime}/{api_format}/{location['latitude']},{location['longitude']}/html"
            
            # Make API request
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse and cache the response
                weather_data = self._parse_weather_response(response.text, format_type)
                self._cache_weather_data(format_type, weather_data)
                return weather_data
            else:
                raise WeatherError(f"Weather API returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise WeatherError(f"Weather API request failed: {str(e)}")
    
    def _parse_weather_response(self, response_text: str, format_type: str) -> str:
        """Parse weather API response."""
        # This is a simplified parser - in a real implementation, you'd parse the actual response
        return f"Weather data for {format_type}: {response_text[:50]}..."
    
    def _cache_weather_data(self, format_type: str, data: str) -> None:
        """Cache weather data."""
        cache_key = f"weather_{format_type}"
        self.cache[cache_key] = data
        self.last_cache_time[cache_key] = time.time()
    
    def _is_cache_valid(self, cache_key: str, cache_duration: int) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.cache or cache_key not in self.last_cache_time:
            return False
        
        return (time.time() - self.last_cache_time[cache_key]) < cache_duration


class SmartLightController:
    """Handles smart light control operations."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.light_settings = config.get_smart_light_settings()
    
    @handle_errors
    def control_lights(self, action: str, **kwargs) -> bool:
        """
        Control smart lights.
        
        Args:
            action: Action to perform (on, off, brightness, color)
            **kwargs: Additional parameters (brightness, color)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = ["kasa", "--host", self.light_settings['kasa_host']]
            
            if action == "on":
                return self._turn_on_lights(cmd, **kwargs)
            elif action == "off":
                return self._turn_off_lights(cmd)
            else:
                raise SmartLightError(f"Unknown action: {action}")
                
        except Exception as e:
            raise SmartLightError(f"Light control failed: {str(e)}")
    
    def _turn_on_lights(self, cmd: List[str], brightness: Optional[int] = None, 
                       color: Optional[str] = None) -> bool:
        """Turn on lights with optional brightness and color."""
        try:
            # Turn on lights
            result = subprocess.run(cmd + ["on"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise SmartLightError(f"Failed to turn on lights: {result.stderr}")
            
            # Set brightness if specified
            if brightness is not None:
                brightness = max(0, min(100, brightness))  # Clamp to 0-100
                result = subprocess.run(cmd + ["brightness", str(brightness)], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    self.logger.warning(f"Failed to set brightness: {result.stderr}")
            
            # Set color if specified
            if color is not None:
                color_values = self._get_color_values(color)
                if color_values:
                    result = subprocess.run(cmd + ["hsv"] + [str(x) for x in color_values], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode != 0:
                        self.logger.warning(f"Failed to set color: {result.stderr}")
            
            return True
            
        except subprocess.TimeoutExpired:
            raise SmartLightError("Light control command timed out")
        except Exception as e:
            raise SmartLightError(f"Failed to turn on lights: {str(e)}")
    
    def _turn_off_lights(self, cmd: List[str]) -> bool:
        """Turn off lights."""
        try:
            result = subprocess.run(cmd + ["off"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise SmartLightError(f"Failed to turn off lights: {result.stderr}")
            return True
            
        except subprocess.TimeoutExpired:
            raise SmartLightError("Light control command timed out")
        except Exception as e:
            raise SmartLightError(f"Failed to turn off lights: {str(e)}")
    
    def _get_color_values(self, color_name: str) -> Optional[List[int]]:
        """Get HSV color values for a color name."""
        colors = self.light_settings.get('colors', {})
        return colors.get(color_name.lower())


class MusicPlayer:
    """Handles music playback."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.music_settings = config.get('music', {})
    
    @handle_errors
    def play_music(self, file_path: Optional[str] = None) -> bool:
        """
        Play music file.
        
        Args:
            file_path: Path to music file (optional, uses default if not specified)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if file_path is None:
                file_path = self.music_settings.get('default_file', 'music.mp3')
            
            if not os.path.exists(file_path):
                raise SmartHomeError(f"Music file not found: {file_path}", component="music")
            
            player = self.music_settings.get('player', 'mpg123')
            cmd = [player, "-vC", file_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise SmartHomeError(f"Music playback failed: {result.stderr}", component="music")
            
            return True
            
        except subprocess.TimeoutExpired:
            raise SmartHomeError("Music playback timed out", component="music")
        except Exception as e:
            raise SmartHomeError(f"Music playback failed: {str(e)}", component="music")


class Users:
    """Manages user sessions and command processing."""
    
    def __init__(self, engine, config) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.engine = engine
        self._statuses: List[str] = []  # name in list -> logged in
        self.cur_user = ""
        self.thread: Optional[threading.Thread] = None
        self.running = False
        
        # Initialize services
        self.weather_service = WeatherService(config)
        self.light_controller = SmartLightController(config)
        self.music_player = MusicPlayer(config)
    
    def log_in(self, name: str) -> None:
        """Log in a user."""
        try:
            if not self._statuses:
                self.thread = threading.Thread(target=self._command_loop)
                self.thread.daemon = True
                self.thread.start()
                self.running = True
            
            self._statuses.append(name)
            self.cur_user = self._statuses[0]
            self.logger.info(f"User logged in: {name}")
            
        except Exception as e:
            self.logger.error(f"Error logging in user {name}: {e}")
    
    def _command_loop(self) -> None:
        """Main command processing loop."""
        while self.running:
            try:
                if not self._statuses:
                    time.sleep(1)
                    continue
                
                cmd = input(f"Hi {self.cur_user}. What would you like to do? ").lower().strip()
                
                if cmd == "lights":
                    self._handle_lights_command()
                elif cmd == "weather":
                    self._handle_weather_command()
                elif cmd == "music":
                    self._handle_music_command()
                elif cmd == "logout":
                    self._handle_logout_command()
                elif cmd == "help":
                    self._handle_help_command()
                elif cmd == "status":
                    self._handle_status_command()
                else:
                    print("Sorry, I don't currently recognize that command. Type 'help' for available commands.")
                
                time.sleep(1)
                
            except EOFError:
                self.logger.info("Input stream closed, stopping command loop")
                break
            except Exception as e:
                self.logger.error(f"Error in command loop: {e}")
                time.sleep(1)
    
    def _handle_lights_command(self) -> None:
        """Handle smart light commands."""
        try:
            status = input("On or off? ").lower().strip()
            
            if status == "on":
                brightness_input = input("Brightness (0-100, press Enter for default)? ").strip()
                brightness = int(brightness_input) if brightness_input.isdigit() else None
                
                color = input("Color (red, green, blue, white, purple, orange)? ").lower().strip()
                
                success = self.light_controller.control_lights("on", brightness=brightness, color=color)
                if success:
                    print("Lights turned on successfully")
                    self._speak("Lights are now on")
                
            elif status == "off":
                success = self.light_controller.control_lights("off")
                if success:
                    print("Lights turned off successfully")
                    self._speak("Lights are now off")
            else:
                print("Invalid option. Please choose 'on' or 'off'")
                
        except Exception as e:
            self.logger.error(f"Error handling lights command: {e}")
            print("Sorry, there was an error controlling the lights")
    
    def _handle_weather_command(self) -> None:
        """Handle weather commands."""
        try:
            choice = input("Temp, wind, precip, sunrise, or sunset? ").lower().strip()
            
            weather_data = self.weather_service.get_weather(choice)
            print(weather_data)
            self._speak(f"The {choice} is {weather_data}")
            
        except Exception as e:
            self.logger.error(f"Error handling weather command: {e}")
            print("Sorry, there was an error getting weather information")
    
    def _handle_music_command(self) -> None:
        """Handle music commands."""
        try:
            success = self.music_player.play_music()
            if success:
                print("Music started playing")
                self._speak("Music is now playing")
            else:
                print("Failed to play music")
                
        except Exception as e:
            self.logger.error(f"Error handling music command: {e}")
            print("Sorry, there was an error playing music")
    
    def _handle_logout_command(self) -> None:
        """Handle logout command."""
        try:
            if self._statuses:
                user_to_logout = self._statuses.pop(0)
                self._speak(f"Goodbye {user_to_logout}")
                
                if not self._statuses:
                    self.running = False
                    return
                else:
                    self.cur_user = self._statuses[0]
                    self._speak(f"Hello {self.cur_user}")
                    
        except Exception as e:
            self.logger.error(f"Error handling logout command: {e}")
    
    def _handle_help_command(self) -> None:
        """Handle help command."""
        help_text = "Available commands: lights, weather, music, logout, status, help"
        print(help_text)
        self._speak("You can control lights, check weather, play music, or logout")
    
    def _handle_status_command(self) -> None:
        """Handle status command."""
        status_text = f"Current user: {self.cur_user}, Total users: {len(self._statuses)}"
        print(status_text)
        self._speak(f"You are currently logged in as {self.cur_user}")
    
    def _speak(self, text: str) -> None:
        """Speak text using the voice engine."""
        try:
            if self.engine:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
    
    def stop(self) -> None:
        """Stop the user management system."""
        self.running = False
