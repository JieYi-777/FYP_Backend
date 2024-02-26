from flask import Flask
import secrets


# To create the flask app with settings
def create_app():
    app = Flask(__name__)

    # Generate random strings of 32 hexadecimal characters for SECRET_KEY
    app.config['SECRET_KEY'] = secrets.token_hex(16)

    return app
