from datetime import timedelta
from .resetBudgetAlert import start_scheduler
from .predictExpense import start_predict_expense_scheduler
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import secrets
import os
import nltk

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

    # To allow CORS, split by ', ' to the origin links into list/array of links
    CORS(app, resources={r"/*": {"origins": os.getenv('ORIGIN').split(', ')}})

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

    # To start the scheduler to reset the budget model's is_exceed to 0 on the first day of every month at 12:00 AM
    start_scheduler(db, app)

    # To start the scheduler to predict the expense for each user's category on first day of every month at 12.15am
    start_predict_expense_scheduler(db, app)

    nltk.download('stopwords')
    nltk.download('punkt')

    # To create tables for the database
    # from .models import User, Category, Expense, Budget, Notification
    # # Create the application context
    # with app.app_context():
    #     # Create all tables
    #     db.create_all()

    return app