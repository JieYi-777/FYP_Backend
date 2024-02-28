from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from .services import services
from .auth import auth
import secrets
import os

# Load environment variables from the .env file
load_dotenv()

# Get values from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

db = SQLAlchemy()


# To create the flask app with settings
def create_app():
    # Create Flask instance named app
    app = Flask(__name__)

    # Generate random strings of 32 hexadecimal characters for SECRET_KEY of app
    app.config['SECRET_KEY'] = secrets.token_hex(16)

    # Set Database URI for Flask app
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    db.init_app(app)

    # Register the blueprints
    app.register_blueprint(services, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth/")

    return app
