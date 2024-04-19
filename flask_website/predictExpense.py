from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
import pytz
import numpy as np
from sklearn.linear_model import LinearRegression

# Initialize the scheduler
scheduler = BackgroundScheduler()


# Function to train and predict expenses
def train_and_predict_expenses(db, app):

    from .models import User, Expense, Notification
    with app.app_context():
        with db.session.begin():
            # Get all users
            users = User.query.all()

            # For each user's budget
            for user in users:
                for budget in user.budgets:

                    # Get the current date and time in Malaysia time zone
                    malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')
                    today_malaysia = datetime.datetime.now(malaysia_timezone)

                    # Convert the Malaysia time to UTC time
                    today_utc = today_malaysia.astimezone(pytz.utc)

                    # Set the time to Malaysia time 12:00 AM
                    today_utc_midnight = today_utc.replace(hour=0, minute=0, second=0, microsecond=0)

                    # Query expenses for the user before the first day of current month
                    expenses = Expense.query.filter(Expense.user_id == user.id,
                                                    Expense.date < today_utc_midnight,
                                                    Expense.category_id == budget.category_id).all()

                    # Dictionary to store total expenses for each year and month
                    monthly_total_expenses = defaultdict(float)

                    # Iterate over the expenses to sum up total expenses for each year and month
                    for expense in expenses:
                        # Convert the UTC date to Malaysia time zone
                        date_malaysia = expense.date.astimezone(pytz.timezone('Asia/Kuala_Lumpur'))

                        # Get the year and month
                        year_month = (date_malaysia.year, date_malaysia.month)

                        # Add the expense amount to the corresponding year and month
                        monthly_total_expenses[year_month] += float(expense.amount)

                    # Sort the total expenses by year and month in ascending order
                    sorted_monthly_total_expenses = sorted(monthly_total_expenses.items())

                    # Extract the amounts into an array, rounded to 2 decimal places
                    history_expenses = [amount for _, amount in sorted_monthly_total_expenses]

                    print(user.username, budget.category.name)
                    print(history_expenses)

                    X_train = np.arange(len(history_expenses)).reshape(-1, 1)  # Month index as feature
                    y_train = history_expenses  # Historical monthly expenses as target

                    # Train the model using the data
                    model = LinearRegression()
                    model.fit(X_train, y_train)

                    # To predict the next month which already is current month possible value based on the past
                    # months' total amount
                    next_month_index = len(history_expenses)
                    next_month_expense = model.predict([[next_month_index]])
                    next_month_expense = round(float(next_month_expense[0]), 2)

                    # print('prediction:', next_month_expense)

                    # If the predicted total expense exceeds the budget, then send notification to tell user
                    if next_month_expense > budget.amount:
                        # Create a notification indicating the budget may be exceeded
                        notification = Notification(
                            title="Budget Exceedance Prediction Alert",
                            message=f"The predicted expense for {budget.category.name} in the current month suggests "
                                    f"a rising trend. Consider adjusting your spending to avoid exceeding the "
                                    f"budget.\n\nNote: Please be aware that this prediction is based on historical "
                                    f"data and may not be entirely accurate.",
                            user_id=user.id
                        )
                        db.session.add(notification)

                    # Explicitly delete the model
                    del model

            # Commit the changes to the database
            db.session.commit()


# Start the scheduler
def start_predict_expense_scheduler(db, app):
    # Define the cron trigger to execute the task on the first day of each month at 12:15 AM
    trigger = CronTrigger(day='19', hour='18', minute='10')

    # Add the job with the specified trigger
    scheduler.add_job(train_and_predict_expenses, trigger, args=[db, app])

    # Start the scheduler
    scheduler.start()
