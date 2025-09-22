from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE','Uni_Automation.settings')

app=Celery('Uni_Automation')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

