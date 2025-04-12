from dotenv import load_dotenv

from flask import Flask

import os

def create_app():
    """
    Flask application factory function.

    This function initializes the Flask app, registers blueprints,
    and returns the app instance ready to run.

    Returns:
        Flask app instance
    """
    # Create the Flask application instance
    app = Flask(__name__)

    # Load configuration based on FLASK_ENV or default to development
    env = os.getenv('FLASK_ENV', 'development')

    if env == 'production':
        app.config.from_object('config.ProductionConfig')
    elif env == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    # Import and register the main blueprint that contains routes
    from .routes import main
    app.register_blueprint(main)

    # Return the fully configured Flask app
    return app
