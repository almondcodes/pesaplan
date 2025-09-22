"""
Celery configuration for PesaPlan
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pesaplan.settings.development')

app = Celery('pesaplan')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    'execute-standing-orders': {
        'task': 'pesaplan.apps.standing_orders.tasks.execute_due_standing_orders',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'retry-failed-payments': {
        'task': 'pesaplan.apps.payments.tasks.retry_failed_payments',
        'schedule': 1800.0,  # Run every 30 minutes
    },
    'cleanup-expired-sessions': {
        'task': 'pesaplan.apps.users.tasks.cleanup_expired_sessions',
        'schedule': 3600.0,  # Run every hour
    },
    'send-payment-reminders': {
        'task': 'pesaplan.apps.notifications.tasks.send_payment_reminders',
        'schedule': 86400.0,  # Run daily
    },
}

app.conf.timezone = 'Africa/Nairobi'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
