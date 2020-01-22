from __future__ import absolute_import, unicode_literals
import csv
from django.apps import apps
from django.core.mail.message import EmailMessage
from django.db.models import Sum
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def event_attendance_report_task(event_id, email_address):
	filename = '{0}_attendance_report.csv'.format(event_id)
	with open(filename, 'w', newline='') as out:
		writer = csv.writer(out)
		event = apps.get_model('assessments', 'TestEvent').objects.get(id=event_id)
		students = event.students.all()
		headers = [
			'appt_id',
			'WRU ID',
			'Last Name',
			'First Name',
			'Phone',
			'Email',
			'Date',
			'Attendance',
			'Hours'
		]
		writer.writerow(headers)

		for appt in students:
			student = appt.student
			data = [
				appt.id,
				student.WRU_ID,
				student.last_name,
				student.first_name,
				student.phone,
				student.email,
				appt.attendance_date,
				appt.attendance_type,
				appt.hours()
			]
			writer.writerow(data)

	email = EmailMessage(
		'Test Event Attendance Report',
		"Per-event report containing student contact information and attendance status",
		'reporter@dccaep.org', 
		[email_address]
	)
	email.attach_file(filename)
	email.send()

@shared_task
def orientation_status_task(student_id):
	student = apps.get_model('people', 'Student').objects.get(id=student_id)
	student.orientation = 'C'
	student.save()
