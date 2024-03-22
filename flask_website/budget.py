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


# To add budget
@budget.route('/add-budget', methods=['POST'])
@jwt_required()
def add_budget():
    try:
        # Get the current user id
        user_id = get_jwt_identity()

        # Get budget data to be store from request
        budget_data = request.json

        # Get each data from the request
        category_id = budget_data.get('category_id')
        amount = budget_data.get('amount')

        # Create new budget object
        new_budget = Budget(amount=amount, category_id=category_id, user_id=user_id)

        # Store the new budget in database, committing the transactions
        db.session.add(new_budget)
        db.session.commit()

        return jsonify({'message': 'The budget has been successfully added.'}), 200

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while adding budget.'}), 500


# To update the budget in database
@budget.route('/update-budget/<budget_id>', methods=['PUT'])
@jwt_required()
def update_budget(budget_id):
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Get budget data to be store from request
        budget_data = request.json

        # Get each data from the request
        category_id = budget_data.get('category_id')
        amount = budget_data.get('amount')

        # Update the budget
        updated_budget = Budget.query.filter_by(id=budget_id, user_id=user_id).update(
            {
                'category_id': category_id,
                'amount': amount
            }
        )

        # Commit the changes to the database
        db.session.commit()

        if updated_budget:
            return jsonify({'message': "Budget updated successfully."}), 200
        else:
            return jsonify({'message': "No Budget Found"}), 404

    except Exception as e:
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while updating budget.'}), 500


# To delete the budget
@budget.route('/delete-budget/<budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id):
    try:

        # Get the current user id
        user_id = get_jwt_identity()

        # Delete the budget directly using a query
        deleted_budget = Budget.query.filter_by(id=budget_id, user_id=user_id).delete()

        # Commit the changes to the database
        db.session.commit()

        if deleted_budget:
            return jsonify({'message': 'Budget deleted successfully.'}), 200
        else:
            return jsonify({'message': 'Budget Not Found'}), 404

    except Exception as e:
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while deleting budget.'}), 500
