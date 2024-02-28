from flask import Blueprint

# Create Blueprint object
auth = Blueprint('auth', __name__)

# Sample
@auth.route('/')
def authenticate():
    return "<h1>Testing auth</h1>"
