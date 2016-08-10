from django.test import TestCase
from people.models import Student, Staff
from autofixture import AutoFixture


class StudentTestCase(TestCase):

    def test_generators(self):
        student_fixture = AutoFixture(Student, generate_fk=True)
        students = student_fixture.create(2)

        self.assertNotEqual(students[0].slug, students[1].slug)
        self.assertNotEqual(students[0].AEP_ID, students[1].AEP_ID)

        print('Student Slug 1-', students[0].slug)
        print('Student Slug 2-', students[1].slug)
        print('ID 1-', students[0].AEP_ID)
        print('ID 2-', students[1].AEP_ID)


class StaffTestCase(TestCase):

    def test_generators(self):
        staff_fixture = AutoFixture(Staff, generate_fk=True)
        staff = staff_fixture.create(2)

        self.assertNotEqual(staff[0].slug, staff[1].slug)

        print('Staff Slug1-', staff[0].slug)
        print('Staff Slug2-', staff[1].slug)
