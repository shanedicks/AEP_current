from django.core.management.base import BaseCommand
from core.utils import state_session
from people.models import WIOA

class Command(BaseCommand):

	def handle(self, *args, **kwargs):
		s = state_session()
		new_students = WIOA.objects.filter(student__WRU_ID=None)
		self.stdout.write("Preparing to send {0} students to state".format(new_students.count()))
		for wioa in new_students:
			wioa.send(s)
