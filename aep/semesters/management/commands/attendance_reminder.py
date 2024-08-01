import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from semesters.models import Semester
from semesters.tasks import attendance_reminder_task

logger = logging.getLogger(__name__)

class Command(BaseCommand):

	def handle(self, *args, **kwargs):
		now = timezone.now()
		if now.weekday() == 4:
			semesters = Semester.objects.filter(
				start_date__lte=now,
				end_date__gte=now
			)
			for semester in semesters:
				logger.info(f"Attendance reminder for {semester}")
				if semester.report_to:
					attendance_reminder_task.delay(
						semester_id_list=[semester.id],
						email_address=semester.report_to,
						send_mail=True)
					logger.info(f"Reported to {semester.report_to}")
				else:
					for section in semester.get_sections():
						section.attendance_reminder(send_mail=True)
						logger.info(f"Report not sent")
