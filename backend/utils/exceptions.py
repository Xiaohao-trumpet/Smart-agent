"""
Custom exception types for the application.
"""


class ChatSystemException(Exception):
    """Base exception for all chat system errors."""
    pass


class ModelAPIException(ChatSystemException):
    """Exception raised when model API calls fail."""
    pass


class SessionNotFoundException(ChatSystemException):
    """Exception raised when a session is not found."""
    pass


class RateLimitExceededException(ChatSystemException):
    """Exception raised when rate limit is exceeded."""
    pass


class ValidationException(ChatSystemException):
    """Exception raised for input validation errors."""
    pass


class ConfigurationException(ChatSystemException):
    """Exception raised for configuration errors."""
    pass
