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
   pip install pyttsx3 opencv-python face-recognition imutils requests cvzone
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

## Setup

### 1. Facial Recognition Setup

The system requires pre-trained facial encodings. You need to:

1. Create a `facial_recognition/` directory
2. Add an `encodings.pickle` file with known face encodings
3. The system will automatically copy this file to the working directory

**Note**: The `encodings.pickle` file should contain a dictionary with:
- `"encodings"`: List of face encodings
- `"names"`: List of corresponding names

### 2. Smart Light Configuration

Update the IP address in `logic.py` for your Kasa smart lights:
```python
cmd = ["kasa", "--host", "192.168.12.238"]  # Change to your light's IP
```

### 3. Weather API (Optional)

The system uses Meteomatics API for weather data. For production use, you may want to:
- Sign up for an API key
- Update the weather function to use authentication
- Currently uses mock data for demonstration

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
├── driver.py              # Main application driver
├── logic.py               # User management and command logic
├── facial_req.py          # Facial recognition system
├── hand_req.py            # Hand gesture recognition (experimental)
├── facial_recognition/    # Directory for face encodings
│   └── encodings.pickle   # Pre-trained face data
└── README.md              # This file
```

## Configuration

### Voice Settings
Modify voice properties in `driver.py`:
```python
eng.setProperty('rate', 160)  # Speech rate
eng.setProperty('voice', voices[16].id)  # Voice selection
```

### Camera Settings
Adjust camera source in `facial_req.py`:
```python
vs = VideoStream(src=0, framerate=2).start()  # Change src for different cameras
```

### Weather Location
Update coordinates in `logic.py` for your location:
```python
# Current: Chicago coordinates (41.8781, -87.6298)
url = f"https://api.meteomatics.com/{formatted_datetime}/{format}/41.8781,87.6298/html"
```

## Troubleshooting

### Common Issues

1. **Camera not found**
   - Check camera permissions
   - Try different camera sources (src=0, 1, 2, etc.)

2. **Face recognition not working**
   - Ensure `encodings.pickle` file exists
   - Check lighting conditions
   - Verify face is clearly visible

3. **Voice not working**
   - Install system text-to-speech drivers
   - Check audio output settings

4. **Smart lights not responding**
   - Verify IP address is correct
   - Check network connectivity
   - Ensure Kasa CLI is installed

### Error Messages

- `"Found encodings"` - System found face data
- `"Copyied encodings"` - System copied face data to working directory
- `"Recognized [name]"` - Face recognition successful
- `"Hello [name]"` - Voice greeting for recognized user

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