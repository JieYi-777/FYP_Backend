from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from .models import User, Notification
from . import bcrypt, db
import logging

# Create Blueprint object
auth = Blueprint('auth', __name__)

# Get a logger
logger = logging.getLogger(__name__)


@auth.route('/register', methods=['POST'])
def register():
    try:

        # Get registration form data in json format
        user_data = request.json

        # Get each data
        username = user_data['username']
        email = user_data['email']
        password = user_data['password']

        # Check if username or email already exists
        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        # If username or email already exists, return error response
        if existing_username:
            return jsonify({'message': 'Username already exists'}), 400
        elif existing_email:
            return jsonify({'message': 'Email already exists'}), 400

        # Create new user object and store in database
        new_user = User(username=username, email=email, password_hash=bcrypt.generate_password_hash(password))

        # Create welcome message
        welcome_message = Notification(title='Welcome to Smart Finance!', message="Welcome to Smart Finance! We're "
                                                                                  "thrilled to have you join our "
                                                                                  "community. Here, you can easily manage "
                                                                                  "your expenses, track your budgets, "
                                                                                  "and stay informed about your financial "
                                                                                  "goals.\n\nTo get started, we recommend "
                                                                                  "setting up your budgets for different "
                                                                                  "categories like food, transportation, "
                                                                                  "and housing. By doing so, "
                                                                                  "you'll receive timely notifications "
                                                                                  "when you're approaching your budget "
                                                                                  "limits.\n\nFeel free to explore the "
                                                                                  "platform and reach out if you have any "
                                                                                  "questions. Happy budgeting!",
                                       user=new_user)

        db.session.add(new_user)
        db.session.add(welcome_message)
        db.session.commit()

        return jsonify({'message': 'Account created successfully'}), 201

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()
        logger.error(f'An error occurred: {str(e)}')
        return jsonify({'message': 'An error occurred while registering account'}), 500


@auth.route('/login', methods=['POST'])
def login():
    return "<h1>Testing auth</h1>"


@auth.route('/logout')
def logout():
    return "<h1>Testing auth</h1>"
