from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from . import db
import logging

# Create Blueprint object
email = Blueprint('email', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)


# To get user personal email
@email.route('')
@jwt_required()
def get_email():
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        if user:
            email = user.email

            return jsonify({'email': email}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500
