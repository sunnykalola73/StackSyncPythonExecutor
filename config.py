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
    
    # nsjail resource limits
    NSJAIL_LIMITS = {
        'time_limit': EXECUTION_TIMEOUT,
        'rlimit_as': int(os.environ.get('MEMORY_LIMIT_MB', 512)),  # MB
        'rlimit_cpu': int(os.environ.get('CPU_LIMIT_SEC', 10)),   # seconds
        'rlimit_fsize': int(os.environ.get('FILE_SIZE_LIMIT_MB', 16)),  # MB
        'rlimit_nofile': int(os.environ.get('MAX_FILES', 32))     # file count
    }


def get_config() -> Config:
    """Get application configuration."""
    return Config()
