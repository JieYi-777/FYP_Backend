from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
import logging

# Create Blueprint object
user_profile = Blueprint('user_profile', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)


@user_profile.route('/edit-username', methods=['PUT'])
@jwt_required()
def edit_username():
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        # Get the new username from the request
        new_username = request.json.get('new_username')

        # Check if the new username is already taken
        existing_user = User.query.filter_by(username=new_username).first()

        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400






    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500
