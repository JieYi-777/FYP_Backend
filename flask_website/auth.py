from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from .models import User, Notification
from . import bcrypt, db
import logging

# Create Blueprint object
auth = Blueprint('auth', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)


# Route to serve the user registration and return the token with message
@auth.route('/register', methods=['POST'])
def register():
    try:

        # Get registration form data in json format
        user_data = request.json

        # Get each data from request
        username = user_data.get('username')
        email = user_data.get('email')
        password = user_data.get('password')

        # Check if username or email already exists
        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        # If username or email already exists, return error response
        if existing_username:
            return jsonify({'message': 'Username already exists'}), 400
        elif existing_email:
            return jsonify({'message': 'Email already exists'}), 400

        # Create new user object with username, email and encrypted password
        new_user = User(username=username, email=email, password_hash=bcrypt.generate_password_hash(password))

        # Create welcome message object, reference to the new user
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

        # Store the new user and message in database, committing the transactions
        db.session.add(new_user)
        db.session.add(welcome_message)
        db.session.commit()

        # Create the JWT token
        access_token = create_access_token(identity=new_user.id)

        # Return the message with the token
        return jsonify({'message': 'Account created successfully', 'token': access_token}), 201

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        # Logging the error in console and return the error message to frontend
        logger.error(f'An error occurred: {str(e)}')
        return jsonify({'message': 'An error occurred while registering account'}), 500


# Route to serve the user login and return the token with message
@auth.route('/login', methods=['POST'])
def login():
    try:
        # Get user login data in json format
        user_data = request.json

        # Get each data from the request
        identifier = user_data.get('identifier')
        password = user_data.get('password')
        is_email = True if user_data.get('isEmail') == 'true' else False

        # If it is email, search the user using the email, else using the username
        if is_email:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(username=identifier).first()

        # If the user is registered and found in database, check the password, else return user not found error message
        if user:
            # If the password is correct, then create the token, return it with message to user
            if bcrypt.check_password_hash(user.password_hash, password):
                access_token = create_access_token(identity=user.id)

                return jsonify({'message': 'Login successful', 'token': access_token}), 200

            # Else, return the password error message
            else:
                return jsonify({'message': 'Incorrect password'}), 401
        else:
            return jsonify({'message': 'User not found'}), 404

    # If any error, logging the message and return the message to user
    except Exception as e:
        logger.error(f'An error occurred: {str(e)}')
        return jsonify({'message': 'An error occurred while logging in'}), 500


# Route to serve the user logout
# @auth.route('/logout')
# def logout():
#     return jsonify({'message': 'User logged out successfully'})
