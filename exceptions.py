"""
Custom exceptions for the Python execution service.
"""

class CodeValidationError(Exception):
    """Raised when the provided code fails validation."""
    pass


class ExecutionError(Exception):
    """Raised when code execution fails."""
    pass
