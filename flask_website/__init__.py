from flask import Flask
from .services import services
from .auth import auth
import secrets


# To create the flask app with settings
def create_app():
    # Create Flask instance named app
    app = Flask(__name__)

    # Generate random strings of 32 hexadecimal characters for SECRET_KEY
    app.config['SECRET_KEY'] = secrets.token_hex(16)

    # Register the blueprints
    app.register_blueprint(services, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth/")

    return app
