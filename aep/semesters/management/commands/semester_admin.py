import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from sections.tasks import create_classroom_sections_task, add_TA_task
from semesters.models import Semester
from semesters.tasks import create_missing_g_suite


class Command(BaseCommand):

	def handle(self, *args, **kwargs):
		now = timezone.now()
		active = Semester.objects.filter(
			start_date__lte=now + timedelta(days=2),
			end_date__gte=now
		)
		create_classroom_sections_group = Semester.objects.filter(start_date=now + timedelta(days=7))
		for semester in create_classroom_sections_group:
			section_ids = [s.id for s in semester.get_sections()]
			create_classroom_section_task(section_ids)
			time.sleep(10)
			add_TA_task(section_ids)
		for semester in active.filter(start_date__gte=now - timedelta(days=14)):
			create_missing_g_suite.delay(semester.id)
			time.sleep(10)
			if now.weekday() == 4:
				semester.waitlist()
				time.sleep(10)
			semester.begin()
			semester.roster_to_classroom()
			time.sleep(10)
		for semester in active.filter(start_date__lt=now - timedelta(days=14)):
			semester.enforce_attendance()
		end_semester_group = Semester.objects.filter(end_date=now - timedelta(days=14))
		for semester in end_semester_group:
			semester.end()
