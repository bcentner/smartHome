"""
SmartHome System Driver
Main entry point for the SmartHome automation system.
"""

import pyttsx3
import os
import time
import logging
from typing import Optional

from config_manager import config
from error_handler import (
    SmartHomeError, VoiceError, FacialRecognitionError, 
    handle_errors, safe_execute, error_handler
)
from facial_req import FaceRecognition
from logic import Users


class SmartHomeDriver:
    """Main driver class for the SmartHome system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine: Optional[pyttsx3.Engine] = None
        self.users: Optional[Users] = None
        self.face_system: Optional[FaceRecognition] = None
        self.running = False
        
        # Validate configuration
        if not config.validate_config():
            raise SmartHomeError("Configuration validation failed", component="configuration")
    
    @handle_errors
    def setup(self) -> bool:
        """Setup the SmartHome system components."""
        try:
            self.logger.info("Setting up SmartHome system...")
            
            # Setup facial recognition encodings
            if not self._setup_facial_recognition():
                return False
            
            # Initialize voice engine
            if not self._init_voice_engine():
                return False
            
            # Initialize user management
            if not self._init_user_management():
                return False
            
            # Initialize facial recognition
            if not self._init_facial_recognition():
                return False
            
            self.logger.info("SmartHome system setup completed successfully")
            return True
            
        except Exception as e:
            raise SmartHomeError(f"Setup failed: {str(e)}", component="system")
    
    def _setup_facial_recognition(self) -> bool:
        """Setup facial recognition encodings file."""
        try:
            encodings_file = config.get('facial_recognition.encodings_file', 'facial_recognition/encodings.pickle')
            
            if os.path.exists("encodings.pickle"):
                self.logger.info("Found existing encodings file")
                return True
            else:
                if os.path.exists(encodings_file):
                    import shutil
                    dest = os.path.join(os.getcwd(), "encodings.pickle")
                    shutil.copy2(encodings_file, dest)
                    self.logger.info("Copied encodings file to working directory")
                    return True
                else:
                    self.logger.warning(f"Encodings file not found: {encodings_file}")
                    return False
                    
        except Exception as e:
            raise FacialRecognitionError(f"Failed to setup facial recognition: {str(e)}")
    
    def _init_voice_engine(self) -> bool:
        """Initialize the text-to-speech engine."""
        try:
            self.engine = pyttsx3.init()
            
            # Apply voice settings from configuration
            voice_settings = config.get_voice_settings()
            self.engine.setProperty('rate', voice_settings['rate'])
            self.engine.setProperty('volume', voice_settings['volume'])
            
            # Set voice
            voices = self.engine.getProperty('voices')
            voice_index = voice_settings['voice_index']
            
            if voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)
                self.logger.info(f"Voice engine initialized with voice index {voice_index}")
            else:
                self.logger.warning(f"Voice index {voice_index} not available, using default")
            
            return True
            
        except Exception as e:
            raise VoiceError(f"Failed to initialize voice engine: {str(e)}")
    
    def _init_user_management(self) -> bool:
        """Initialize user management system."""
        try:
            if self.engine is None:
                raise SmartHomeError("Voice engine not initialized", component="system")
            
            self.users = Users(self.engine, config)
            self.logger.info("User management system initialized")
            return True
            
        except Exception as e:
            raise SmartHomeError(f"Failed to initialize user management: {str(e)}", component="system")
    
    def _init_facial_recognition(self) -> bool:
        """Initialize facial recognition system."""
        try:
            self.face_system = FaceRecognition(config)
            self.face_system.start()
            self.logger.info("Facial recognition system initialized")
            return True
            
        except Exception as e:
            raise FacialRecognitionError(f"Failed to initialize facial recognition: {str(e)}")
    
    @handle_errors
    def run(self) -> None:
        """Run the main SmartHome system loop."""
        try:
            self.logger.info("Starting SmartHome system...")
            self.running = True
            
            # Wait for systems to initialize
            time.sleep(1)
            
            while self.running:
                if self.face_system and self.face_system.new_person_found:
                    self._handle_new_user()
                time.sleep(config.get('facial_recognition.detection_interval', 1.0))
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            raise SmartHomeError(f"Runtime error: {str(e)}", component="system")
        finally:
            self.cleanup()
    
    def _handle_new_user(self) -> None:
        """Handle detection of a new user."""
        try:
            if not self.face_system or not self.users:
                return
            
            user_name = self.face_system.get_name
            self.users.log_in(user_name)
            self.face_system.reset_new_person_found()
            
            # Greet the user
            self._speak(f"Hello {user_name}")
            
        except Exception as e:
            self.logger.error(f"Error handling new user: {e}")
    
    def _speak(self, text: str) -> None:
        """Speak text using the voice engine."""
        try:
            if self.engine:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
    
    def cleanup(self) -> None:
        """Cleanup system resources."""
        try:
            self.logger.info("Cleaning up SmartHome system...")
            
            if self.face_system:
                self.face_system.stop()
            
            # Cleanup temporary files
            if os.path.exists("encodings.pickle"):
                os.remove("encodings.pickle")
                self.logger.info("Cleaned up temporary encodings file")
            
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def stop(self) -> None:
        """Stop the SmartHome system."""
        self.running = False


def main():
    """Main entry point for the SmartHome system."""
    driver = None
    try:
        driver = SmartHomeDriver()
        
        if driver.setup():
            driver.run()
        else:
            logging.error("Failed to setup SmartHome system")
            return 1
            
    except SmartHomeError as e:
        error_handler.handle_error(e)
        return 1
    except Exception as e:
        logging.critical(f"Unexpected error: {e}")
        return 1
    finally:
        if driver:
            driver.cleanup()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
