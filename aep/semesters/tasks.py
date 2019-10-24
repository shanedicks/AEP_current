from __future__ import absolute_import, unicode_literals
import csv
from django.apps import apps
from django.core.mail.message import EmailMessage
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def enforce_attendance_task(section_id):
	logger.info('Activating enrollment {0}'.format(enrollment_id))
	section = apps.get_model('sections', 'Section').objects.get(id=section_id)
	return section.enforce_attendance()
