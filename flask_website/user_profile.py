from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from . import bcrypt, db
import logging

# Create Blueprint object
user_profile = Blueprint('user_profile', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)


@user_profile.route('/update-username', methods=['PUT'])
@jwt_required()
def update_username():
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        # Check the user is existed or not
        if user is None:
            return jsonify({'message': 'Account Not Found'}), 404

        # Get the new username from the request
        new_username = request.json.get('new_username')

        # Check if the new username is already taken
        existing_user = User.query.filter_by(username=new_username).first()

        if existing_user:
            return jsonify({'message': 'Username Already Exists'}), 400

        # Update the username
        user.username = new_username

        # Save changes to the database
        db.session.commit()

        return jsonify({'message': 'Username updated successfully.'}), 200

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while updating username.'}), 500


@user_profile.route('/update-email', methods=['PUT'])
@jwt_required()
def update_email():
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        # Check the user is existed or not
        if user is None:
            return jsonify({'message': 'Account Not Found'}), 404

        # Get the new email from the request
        new_email = request.json.get('new_email')

        # Check if the new email is already taken
        existing_email = User.query.filter_by(email=new_email).first()

        if existing_email:
            return jsonify({'message': 'Email Already Exists'}), 400

        # Update the email
        user.email = new_email

        # Save changes to the database
        db.session.commit()

        return jsonify({'message': 'Email updated successfully.'}), 200

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while updating email.'}), 500


@user_profile.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        # Get the old password and new password from the request
        password_data = request.json
        old_password = password_data.get('old_password')
        new_password = password_data.get('new_password')

        # Check the user is existed or not
        if user:
            # If the password is correct, then change the password, return it with message to user
            if bcrypt.check_password_hash(user.password_hash, old_password):

                user.password_hash = bcrypt.generate_password_hash(new_password)

                # Save changes to the database
                db.session.commit()

                return jsonify({'message': 'Password changed successfully.'}), 200

            # Else, return the password error message
            else:
                return jsonify({'message': 'Incorrect Old Password'}), 401
        else:
            return jsonify({'message': 'Account Not Found'}), 404

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while changing password.'}), 500
