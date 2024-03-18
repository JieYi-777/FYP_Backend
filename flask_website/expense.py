from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Expense, Category
from . import db
import logging

# Create Blueprint object
expense = Blueprint('expense', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)


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
