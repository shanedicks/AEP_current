import time
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from sections.tasks import create_classroom_section_task, add_TA_task
from semesters.models import Semester
from semesters.tasks import create_missing_g_suite_task, first_class_warning_report_task

logger = logging.getLogger(__name__)


class Command(BaseCommand):

	def handle(self, *args, **kwargs):
		now = timezone.now()
		active = Semester.objects.filter(
			start_date__lte=now + timedelta(days=2),
			end_date__gte=now
		)
		logger.info(f"Beginning Semester Admin Process")
		create_classroom_sections_group = Semester.objects.filter(start_date=now + timedelta(days=7))
		for semester in create_classroom_sections_group:
			section_ids = [s.id for s in semester.get_sections() if s.g_suite_id == '']
			create_classroom_section_task.delay(section_ids)
			time.sleep(300)
			add_TA_task.delay(section_ids)
		for semester in active.filter(start_date__gte=now - timedelta(days=17)):
			if now.weekday() in [1, 2, 3, 4]:
				first_class_warning_report_task.delay(semester.id)
				time.sleep(5)
			if now.weekday() == 4:
				semester.waitlist()
				time.sleep(10)
		for semester in active.filter(start_date__gte=now - timedelta(days=45)):
			create_missing_g_suite_task.delay(semester.id)
			time.sleep(10)
			semester.begin()
			semester.roster_to_classroom()
			time.sleep(10)
		for semester in active.filter(start_date__lt=now - timedelta(days=14)):
			semester.enforce_attendance()
		end_semester_group = Semester.objects.filter(end_date=now - timedelta(days=14))
		for semester in end_semester_group:
			semester.end()
		logger.info(f"Semester Admin Process Complete")
