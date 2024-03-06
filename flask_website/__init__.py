from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import secrets
import os

# Load environment variables from the .env file
load_dotenv()

# Get values from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Define db outside so can be imported by models.py
db = SQLAlchemy()

# Create bcrypt object outside to be imported by other files
bcrypt = Bcrypt()


# To create the flask app with settings
def create_app():
    # Create Flask instance named app
    app = Flask(__name__)

    # To allow CORS
    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://192.168.1.119:8080"]}})

    # Generate random strings of 32 hexadecimal characters for SECRET_KEY of app
    app.config['SECRET_KEY'] = secrets.token_hex(16)

    # Initialize JWT manager
    app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    jwt = JWTManager(app)

    # Set Database URI for Flask app and initialize the app
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    db.init_app(app)

    # Initialize bcrypt object, used for encrypt password and check password currently
    bcrypt.init_app(app)

    # To create tables for the database
    # from .models import User, Category, Expense, Budget, Notification
    # # Create the application context
    # with app.app_context():
    #     # Create all tables
    #     db.create_all()

    return app
