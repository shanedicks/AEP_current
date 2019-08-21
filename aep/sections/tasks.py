from __future__ import absolute_import, unicode_literals
import csv
from django.apps import apps
from django.core.mail.message import EmailMessage
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
	if enrollment.status == enrollment.ACTIVE:
		enrollment.status = enrollment.COMPLETED
	return enrollment.save()

@shared_task
def drop_task(enrollment_id):
	logger.info('Dropping enrollment {0}'.format(enrollment_id))
	enrollment = get_enrollment(enrollment_id)
	return enrollment.attendance_drop()

@shared_task
def report_task():
	with open('out.csv', 'w', newline='') as out:
		writer = csv.writer(out)
		writer.writerow(['This', 'is', 'a', 'test'])
		writer.writerow(['Obviously', 'not', 'real', 'data'])
	email = EmailMessage('Async Reports Test', "Can a worker email a csv attachment? If you're reading this, it can.", 'reporter@dccaep.org', ['jalehrman@gmail.com', 'shane.dicks1@gmail.com'])
	email.attach_file('out.csv')
	email.send()

@shared_task
def roster_to_classroom_task(section_id):
	Section = apps.get_model('sections', 'Section')
	section = Section.objects.get(id=section_id)
	logger.info('Exporting roster for {0} to google classroom'.format(section))
	return section.roster_to_classroom()
