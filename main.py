from flask_website import create_app
from flask_website.notifications import notifications
from flask_website.auth import auth
from flask_website.email import email
from flask_website.user_profile import user_profile
from flask_website.expense import expense
from flask_website.budget import budget

# Create the flask app
app = create_app()

# Register the blueprints here to avoid the circular import error in flask_website package
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(notifications, url_prefix="/notifications")
app.register_blueprint(email, url_prefix="/email")
app.register_blueprint(user_profile, url_prefix="/user-profile")
app.register_blueprint(expense, url_prefix="/expense")
app.register_blueprint(budget, url_prefix="/budget")

# Run the script
if __name__ == '__main__':
    app.run(debug=True)
