from flask_website import create_app
from flask_website.notifications import notifications
from flask_website.auth import auth
from flask_website.email import email

# Create the flask app
app = create_app()

# Register the blueprints here to avoid the circular import error in flask_website package
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(notifications, url_prefix="/notifications")
app.register_blueprint(email, url_prefix="/email")

# Run the script
if __name__ == '__main__':
    app.run(debug=True)
