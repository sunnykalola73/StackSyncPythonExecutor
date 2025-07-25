#!/bin/bash
set -e

# Start the Flask application with Gunicorn
exec gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 60 app:app
