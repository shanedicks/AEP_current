from __future__ import absolute_import, unicode_literals
import csv
from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.mail.message import EmailMessage
from django.utils import timezone

logger = get_task_logger(__name__)

@shared_task
def get_elearn_record(elearn_record_id):
	ElearnRecord = apps.get_model('coaching', 'ElearnRecord')
	return ElearnRecord.objects.get(id=elearn_record_id)

@shared_task
def elearn_status_task(elearn_record_id):
	loggerl.info("Updating status of ElearnRecord {0}".format(elearn_record_id))
	elearn_record = get_elearn_record(elearn_record_id)
	elearn_record.elearn_status = 'Pending'
	elearn_record.status_updated = timezone.now()
	elearn_record.save()
	return True

@shared_task
def coaching_export_task(email):
	coachings = apps.get_model('coaching', 'Coaching').objects.filter(active=True)
	with open('coaching_export.csv', 'w', newline='') as out:
		writer = csv.writer(out)
		headers = [
			'Student WRU ID',
			'Student Last Name',
			'Student First Name',
			'Coach ID',
			'Coach Last Name',
			'Coach First Name',
			'Coaching Type',
			'Start Date'
		]
		writer.writerow(headers)

		for coaching in coachings:
			s = [
				coaching.coachee.WRU_ID,
				coaching.coachee.last_name,
				coaching.coachee.first_name,
				coaching.coach,
				coaching.coach.last_name,
				coaching.coach.first_name,
				coaching.coaching_type,
				coaching.start_date,
			]
			writer.writerow(s)
	email = EmailMessage(
		"Coaching Export",
		"Here is the coaching export you requested",
		'reporter@dccaep.org',
		[email]
	)
	email.attach_file('coaching_export.csv')
	email.send()
