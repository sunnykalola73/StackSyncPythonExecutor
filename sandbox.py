"""
Simple sandbox execution for Python code using nsjail.
"""

import json
import logging
import os
import subprocess
from typing import Dict, Any
from config import get_config

config = get_config()
logger = logging.getLogger(__name__)


def execute_code_with_nsjail(code: str) -> Dict[str, Any]:
    """Execute code with nsjail - simplified approach without config files."""
    logger.info("Starting code execution with nsjail")
    
    # Create wrapper code inline (no separate files)  
    wrapper_code = f'''
import json
import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr

user_code = {repr(code)}

try:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    namespace = {{'__name__': '__main__', '__builtins__': __builtins__}}
    
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        exec(user_code, namespace)
        
        if 'main' not in namespace:
            raise Exception("No main() function found")
        
        result = namespace['main']()
        
        # Validate that result is JSON serializable (but keep original object)
        try:
            json.dumps(result)  # Test serialization but don't store the string
        except (TypeError, ValueError) as json_error:
            error_type = type(result).__name__
            raise Exception(
                f"main() function must return JSON serializable data. "
                f"Got {{error_type}}: {{str(json_error)}}"
            )
    
    response = {{
        'success': True,
        'result': result,
        'stdout': stdout_buffer.getvalue().rstrip(),
        'stderr': stderr_buffer.getvalue().rstrip()
    }}
    
except Exception as e:
    response = {{
        'success': False,
        'error': str(e),
        'traceback': traceback.format_exc(),
        'stdout': stdout_buffer.getvalue().rstrip() if 'stdout_buffer' in locals() else '',
        'stderr': stderr_buffer.getvalue().rstrip() if 'stderr_buffer' in locals() else ''
    }}

print(json.dumps(response, default=str))
'''
    
    try:
        # Verify nsjail exists and is executable
        if not os.path.exists('/usr/local/bin/nsjail'):
            logger.error("nsjail binary not found at /usr/local/bin/nsjail")
            return {
                'success': False,
                'error': 'nsjail binary not found',
                'stdout': '',
                'stderr': 'System configuration error: nsjail not installed'
            }
        
        # Log nsjail version
        try:
            version_result = subprocess.run(['nsjail', '--version'], 
                capture_output=True, text=True)
            logger.info(f"nsjail version: {version_result.stdout.strip()}")
        except Exception as e:
            logger.warning(f"Failed to get nsjail version: {str(e)}")
        
        logger.info("Preparing to execute code in nsjail sandbox")
        
        # Use command line flags instead of config file - much simpler and more reliable
        cmd = [
            'nsjail',
            '--mode', 'o',  # once
            '--time_limit', str(config.EXECUTION_TIMEOUT),
            '--rlimit_as', '1024',  # 1GB memory
            '--rlimit_cpu', '10',
            '--rlimit_fsize', '64',
            '--rlimit_nofile', '128',
            # Disable all unnecessary features for Cloud Run compatibility
            '--disable_clone_newuser',
            '--disable_clone_newnet',
            '--disable_clone_newns',
            '--disable_clone_newpid',
            '--disable_clone_newipc',
            '--disable_clone_newuts',
            '--disable_clone_newcgroup',
            '--disable_proc',
            '--skip_setsid',
            '--use_preload',
            '--keep_caps',  # Keep capabilities
            '--disable_rlimits',  # Disable resource limits that might cause issues
            '--verbose',  # Enable verbose logging for debugging
            '--env', 'HOME=/tmp',
            '--env', 'PATH=/usr/local/bin:/usr/bin:/bin',
            '--env', 'PYTHONPATH=/usr/local/lib/python3.11/site-packages',
            '--env', 'LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:/lib',
            '--',
            '/usr/local/bin/python3', '-c', wrapper_code
        ]
        
        logger.info(f"Executing nsjail command with arguments: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.EXECUTION_TIMEOUT + 5
        )
        
        # Check if nsjail execution failed
        if result.returncode != 0:
            logger.error(f"nsjail execution failed with return code {result.returncode}")
            logger.error(f"nsjail stdout: {result.stdout}")
            logger.error(f"nsjail stderr: {result.stderr}")
            
            error_msg = "Code execution failed in sandbox"
            if result.returncode == 255:
                error_msg = "Failed to create process in Cloud Run environment. Please check container permissions and system resources."
            
            return {
                'success': False,
                'error': error_msg,
                'details': f'nsjail failed with return code {result.returncode}',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        
        # Parse JSON output from the wrapper
        if result.stdout.strip():
            try:
                return json.loads(result.stdout.strip())
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Failed to parse JSON output: {str(e)}',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
        else:
            return {
                'success': False,
                'error': 'No output from execution',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Code execution timed out', 'stdout': '', 'stderr': ''}
    except FileNotFoundError:
        return {'success': False, 'error': 'nsjail not found - please install nsjail', 'stdout': '', 'stderr': ''}
    except Exception as e:
        return {'success': False, 'error': f'Execution failed: {str(e)}', 'stdout': '', 'stderr': ''}
