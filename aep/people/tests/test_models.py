from django.test import TestCase
from people.models import Student, Staff
from autofixture import AutoFixture


class StudentTestCase(TestCase):
    student_fixture = AutoFixture(Student, generate_fk=true)
    students = student_fixture.create(2)

    def setUp(self):
        student_1 = Student.objects.get(pk=1)
        student_2 = Student.objects.get(pk=2)

        self.assertNotEqual(student_1.slug, student_2.slug)
        self.assertNotEqual(student_1.AEP_ID, student_2.AEP_ID)
