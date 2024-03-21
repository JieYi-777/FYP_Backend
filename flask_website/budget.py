from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Budget
from . import db
import logging

# Create Blueprint object
budget = Blueprint('budget', __name__)

# Get a logger for logging
logger = logging.getLogger(__name__)

# To get all the budgets related to the user
@budget.route('')
@jwt_required()
def get_all_budgets():
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Retrieve the user object from the database
        user = User.query.get(user_id)

        if user:

            # Access budgets associated with the user
            budgets = Budget.query.filter_by(user_id=user_id).all()

            # Sort budgets by category name
            sorted_budgets = sorted(budgets, key=lambda budget: budget.category.name)

            # Serialize the budgets to JSON
            serialized_budgets = [{
                'id': budget.id,
                'amount': budget.amount,
                'category_id': budget.category_id,
                'category_name': budget.category.name,
            } for budget in sorted_budgets]

            return jsonify({'budgets': serialized_budgets}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        logger.error(e)
        return jsonify({'message': str(e)}), 500
