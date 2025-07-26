"""
Configuration settings for the Python execution service.
"""

import os
from typing import Dict, Any


class Config:
    """Application configuration."""
    
    # Flask settings
    PORT = int(os.environ.get('PORT', 8080))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Security settings
    MAX_CODE_LENGTH = int(os.environ.get('MAX_CODE_LENGTH', 10000))  # 10KB max
    EXECUTION_TIMEOUT = int(os.environ.get('EXECUTION_TIMEOUT', 30))  # 30 seconds


def get_config() -> Config:
    """Get application configuration."""
    return Config()
