from flask import Blueprint, jsonify

# Create Blueprint object
services = Blueprint('services', __name__)


# Sample
@services.route('/')
def home():
    return jsonify({'message': 'hello'})
