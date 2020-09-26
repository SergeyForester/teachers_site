from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
from teachers import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teachers.settings')

app = Celery('teachers', broker="redis://h:p35dfc08bb5d2a659e408bc61dec2d58d0ed77ae61b5cd60e30d48b43e7ff7944@ec2-3-222-186-102.compute-1.amazonaws.com/0")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
