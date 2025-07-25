"""
Code validation utilities for the Python execution service.
"""

import ast
import json
from exceptions import CodeValidationError


def validate_python_code(code: str) -> None:
    """
    Validate that the code contains a main() function and is syntactically correct.
    """
    if not code or not code.strip():
        raise CodeValidationError("Code cannot be empty")
    
    # Check for unsafe patterns - more comprehensive
    unsafe_patterns = [
        'import os', 'import sys', 'import subprocess', 'import socket',
        'import urllib', 'import requests', 'import http', 'import ftplib',
        'import smtplib', 'import telnetlib', 'import webbrowser',
        'from os', 'from sys', 'from subprocess', 'from socket',
        '__import__', 'getattr', 'setattr', 'delattr', 'hasattr',
        'globals()', 'locals()', 'vars()', 'dir()',
        'eval(', 'exec(', 'compile(', 'open(', 'file(',
        'input(', 'raw_input(', 'execfile(',
        '__builtins__', '__globals__', '__locals__'
    ]
    
    code_lower = code.lower()
    for pattern in unsafe_patterns:
        if pattern in code_lower:
            raise CodeValidationError(f"Unsafe operation detected: {pattern}")
    try:
        # Parse the code to check syntax
        tree = ast.parse(code)
    except SyntaxError as e:
        raise CodeValidationError(f"Syntax error in code: {e}")
    
    # Check if main() function exists and has return statements
    has_main = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            has_main = True
            # Check if function has at least one return statement
            has_return = any(isinstance(stmt, ast.Return) for stmt in ast.walk(node))
            if not has_return:
                raise CodeValidationError("main() function must have a return statement")
            break
    
    if not has_main:
        raise CodeValidationError("Code must contain a main() function")