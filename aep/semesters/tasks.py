from __future__ import absolute_import, unicode_literals
import csv
from apiclient.errors import HttpError
from django.apps import apps
from django.core.mail.message import EmailMessage
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from core.utils import g_suite_service

logger = get_task_logger(__name__)

@shared_task
def semester_begin_task(semester_id):
	semester = apps.get_model('semesters', 'Semester').objects.get(id=semester_id)
	logger.info('Beginning Semester{0}'.format(semester.title))
	for section in semester.sections.all():
		section.begin()
	return True

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

@shared_task
def send_survey_task(survey_id):
	survey = apps.get_model('semesters', 'Survey').objects.get(id=survey_id)
	logger.info('Sending survey {0}'.format(survey.title))
	survey.send_survey()

@shared_task
def create_missing_g_suite_task(semester_id):
	semester = apps.get_model('semesters', 'Semester').objects.get(semester_id)
	Student = apps.get_model('people', 'Student')
	Elearn = apps.get_model('coaching', 'ElearnRecord')
	logger.info("Creating G Suite Service")
	service = g_suite_service()
	students = Student.objects.filter(classes__section__semester=semester).distinct()
	need_elearn = students.filter(elearn_record=None)
	logger.info("{0} students need elearn records".format(need_elearn.count()))
	for student in need_elearn:
		Elearn.objects.create(
			student=student,
			intake_date=timezone.now().date()
		)
		logger.info("Created elearn record for {0}".format(student))
	logger.info('Creating missing GSuite accounts for {0}'.format(semester.title))
	for student in students:
		logger.info("Creating GSuite account for {0}".format(student))
		try:
			student.elearn_record.create_g_suite_account()
		except HttpError as e:
			logger.info("{0}".format(e))