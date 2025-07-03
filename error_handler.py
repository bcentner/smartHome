"""
Error Handling Module for SmartHome System
Provides custom exceptions, error recovery strategies, and graceful degradation.
"""

import logging
import traceback
import sys
from typing import Optional, Callable, Any, Dict
from functools import wraps
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SmartHomeError(Exception):
    """Base exception for SmartHome system."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 component: str = "unknown", recoverable: bool = True):
        self.message = message
        self.severity = severity
        self.component = component
        self.recoverable = recoverable
        super().__init__(self.message)


class CameraError(SmartHomeError):
    """Camera-related errors."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.HIGH):
        super().__init__(message, severity, "camera", True)


class VoiceError(SmartHomeError):
    """Voice/TTS-related errors."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        super().__init__(message, severity, "voice", True)


class FacialRecognitionError(SmartHomeError):
    """Facial recognition errors."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        super().__init__(message, severity, "facial_recognition", True)


class SmartLightError(SmartHomeError):
    """Smart light control errors."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        super().__init__(message, severity, "smart_lights", True)


class WeatherError(SmartHomeError):
    """Weather API errors."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.LOW):
        super().__init__(message, severity, "weather", True)


class ConfigurationError(SmartHomeError):
    """Configuration-related errors."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.HIGH):
        super().__init__(message, severity, "configuration", False)


class ErrorHandler:
    """Centralized error handling for the SmartHome system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_count: Dict[str, int] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self._setup_recovery_strategies()
    
    def _setup_recovery_strategies(self):
        """Setup default recovery strategies for different error types."""
        self.recovery_strategies = {
            'camera': self._recover_camera,
            'voice': self._recover_voice,
            'facial_recognition': self._recover_facial_recognition,
            'smart_lights': self._recover_smart_lights,
            'weather': self._recover_weather,
            'configuration': self._recover_configuration
        }
    
    def handle_error(self, error: SmartHomeError, context: Optional[Dict] = None) -> bool:
        """
        Handle a SmartHome error with appropriate logging and recovery.
        
        Args:
            error: The SmartHome error to handle
            context: Additional context information
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        try:
            # Log the error
            self._log_error(error, context)
            
            # Update error count
            self._update_error_count(error.component)
            
            # Attempt recovery if error is recoverable
            if error.recoverable:
                return self._attempt_recovery(error)
            else:
                self.logger.critical(f"Non-recoverable error in {error.component}: {error.message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            return False
    
    def _log_error(self, error: SmartHomeError, context: Optional[Dict] = None):
        """Log error with appropriate level based on severity."""
        log_message = f"[{error.component.upper()}] {error.message}"
        if context:
            log_message += f" | Context: {context}"
        
        if error.severity == ErrorSeverity.LOW:
            self.logger.warning(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.error(log_message)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
        elif error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
            self.logger.critical(f"Stack trace: {traceback.format_exc()}")
    
    def _update_error_count(self, component: str):
        """Update error count for a component."""
        self.error_count[component] = self.error_count.get(component, 0) + 1
    
    def _attempt_recovery(self, error: SmartHomeError) -> bool:
        """Attempt to recover from an error."""
        try:
            recovery_func = self.recovery_strategies.get(error.component)
            if recovery_func:
                self.logger.info(f"Attempting recovery for {error.component}")
                return recovery_func(error)
            else:
                self.logger.warning(f"No recovery strategy for {error.component}")
                return False
        except Exception as e:
            self.logger.error(f"Recovery failed for {error.component}: {e}")
            return False
    
    def _recover_camera(self, error: SmartHomeError) -> bool:
        """Recovery strategy for camera errors."""
        try:
            # Try to reinitialize camera with different source
            self.logger.info("Attempting camera recovery...")
            # This would be implemented in the camera module
            return True
        except Exception as e:
            self.logger.error(f"Camera recovery failed: {e}")
            return False
    
    def _recover_voice(self, error: SmartHomeError) -> bool:
        """Recovery strategy for voice errors."""
        try:
            self.logger.info("Attempting voice system recovery...")
            # Try to reinitialize TTS engine
            return True
        except Exception as e:
            self.logger.error(f"Voice recovery failed: {e}")
            return False
    
    def _recover_facial_recognition(self, error: SmartHomeError) -> bool:
        """Recovery strategy for facial recognition errors."""
        try:
            self.logger.info("Attempting facial recognition recovery...")
            # Try to reload encodings or restart detection
            return True
        except Exception as e:
            self.logger.error(f"Facial recognition recovery failed: {e}")
            return False
    
    def _recover_smart_lights(self, error: SmartHomeError) -> bool:
        """Recovery strategy for smart light errors."""
        try:
            self.logger.info("Attempting smart light recovery...")
            # Try to reconnect to lights
            return True
        except Exception as e:
            self.logger.error(f"Smart light recovery failed: {e}")
            return False
    
    def _recover_weather(self, error: SmartHomeError) -> bool:
        """Recovery strategy for weather errors."""
        try:
            self.logger.info("Attempting weather service recovery...")
            # Switch to mock data or retry API call
            return True
        except Exception as e:
            self.logger.error(f"Weather recovery failed: {e}")
            return False
    
    def _recover_configuration(self, error: SmartHomeError) -> bool:
        """Recovery strategy for configuration errors."""
        try:
            self.logger.info("Attempting configuration recovery...")
            # Reload configuration or use defaults
            return True
        except Exception as e:
            self.logger.error(f"Configuration recovery failed: {e}")
            return False
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            'total_errors': sum(self.error_count.values()),
            'error_count_by_component': self.error_count.copy(),
            'most_error_prone_component': max(self.error_count.items(), key=lambda x: x[1])[0] if self.error_count else None
        }
    
    def reset_error_count(self, component: Optional[str] = None):
        """Reset error count for a component or all components."""
        if component:
            self.error_count[component] = 0
        else:
            self.error_count.clear()


def handle_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in functions.
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SmartHomeError as e:
            error_handler = ErrorHandler()
            error_handler.handle_error(e, {'function': func.__name__})
            return None
        except Exception as e:
            # Convert generic exceptions to SmartHomeError
            smart_home_error = SmartHomeError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                ErrorSeverity.HIGH,
                "system"
            )
            error_handler = ErrorHandler()
            error_handler.handle_error(smart_home_error, {'function': func.__name__})
            return None
    return wrapper


def safe_execute(func: Callable, *args, default_return: Any = None, **kwargs) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return if function fails
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return if execution fails
    """
    try:
        return func(*args, **kwargs)
    except SmartHomeError as e:
        error_handler = ErrorHandler()
        error_handler.handle_error(e, {'function': func.__name__})
        return default_return
    except Exception as e:
        smart_home_error = SmartHomeError(
            f"Unexpected error in {func.__name__}: {str(e)}",
            ErrorSeverity.HIGH,
            "system"
        )
        error_handler = ErrorHandler()
        error_handler.handle_error(smart_home_error, {'function': func.__name__})
        return default_return


# Global error handler instance
error_handler = ErrorHandler() 