from flask_website import create_app

# Create the flask app
app = create_app()

# Run the script.
if __name__ == '__main__':
    app.run(debug=True)
