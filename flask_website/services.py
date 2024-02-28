from flask import Blueprint

# Create Blueprint object
services = Blueprint('services', __name__)


# Sample
@services.route('/')
def home():
    return "<h1>Testing Home</h1>"
