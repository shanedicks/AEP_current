from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

def copy_roster(old_section, new_section, user=None):
	Enrollment = apps.get_model('sections', 'Enrollment')
	User = get_user_model()

	if not user:
		user = old_section.teacher.user

	student_list = [
		student.student for student
		in old_section.students.exclude(
			status__in=[Enrollment.DROPPED, Enrollment.WITHDRAWN]
		)
	]

	for student in student_list:
		try:
			Enrollment.objects.create(
				creator=user,
				student=student,
				section=new_section
			)
		except IntegrityError:
			pass
