from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
import logging
import mailtrap as mt
import os

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
            return jsonify({'message': 'Account not found.'}), 404

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500


# To send support/help email from user to developer/support team
@email.route('/send-support-email', methods=['POST'])
@jwt_required()
def send_support_email():
    try:
        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)
        username = user.username

        # Get email data to be sent in json format
        email_data = request.json

        # Get each data from the request
        from_email = email_data.get('from')
        email_subject = email_data.get('subject')
        email_content = email_data.get('content')

        # Create mail object ('sender email' and 'to email' is constant since mailtrap free plan limitation)
        mail = mt.Mail(
            sender=mt.Address(email="mailtrap@demomailtrap.com", name="Smart Finance Help"),
            to=[mt.Address(email="limjieyi777@gmail.com")],
            subject=f"{email_subject}",
            text=f"From: {username} - {from_email}\n\n{email_content}"
        )

        # Give the MailTrap token to be used when sending email using its API
        # Note: The sent email maybe in spam folder
        client = mt.MailtrapClient(token=os.getenv('MAILTRAP_TOKEN'))
        client.send(mail)

        return jsonify({'message': 'Expect a response within 24 hours.'}), 200

    except Exception as e:
        logger.error(e)
        return jsonify({'message': 'An error occurred while sending email.'}), 500
