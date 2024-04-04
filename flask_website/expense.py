from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, extract
from .models import User, Expense, Category, Budget, Notification
from . import db
import logging
import os
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Create Blueprint object
expense = Blueprint('expense', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)

# Get the directory path of the current script (app.py)
current_dir = os.path.dirname(__file__)

# Define the path to the folder containing the model file
models_dir = os.path.join(current_dir, 'machine_learning_models', 'categorize_expense')

# Specify the path to the model file
model_file_path = os.path.join(models_dir, 'nb_model.pkl')

# Specify the vectorizer file
vectorizer_file_path = os.path.join(models_dir, 'vectorizer.pkl')

# Load the trained model and vectorizer
nb_model = joblib.load(model_file_path)
vectorizer = joblib.load(vectorizer_file_path)


# Download the required resources, one time only
# nltk.download('stopwords')
# nltk.download('punkt')


# To preprocess the text before use in machine learning model
def preprocess_text(text):
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    # Convert to lowercase
    text = text.lower()

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Stem the words
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens]

    # Join the tokens back into a single string
    preprocessed_text = ' '.join(tokens)

    return preprocessed_text


# To get the expense category list
@expense.route('/get-expense-category-list')
@jwt_required()
def get_category_list():
    try:

        # Retrieve all the category from the database
        categories = Category.query.order_by(Category.id).all()

        # Format the list
        category_list = [{
            'id': category.id,
            'name': category.name
        } for category in categories]

        return jsonify({'category_list': category_list}), 200

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500


@expense.route('/add-expense', methods=['POST'])
@jwt_required()
def add_expense():
    try:
        # Get the current user id
        user_id = get_jwt_identity()

        # Get expense data to be store from request
        expense_data = request.json

        # Get each data from the request
        title = expense_data.get('title')
        date = datetime.fromisoformat(expense_data.get('date'))
        amount = expense_data.get('amount')
        category_id = expense_data.get('category_id')
        description = expense_data.get('description')

        # Create new expense object
        new_expense = Expense(title=title, date=date, amount=amount, category_id=category_id,
                              description=description, user_id=user_id)

        # Store the new expense in database, committing the transactions
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({'message': 'The expense has been successfully added.'}), 200

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while adding expense.'}), 500


# To get all the expenses related to the user
@expense.route('')
@jwt_required()
def get_all_expenses():
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        if user:

            # Access expenses associated with the user, and order by date in descending order
            expenses = Expense.query.filter_by(user_id=user_id).order_by(desc(Expense.date)).all()

            # Serialize the expenses to JSON
            serialized_expenses = [{
                'id': expense.id,
                'title': expense.title,
                'date': expense.date,
                'amount': expense.amount,
                'category_id': expense.category_id,
                'category_name': expense.category.name,
                'description': expense.description
            } for expense in expenses]

            return jsonify({'expenses': serialized_expenses}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500


@expense.route('/update-expense/<expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Get expense data to be store from request
        expense_data = request.json

        # Get each data from the request
        title = expense_data.get('title')
        date = datetime.fromisoformat(expense_data.get('date'))
        amount = expense_data.get('amount')
        category_id = expense_data.get('category_id')
        description = expense_data.get('description')

        # Update the expense
        updated_expense = Expense.query.filter_by(id=expense_id, user_id=user_id).update(
            {
                'title': title,
                'date': date,
                'amount': amount,
                'category_id': category_id,
                'description': description
            }
        )

        # Commit the changes to the database
        db.session.commit()

        if updated_expense:
            return jsonify({'message': "Expense updated successfully."}), 200
        else:
            return jsonify({'message': "No Expense Found"}), 404

    except Exception as e:
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while updating expense.'}), 500


@expense.route('/delete-expense/<expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Delete the expense directly using a query
        deleted_expense = Expense.query.filter_by(id=expense_id, user_id=user_id).delete()

        # Commit the changes to the database
        db.session.commit()

        if deleted_expense:
            return jsonify({'message': 'Expense deleted successfully.'}), 200
        else:
            return jsonify({'message': 'Expense Not Found'}), 404

    except Exception as e:
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while deleting expense.'}), 500


# To check the current month expense will exceed the budget or not
@expense.route('/check-monthly-expense', methods=['POST'])
@jwt_required()
def check_monthly_expense_with_budget():
    try:
        # Get the current user id
        user_id = get_jwt_identity()

        # Get expense data to be store from request
        category_id = request.json.get('category_id')

        # Get the current year and month
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Query expenses for the given user, category, and current year/month
        total_expense = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.category_id == category_id,
            extract('year', Expense.date) == current_year,
            extract('month', Expense.date) == current_month
        ).scalar() or 0

        # Query the budget for the given user and category
        budget = Budget.query.filter_by(user_id=user_id, category_id=category_id).first()

        if budget:
            is_exceed_value = budget.is_exceed

            # Compare total expense with the budget amount
            if total_expense >= budget.amount:
                # Update is_exceed field of the budget to True
                budget.is_exceed = True
            else:
                # Reset is_exceed field of the budget to False
                budget.is_exceed = False

            db.session.commit()

            # Create a notification if expenses reach or exceed the budget
            if is_exceed_value is False and total_expense >= budget.amount:
                if total_expense == budget.amount:
                    title = 'Budget Reached'
                    message = f'Your expenses in category {budget.category.name} have reached the budget limit.'
                else:
                    title = 'Budget Exceeded'
                    message = f'Your expenses in category {budget.category.name} have exceeded the budget.'

                notification = Notification(
                    title=title,
                    message=message,
                    user_id=user_id
                )
                db.session.add(notification)
                db.session.commit()

        return jsonify({'message': 'Monthly expenses have been checked against the budget.'}), 200

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while checking the monthly expense and budget.'}), 500


# To predict and suggest the category of the expense
@expense.route('/predict-expense-category', methods=['POST'])
@jwt_required()
def predict_expense_category():
    try:
        # Get expense data to be store from request
        expense_data = request.json

        # Get each data from the request
        title = expense_data.get('title')
        description = expense_data.get('description')

        # Concatenate title and description
        combined_text = f"{title} {description}"

        # Preprocess combined text
        preprocessed_combined_text = preprocess_text(combined_text)

        # Vectorize combined text
        combined_text_vectorized = vectorizer.transform([preprocessed_combined_text])

        # Make predictions
        predictions = nb_model.predict(combined_text_vectorized)

        # Get the prediction (it is in array/list form)
        prediction = predictions[0]

        print(prediction)

        return jsonify({'prediction': prediction})
    except Exception as e:
        logger.error(e)
        return jsonify({'message': 'An error occurred while predicting the expense category.'}), 500
