from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from . import db
import logging

# Create Blueprint object
notifications = Blueprint('notifications', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)

# Get all notifications for the current user
@notifications.route('')
@jwt_required()
def get_notifications():
    try:
        # Get the current user id
        user_id = get_jwt_identity()

        print(user_id)

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        # Access notifications associated with the user through the relationship
        notifications = user.notifications

        # Serialize the notifications to JSON
        serialized_notifications = [{
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'read': notification.read,
            'date_created': notification.date_created
        } for notification in notifications]

        return jsonify({'notifications': serialized_notifications}), 200
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500
