"""
Flask routes for the Python execution service.
"""

from flask import Flask, request, jsonify
from validator import validate_python_code
from sandbox import execute_code_with_nsjail
from exceptions import CodeValidationError
from config import get_config

config = get_config()


def create_routes(app: Flask) -> None:
    @app.route('/execute', methods=['POST'])
    def execute_code():
        """
        Execute Python code endpoint.
        
        Expected JSON payload:
        {
            "script": "def main(): return {'hello': 'world'}"
        }
        
        Returns:
        {
            "result": {...},  # Return value from main()
            "stdout": "..."   # stdout content
        }
        """
        try:
            # Validate request
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            if not data or 'script' not in data:
                return jsonify({'error': 'Missing "script" field in request'}), 400
            
            script = data['script']
            
            # Validate script length
            if len(script) > config.MAX_CODE_LENGTH:
                return jsonify({'error': f'Script too long. Maximum {config.MAX_CODE_LENGTH} characters allowed'}), 400
            
            # Validate the code
            validate_python_code(script)
            
            # Execute the code
            execution_result = execute_code_with_nsjail(script)
            
            if not execution_result['success']:
                return jsonify({
                    'error': execution_result['error'],
                    'stdout': execution_result.get('stdout', ''),
                    'stderr': execution_result.get('stderr', '')
                }), 400
            
            # Return successful result
            return jsonify({
                'result': execution_result['result'],
                'stdout': execution_result['stdout']
            })
        except CodeValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
