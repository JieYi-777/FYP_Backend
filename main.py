from flask_website import create_app
from flask_website.services import services
from flask_website.auth import auth

# Create the flask app
app = create_app()

# Register the blueprints here to avoid the circular import error in flask_website package
app.register_blueprint(services, url_prefix="/")
app.register_blueprint(auth, url_prefix="/auth/")

# Run the script
if __name__ == '__main__':
    app.run(debug=True)