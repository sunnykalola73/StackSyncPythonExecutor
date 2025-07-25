#!/usr/bin/env python3
import logging
import sys
from flask import Flask
from config import get_config
from routes import create_routes


def setup_logging():
    """Configure logging for Google Cloud Run"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        stream=sys.stdout  # Cloud Run captures stdout
    )
    # Disable werkzeug default logger
    logging.getLogger('werkzeug').setLevel(logging.ERROR)


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    # Setup logging first
    setup_logging()
    
    app = Flask(__name__)
    logger = logging.getLogger(__name__)
    logger.info("Initializing Flask application")
    
    # Load configuration
    config = get_config()
    
    # Create routes
    create_routes(app)
    
    logger.info("Flask application initialized successfully")
    
    return app


# Create the Flask app
app = create_app()

if __name__ == '__main__':
    config = get_config()
    app.run(host=config.HOST, port=config.PORT)
