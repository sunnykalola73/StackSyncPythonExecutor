#!/bin/bash
set -e

# Enable debug logging
export PYTHONUNBUFFERED=1
export GUNICORN_CMD_ARGS="--capture-output --enable-stdio-inheritance"

# Log system information
echo "=== System Information ==="
uname -a
echo "=== Process Capabilities ==="
capsh --print || true
echo "=== Directory Permissions ==="
ls -la /tmp || true
echo "=========================="

# Ensure proper permissions for temporary directories
mkdir -p /tmp/sandbox
chmod 777 /tmp/sandbox

# Start the Flask application with Gunicorn
# Adding access log and error log configuration
exec gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    app:app
