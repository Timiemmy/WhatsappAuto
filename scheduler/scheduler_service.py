# scheduler/scheduler_service.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from django_apscheduler.models import DjangoJobExecution
import sys
import pywhatkit as pwk
from datetime import datetime
from .models import ScheduledMessage
import time


def send_pending_messages():
    """
    Function to check for messages that need to be sent now
    """
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    messages_to_send = ScheduledMessage.objects.filter(
        sent=False,
        send_hour=current_hour,
        send_minute=current_minute
    )

    for msg in messages_to_send:
        try:
            # Send the message
            pwk.sendwhatmsg_instantly(
                msg.phone_number,
                msg.message,
                wait_time=15  # 15 seconds wait time
            )
            msg.sent = True
            msg.save()
            print(f"Sent message to {msg.phone_number}")
            time.sleep(10)  # Give time between messages
        except Exception as e:
            print(f"Error sending message to {msg.phone_number}: {e}")


def start():
    """
    Start the scheduler
    """
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Add the job to the scheduler
    scheduler.add_job(
        send_pending_messages,
        trigger=CronTrigger(minute="*"),  # Run every minute
        id="send_pending_messages",  # Unique ID for this job
        max_instances=1,  # Only run one instance at a time
        replace_existing=True,  # Replace if already exists
    )

    # Delete old job executions to prevent database from growing indefinitely
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )

    try:
        print("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        print("Stopping scheduler...")
        scheduler.shutdown()
        print("Scheduler shut down successfully!")


def delete_old_job_executions(max_age=604_800):
    """
    Delete old job executions to prevent database from growing too large
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
