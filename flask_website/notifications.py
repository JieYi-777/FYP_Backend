from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Notification
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

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        if user:

            # Access notifications associated with the user through the relationship
            notifications = user.notifications

            # Serialize the notifications to JSON
            serialized_notifications = [{
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'has_read': notification.has_read,
                'date_created': notification.date_created
            } for notification in notifications]

            return jsonify({'notifications': serialized_notifications}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500


# To mark the notification based on its id as has read in database
@notifications.route('/mark-as-read/<notification_id>', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    try:

        # Get the user ID
        user_id = get_jwt_identity()

        # Query the database to find the notification belonging to the authenticated user
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

        if notification:
            # Mark the notification as read
            notification.has_read = True
            db.session.commit()

            return jsonify({'message': f'Notification {notification_id} marked as read.'}), 200
        else:
            return jsonify({'message': 'Notification not found'}), 404

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500


@notifications.route('/mark-all-as-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    try:

        # Get the user ID
        user_id = get_jwt_identity()

        # Query the database to find the authenticated user
        user = User.query.get(user_id)

        if user:
            # Mark all notifications as read for the user
            for notification in user.notifications:
                notification.has_read = True

            db.session.commit()

            return jsonify({'message': 'All notifications marked as read.'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500


''' Testing purpose only'''
# @notifications.route('/add')
# def add_notification():
#     message = Notification(title='Test 3', message="test 3", user_id=1)
#
#     db.session.add(message)
#     db.session.commit()
#
#     return jsonify({'message': 'test good'})
