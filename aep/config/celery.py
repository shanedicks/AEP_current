from __future__ import absolute_import, unicode_literals
import os, ssl
import logging
from celery import Celery

logger = logging.getLogger(__name__)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery('config',
	redis_background_use_ssl = {
	'ssl_cert_reqs': ssl.CERT_NONE
	}
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
	logger.info('Request: {0!r}'.format(self.request))