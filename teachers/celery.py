from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

from teachers import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teachers.settings')

app = Celery('teachers',
             broker="redis://h:pbad2e057a5c4a1a0039c384db46ca2bd1b5cd1f42edd793f7fe1ae484fd9de71@ec2-54-228-162-89.eu-west-1.compute.amazonaws.com:7659/0")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    'check-teachers-bills': {
        'task': 'lesson_confirmation_app.tasks.check_teachers_bills',
        'schedule': crontab(minute=1),
    },
}
app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))
