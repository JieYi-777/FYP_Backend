from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Expense, Category
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
