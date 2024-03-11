from flask import Blueprint, jsonify

# Create Blueprint object
notification = Blueprint('notification', __name__)


# Sample
@notification.route('/')
def home():
    return jsonify({'message': 'hello'})
