# PesaPlan - Automated Recurring Payments Platform
from .celery import app as celery_app

__all__ = ('celery_app',)