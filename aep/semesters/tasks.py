from __future__ import absolute_import, unicode_literals
import csv
from django.apps import apps
from django.core.mail.message import EmailMessage
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def enforce_attendance_task(section_id):
	logger.info('Enforcing Attendance for Section {0}'.format(section_id))
	section = apps.get_model('sections', 'Section').objects.get(id=section_id)
	return section.enforce_attendance()

@shared_task
def send_g_suite_info_task(semester_id):
	ElearnRecord = apps.get_model('coaching', 'ElearnRecord')
	students = ElearnRecord.objects.filter(student__classes__section__semester__id=semester_id).distinct()
	logger.info('Sending G Suite Account Info to roster for semester {0}'.format(semester_id))
	for student in students:
		student.send_g_suite_info()
	return True

@shared_task
def validate_enrollments_task(semester_id):
	Semester = apps.get_model('semesters', 'Semester')
	s = Semester.objects.get(id=semester_id)
	s.validate_enrollments()

@shared_task
def refresh_enrollments_task(semester_id):
	Semester = apps.get_model('semesters', 'Semester')
	s = Semester.objects.get(id=semester_id)
	s.refresh_enrollments()
