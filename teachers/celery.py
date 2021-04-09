from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

from teachers import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teachers.settings')

app = Celery('teachers',
             broker=f"{settings.CELERY_BROKER_URL}/0")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')



app.conf.beat_schedule = {
	'check-teachers-bills': {
		'task': 'lesson_confirmation_app.tasks.check_teachers_bills',
		'schedule': crontab(hour="7", minute="40"),
	},
	'lesson-confirmation': {
		'task': 'lesson_confirmation_app.tasks.lesson_complete_confirmation',
		'schedule': crontab(minute='*/30'),
	}
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)
