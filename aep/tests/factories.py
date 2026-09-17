"""factory_boy factories for the Student/Section/Enrollment/Attendance spine.

Values are deterministic and domain-valid on purpose. Randomised CharField junk
would break the logic most worth testing: assessments/rules.py compares NRS
levels as strings (``math_nrs__gte=1`` on a CharField), and the state-code
converters in people/models.py are value-semantic. Use factory.Sequence for
uniqueness, not Faker, for anything the domain reads back.
"""
import datetime

import factory
from django.contrib.auth.models import User

from academics.models import Course
from assessments.models import Tabe, TestHistory
from people.models import RecordRelease, Staff, Student
from sections.models import Attendance, Enrollment, Section, Site
from semesters.models import Semester


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    first_name = 'Test'
    last_name = factory.Sequence(lambda n: f'User{n}')


class SystemUserFactory(UserFactory):
    """Single shared user for django-author creator/modified_by fields.

    django_get_or_create on username means the whole suite reuses one row
    instead of inventing a throwaway User per Enrollment.
    """
    username = 'system'


class StaffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Staff

    user = factory.SubFactory(UserFactory)
    first_name = 'Staff'
    last_name = factory.Sequence(lambda n: f'Member{n}')
    email = factory.LazyAttribute(lambda o: f'{o.last_name.lower()}@example.com')
    phone = '5045551000'
    street_address_1 = '123 Test St'
    city = 'New Orleans'
    state = 'LA'
    zip_code = '70119'
    dob = datetime.date(1980, 1, 1)
    teacher = True
    active = True


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    first_name = 'Student'
    last_name = factory.Sequence(lambda n: f'Test{n}')
    email = factory.LazyAttribute(lambda o: f'{o.last_name.lower()}@example.com')
    phone = '5045552000'
    street_address_1 = '456 Test Ave'
    city = 'New Orleans'
    state = 'LA'
    zip_code = '70119'
    dob = datetime.date(1995, 6, 15)
    WRU_ID = factory.Sequence(lambda n: f'{900000 + n}')


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Site
        django_get_or_create = ('code',)

    # Site.code is max_length=2 -- keep the sequence two characters wide.
    code = factory.Sequence(lambda n: f'{n % 100:02d}')
    name = factory.Sequence(lambda n: f'Test Site {n}')
    street_address = '789 Site Blvd'
    city = 'New Orleans'
    state = 'LA'
    zip_code = '70119'


class SemesterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Semester
        django_get_or_create = ('title',)

    title = factory.Sequence(lambda n: f'Test Semester {n}')
    start_date = datetime.date(2026, 1, 5)
    end_date = datetime.date(2026, 5, 15)
    allowed_absences = 4


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
        django_get_or_create = ('title',)

    title = factory.Sequence(lambda n: f'Test Course {n}')


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Section

    title = factory.Sequence(lambda n: f'Test Section {n}')
    semester = factory.SubFactory(SemesterFactory)
    teacher = factory.SubFactory(StaffFactory)
    course = factory.SubFactory(CourseFactory)
    # site is NOT optional in practice: Enrollment.activate() dereferences
    # self.section.site.code and will AttributeError on a null site.
    site = factory.SubFactory(SiteFactory)
    program = Section.CCR
    seats = 20
    start_time = datetime.time(9, 0)
    end_time = datetime.time(11, 0)
    monday = True
    wednesday = True


class EnrollmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Enrollment

    student = factory.SubFactory(StudentFactory)
    section = factory.SubFactory(SectionFactory)
    creator = factory.SubFactory(SystemUserFactory)
    status = Enrollment.ACTIVE


class AttendanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attendance

    enrollment = factory.SubFactory(EnrollmentFactory)
    attendance_date = datetime.date(2026, 1, 7)
    attendance_type = Attendance.PRESENT
    time_in = datetime.time(9, 0)
    time_out = datetime.time(11, 0)


class TestHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TestHistory

    student = factory.SubFactory(StudentFactory)
    student_wru = factory.LazyAttribute(lambda o: o.student.WRU_ID)


class TabeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tabe

    # NB: Tabe.student is a FK to TestHistory, not to Student.
    student = factory.SubFactory(TestHistoryFactory)
    test_date = datetime.date(2026, 1, 10)
    form = '11'
    read_level = 'M'
    math_level = 'M'
    lang_level = 'M'
    read_ss = 520
    math_comp_ss = 520
    app_math_ss = 520
    lang_ss = 520
    total_math_ss = 520
    total_batt_ss = 520
    read_nrs = '2'
    math_nrs = '2'
    lang_nrs = '2'


class RecordReleaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecordRelease

    student = factory.SubFactory(StudentFactory)
    released_to = factory.Sequence(lambda n: f'Seed Org {n}')
    all_information = True
