from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


# Function to print a message
def print_message():
    print("Scheduled task executed at:", datetime.now())

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(print_message, trigger='interval', seconds=10)
scheduler.start()