from django.core.management.base import BaseCommand
from django.utils import timezone
from semesters.models import Semester
from semesters.tasks import attendance_reminder_task

class Command(BaseCommand):

	def handle(self, *args, **kwargs):
		now = timezone.now()
		if now.weekday() == 4:
			semesters = Semester.objects.filter(
				start_date__lte=now,
				end_date__gte=now
			)
			for semester in semesters:
				if semester.report_to:
					attendance_reminder_task.delay(
						semester_id_list=[semester.id], 
						email_address=semester.report_to,
						send_mail=True)
				else:
					for section in semester.get_sections():
						section.attendance_reminder(send_mail=True)
