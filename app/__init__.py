from flask import Flask

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

    # Import and register the main blueprint that contains routes
    from .routes import main
    app.register_blueprint(main)

    # Return the fully configured Flask app
    return app
