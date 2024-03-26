from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import extract
from .models import User, Budget, Expense, Notification
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


# To check the current month budget will be exceeded or not
@budget.route('/check-monthly-budget', methods=['POST'])
@jwt_required()
def check_monthly_budget_with_expense():
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

            # Compare total expense with the budget amount
            if total_expense < budget.amount:
                # Reset is_exceed field of the budget to False
                budget.is_exceed = False

            db.session.commit()

            # Check if the budget is less than the total expenses
            if budget.amount < total_expense:
                # Send a notification indicating that the budget is less than the expenses
                title = 'Budget Below Total Expenses'
                message = f'Your budget for {budget.category.name} is currently lower than your total expenses for ' \
                          f'this month. Please review your budget allocation to ensure it covers your spending needs.'

                notification = Notification(
                    title=title,
                    message=message,
                    user_id=user_id
                )
                db.session.add(notification)
                db.session.commit()

        return jsonify({'message': 'Monthly budget have been checked against the expense.'}), 200

    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()

        logger.error(e)
        return jsonify({'message': 'An error occurred while checking the monthly expense and budget.'}), 500
