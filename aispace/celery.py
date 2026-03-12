import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aispace.settings')

app = Celery('aispace')

# Read Celery configuration from Django settings, using the CELERY_ namespace.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all INSTALLED_APPS.
app.autodiscover_tasks()
