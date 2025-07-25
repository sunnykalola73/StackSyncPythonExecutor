#!/usr/bin/env python3
from flask import Flask
from config import get_config
from routes import create_routes


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    
    # Create routes
    create_routes(app)
    
    return app


# Create the Flask app
app = create_app()

if __name__ == '__main__':
    config = get_config()
    app.run(host=config.HOST, port=config.PORT)
