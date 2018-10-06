from __future__ import absolute_import, unicode_literals
from django.apps import apps
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def get_enrollment(enrollment_id):
	Enrollment = apps.get_model('sections', 'Enrollment')
	return Enrollment.objects.get(id=enrollment_id)

@shared_task
def activate_task(enrollment_id):
	logger.info('Activating enrollment {0}'.format(enrollment_id))
	enrollment = get_enrollment(enrollment_id)
	return enrollment.activate()

@shared_task
def end_task(enrollment_id):
	logger.info('Ending enrollment {0}'.format(enrollment_id))
	enrollment = get_enrollment(enrollment_id)
	if student.status == student.ACTIVE:
		student.status = student.COMPLETED
	return student.save()

@shared_task
def drop_task(enrollment_id):
	logger.info('Dropping enrollment {0}'.format(enrollment_id))
	enrollment = get_enrollment(enrollment_id)
	return enrollment.attendance_drop() 