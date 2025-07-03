# SmartHome System

A Python-based smart home automation system that combines facial recognition, voice commands, and home automation features. The system can recognize users, provide voice feedback, control smart lights, check weather, and play music.

## Features

### 🔐 Facial Recognition
- Real-time face detection and recognition
- Automatic user login/logout based on facial recognition
- Voice greetings when recognized users are detected
- Multi-user support with session management

### 🎤 Voice Interface
- Text-to-speech feedback using pyttsx3
- Voice announcements for user recognition
- Voice responses for system commands

### 🏠 Home Automation
- **Smart Light Control**: Control Kasa smart lights via IP address
  - Turn lights on/off
  - Adjust brightness
  - Change colors (red, green, blue, white)
- **Weather Information**: Get real-time weather data
  - Temperature
  - Wind speed
  - Precipitation
  - Sunrise/sunset times
- **Music Player**: Play music files using mpg123

### 🤚 Hand Gesture Recognition (Experimental)
- Finger counting and gesture detection
- Visual feedback for hand gestures
- Configurable gesture responses

## Prerequisites

### Hardware Requirements
- Webcam for facial recognition
- Microphone (optional, for future voice input features)
- Smart lights compatible with Kasa protocol

### Software Requirements
- Python 3.7+
- OpenCV
- Face recognition libraries
- Internet connection for weather API

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smartHome
   ```

2. **Install required Python packages**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install pyttsx3 opencv-python face-recognition imutils requests cvzone PyYAML
   ```

3. **Install system dependencies**
   ```bash
   # For Ubuntu/Debian
   sudo apt-get install mpg123
   
   # For macOS
   brew install mpg123
   
   # For Windows
   # Download mpg123 from https://www.mpg123.de/
   ```

4. **Setup configuration**
   ```bash
   # Copy the example configuration
   cp config.example.yaml config.yaml
   
   # Edit the configuration file with your settings
   nano config.yaml
   ```

## Setup

### 1. Configuration Setup

The system uses a YAML configuration file for all settings:

1. **Copy the example configuration**:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. **Edit the configuration file** with your specific settings:
   - Update smart light IP addresses
   - Set your location coordinates for weather
   - Configure voice settings
   - Adjust camera settings

### 2. Facial Recognition Setup

The system requires pre-trained facial encodings. You need to:

1. Create a `facial_recognition/` directory
2. Add an `encodings.pickle` file with known face encodings
3. Update the `encodings_file` path in your `config.yaml`
4. The system will automatically copy this file to the working directory

**Note**: The `encodings.pickle` file should contain a dictionary with:
- `"encodings"`: List of face encodings
- `"names"`: List of corresponding names

### 3. Smart Light Configuration

Update the smart light settings in your `config.yaml`:
```yaml
smart_lights:
  kasa_host: "192.168.12.238"  # Your light's IP address
  kasa_port: 9999              # Kasa port
  default_brightness: 80       # Default brightness
```

### 4. Weather API (Optional)

The system uses Meteomatics API for weather data. For production use:
- Set `use_mock_data: false` in your config
- Update location coordinates in the weather section
- The system includes caching and error handling for API calls

## Usage

### Starting the System

Run the main driver:
```bash
python driver.py
```

The system will:
1. Initialize the facial recognition system
2. Start the webcam feed
3. Begin monitoring for recognized faces
4. Provide voice feedback when users are detected

### Available Commands

Once logged in, you can use these commands:

- **`lights`** - Control smart lights
  - Choose "on" or "off"
  - Set brightness (0-100)
  - Choose color: red, green, blue, or white

- **`weather`** - Get weather information
  - Choose: temp, wind, precip, sunrise, or sunset

- **`music`** - Play music file (requires `music.mp3` in directory)

- **`logout`** - Log out current user

- **`help`** - Display available commands

### Example Usage

```
Hi. What would you like to do? lights
On or off? on
Brightness? 80
Color? blue
```

## File Structure

```
smartHome/
├── driver.py                  # Main application driver
├── logic.py                   # User management and command logic
├── facial_req.py              # Facial recognition system
├── hand_req.py                # Hand gesture recognition (experimental)
├── config_manager.py          # Configuration management
├── error_handler.py           # Error handling and recovery
├── config.yaml                # Configuration file (create from example)
├── config.example.yaml        # Example configuration
├── requirements.txt           # Python dependencies
├── facial_recognition/        # Directory for face encodings
│   └── encodings.pickle       # Pre-trained face data
└── README.md                  # This file
```

## Configuration

All configuration is now managed through the `config.yaml` file. The system includes:

### Configuration Management
- **Centralized Settings**: All settings in one YAML file
- **Validation**: Automatic configuration validation on startup
- **Defaults**: Fallback to sensible defaults if configuration is missing
- **Environment Support**: Easy to modify for different environments

### Key Configuration Sections

**Voice Settings**:
```yaml
voice:
  rate: 160                    # Speech rate
  voice_index: 16              # Voice selection
  volume: 1.0                  # Volume level
```

**Camera Settings**:
```yaml
camera:
  source: 0                    # Camera source
  framerate: 2                 # Processing framerate
  width: 500                   # Frame width
```

**Smart Light Settings**:
```yaml
smart_lights:
  kasa_host: "192.168.12.238"  # Your light's IP
  colors:
    red: [0, 100, 80]          # HSV color values
```

**Weather Settings**:
```yaml
weather:
  location:
    latitude: 41.8781          # Your latitude
    longitude: -87.6298        # Your longitude
  use_mock_data: true          # Use mock data for testing
```

## Error Handling & Troubleshooting

The system now includes comprehensive error handling and recovery mechanisms:

### Error Handling Features
- **Custom Exceptions**: Specific error types for different components
- **Automatic Recovery**: Attempts to recover from common errors
- **Graceful Degradation**: Continues operation when possible
- **Detailed Logging**: Comprehensive error logging with context
- **Error Statistics**: Track and monitor error patterns

### Common Issues

1. **Camera not found**
   - Check camera permissions
   - Try different camera sources in config.yaml
   - Verify camera is not in use by another application

2. **Face recognition not working**
   - Ensure `encodings.pickle` file exists and path is correct in config
   - Check lighting conditions
   - Verify face is clearly visible
   - Adjust tolerance setting in configuration

3. **Voice not working**
   - Install system text-to-speech drivers
   - Check audio output settings
   - Verify voice index in configuration

4. **Smart lights not responding**
   - Verify IP address is correct in config.yaml
   - Check network connectivity
   - Ensure Kasa CLI is installed
   - Check light power and network status

5. **Configuration errors**
   - Validate your config.yaml file
   - Check for syntax errors
   - Ensure all required sections are present

### Error Messages & Logging

The system now provides detailed logging:
- **Log File**: Check `smartHome.log` for detailed error information
- **Console Output**: Real-time status and error messages
- **Error Recovery**: Automatic attempts to recover from failures

### Debugging

To enable debug logging, set in your config.yaml:
```yaml
system:
  log_level: "DEBUG"
```

## Security Considerations

- The system stores face encodings locally
- No data is transmitted to external servers (except weather API)
- Consider implementing additional authentication for sensitive operations
- Regularly update face encodings for security

## Future Enhancements

- Voice command input
- Integration with more smart home devices
- Mobile app interface
- Scheduling and automation features
- Enhanced security features
- Support for more weather APIs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Create an issue in the repository

---

**Note**: This is a demonstration project. For production use, implement proper security measures and error handling. 