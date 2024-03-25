from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Initialize the scheduler
scheduler = BackgroundScheduler()


# Function to update is_exceed to 0
def update_is_exceed(db, app):
    from .models import Budget
    with app.app_context():
        with db.session.begin():
            Budget.query.update({"is_exceed": False})
            db.session.commit()
        print("is_exceed updated to 0 at:", datetime.now())


# Start the scheduler
def start_scheduler(db, app):
    # Define the cron trigger to execute on the first day of the month at 12:00 AM
    trigger = CronTrigger(day='1', hour='0')

    # Add the job with the specified trigger
    scheduler.add_job(update_is_exceed, trigger, args=[db, app])

    # Start the scheduler
    scheduler.start()
