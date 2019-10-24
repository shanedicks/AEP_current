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
def participation_detail_task():
	enrollments = apps.get_model('sections', 'Enrollment').objects.all()
	sites = apps.get_model('sections', 'Site').objects.all()
	students = apps.get_model('people', 'Student').objects.filter(duplicate=False)
	with open('participation_detail_report.csv', 'w', newline='') as out:
		writer = csv.writer(out)

		headers = [
			'WRU_ID',
			'Name',
			'Total',
			'completed',
			'MW',
			'completed',
			'TR',
			'completed',
			'Morning',
			'completed',
			'Afternoon',
			'completed',
			'Evening',
			'completed',
		]
		for site in sites:
			headers.extend([site.code, 'completed'])
		writer.writerow(headers)

		for student in students:
			enrolled = student.classes.all()
			if enrolled.count() == 0:
				continue
			completed = enrolled.filter(status='C')
			data = [
				student.WRU_ID,
				", ".join([student.last_name, student.first_name]),
				enrolled.count(),
				completed.count(),
				enrolled.filter(section__monday=True).count(),
				completed.filter(section__monday=True).count(),
				enrolled.filter(section__tuesday=True).count(),
				completed.filter(section__tuesday=True).count(),
				enrolled.filter(section__start_time__lte='11:30').count(),
				completed.filter(section__start_time__lte='11:30').count(),
				enrolled.filter(section__start_time__gt='11:30', section__start_time__lt='16:00').count(),
				completed.filter(section__start_time__gt='11:30', section__start_time__lt='16:00').count(),
				enrolled.filter(section__start_time__gte='16:00').count(),
				completed.filter(section__start_time__gte='16:00').count(),
			]
			for site in sites:
				data.append(enrolled.filter(section__site=site).count())
				data.append(completed.filter(section__site=site).count())

			writer.writerow(data)

	email = EmailMessage(
		'Student Participation Report',
		'Report on student enrollment and class completion for various days, times, and sites',
		'reporter@dccaep.org',
		['shane.dicks1@gmail.com']
	)
	email.attach_file('participation_detail_report.csv')
	email.send()

@shared_task
def roster_to_classroom_task(section_id):
	Section = apps.get_model('sections', 'Section')
	section = Section.objects.get(id=section_id)
	logger.info('Exporting roster for {0} to google classroom'.format(section))
	return section.roster_to_classroom()

@shared_task
def missed_class_report_task():
	pass
