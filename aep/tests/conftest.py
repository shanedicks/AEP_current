"""Shared fixtures and the two global kill switches.

Greenbean fires Celery tasks from model save() methods (Attendance, Test,
NRSTest, TestAppointment) and reaches out to Google / Plivo / WorkReadyU from
tasks and views. Both are neutered here, autouse, so no test has to remember.
"""
import datetime

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from tests import factories

# Fail loudly rather than silently running against development settings.
# UV_ENV_FILE=.env exports DJANGO_SETTINGS_MODULE=config.settings.development,
# which outranks pytest.ini's ini setting -- only --ds in addopts beats it.
assert settings.SETTINGS_MODULE.endswith('testing'), (
    f'Tests must run against config.settings.testing, got '
    f'{settings.SETTINGS_MODULE!r}. Check --ds in pytest.ini addopts.'
)


class CeleryCallRecorder:
    """Records .delay()/.apply_async() calls instead of dispatching them."""

    def __init__(self):
        self.calls = []

    def record(self, name, args, kwargs):
        self.calls.append((name, args, kwargs))

    def names(self):
        return [name for name, _, _ in self.calls]

    def for_task(self, task_name):
        return [c for c in self.calls if c[0].endswith(task_name)]

    def __len__(self):
        return len(self.calls)


@pytest.fixture(autouse=True)
def celery_calls(monkeypatch):
    """Patch Task.delay/apply_async on the base class.

    Patching the base class rather than each consumer module catches all ~130
    call sites regardless of how the task was imported, with no per-module patch
    list to maintain.
    """
    from celery.app.task import Task

    recorder = CeleryCallRecorder()

    def fake_delay(self, *args, **kwargs):
        recorder.record(self.name, args, kwargs)
        return None

    def fake_apply_async(self, args=None, kwargs=None, **options):
        recorder.record(self.name, tuple(args or ()), dict(kwargs or {}))
        return None

    monkeypatch.setattr(Task, 'delay', fake_delay, raising=False)
    monkeypatch.setattr(Task, 'apply_async', fake_apply_async, raising=False)
    return recorder


# Modules that did `from core.utils import <seam>` and so hold their own
# reference; patching core.utils alone would miss them.
_SEAM_CONSUMERS = {
    'directory_service': ['coaching.tasks', 'sections.tasks', 'semesters.tasks'],
    'drive_service': ['people.views'],
    'classroom_service': ['sections.models', 'sections.tasks', 'sections.views'],
    'state_session': ['people.models', 'people.tasks', 'people.admin'],
}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Block every outbound seam: Google, WorkReadyU, Plivo, and raw HTTP."""
    import importlib

    import core.utils

    def blocked(name):
        def _fail(*args, **kwargs):
            raise AssertionError(f'{name} called in a test; mock it explicitly')
        return _fail

    for seam, consumers in _SEAM_CONSUMERS.items():
        monkeypatch.setattr(core.utils, seam, blocked(seam), raising=False)
        for module_path in consumers:
            try:
                module = importlib.import_module(module_path)
            except ImportError:
                continue
            if hasattr(module, seam):
                monkeypatch.setattr(module, seam, blocked(seam), raising=False)

    import plivo
    monkeypatch.setattr(plivo, 'RestClient', blocked('plivo.RestClient'), raising=False)

    # Catch-all: anything that slips past the named seams fails loudly instead
    # of making a real request.
    from requests.adapters import HTTPAdapter
    monkeypatch.setattr(HTTPAdapter, 'send', blocked('requests HTTPAdapter.send'))


@pytest.fixture
def staff_user(db):
    staff = factories.StaffFactory()
    staff.user.set_password('testpass')
    staff.user.is_staff = True
    staff.user.is_superuser = True
    staff.user.save()
    return staff.user


@pytest.fixture
def auth_client(client, staff_user):
    client.force_login(staff_user)
    return client


@pytest.fixture(scope='session')
def seed_data(django_db_setup, django_db_blocker):
    """One shared dataset for the whole session.

    This is what makes the 269-route sweep cheap: build once, and let each test
    roll back its own writes.

    Must stay idempotent. pytest.ini passes --reuse-db, so this runs against
    whatever the previous session left behind. Every object is keyed on a stable
    unique field (slug / code / title / user) and fetched if already present --
    factories are deliberately not used here, since their sequences produce a
    different value on every run.
    """
    from academics.models import Course, Skill
    from assessments.models import (
        Accuplacer, Clas_E, Gain, HiSET, HiSet_Practice, Tabe, TestAppointment,
        TestEvent, TestHistory,
    )
    from coaching.models import AceRecord, Coaching, ElearnRecord, MeetingNote
    from coaching.models import Profile as CoachingProfile
    from inventory.models import Category, Item, Ticket
    from people.models import Prospect, ProspectNote, Staff, Student
    from sections.models import (
        Attendance, Cancellation, Enrollment, Section, Site,
    )
    from semesters.models import Semester

    with django_db_blocker.unblock():
        system_user, _ = User.objects.get_or_create(
            username='system', defaults={'email': 'system@example.com'}
        )
        teacher_user, _ = User.objects.get_or_create(
            username='seedteacher',
            defaults={'email': 'seedteacher@example.com'},
        )

        semester, _ = Semester.objects.get_or_create(
            title='Seed Semester',
            defaults={
                'start_date': datetime.date(2026, 1, 5),
                'end_date': datetime.date(2026, 5, 15),
                'allowed_absences': 4,
            },
        )
        site, _ = Site.objects.get_or_create(
            code='SD',
            defaults={
                'name': 'Seed Site', 'street_address': '789 Site Blvd',
                'city': 'New Orleans', 'state': 'LA', 'zip_code': '70119',
            },
        )
        online_site, _ = Site.objects.get_or_create(
            code='OL',
            defaults={
                'name': 'Online', 'street_address': '789 Site Blvd',
                'city': 'New Orleans', 'state': 'LA', 'zip_code': '70119',
            },
        )
        course, _ = Course.objects.get_or_create(title='Seed Course')
        skill, _ = Skill.objects.get_or_create(title='Seed Skill')
        course.skills.add(skill)
        category, _ = Category.objects.get_or_create(name='Seed Category')
        item, _ = Item.objects.get_or_create(
            item_id='SEED-ITEM-1',
            defaults={'category': category, 'name': 'Seed Item'},
        )
        teacher, _ = Staff.objects.get_or_create(
            user=teacher_user,
            defaults={
                'first_name': 'Seed', 'last_name': 'Teacher',
                'email': 'seedteacher@example.com', 'phone': '5045551000',
                'street_address_1': '123 Test St', 'city': 'New Orleans',
                'state': 'LA', 'zip_code': '70119',
                'dob': datetime.date(1980, 1, 1),
                'teacher': True, 'active': True,
            },
        )

        sections = []
        for i in range(4):
            section, _ = Section.objects.get_or_create(
                slug=f'sec{i:02d}',
                defaults={
                    'title': f'Seed Section {i}',
                    'semester': semester,
                    'site': site if i < 3 else online_site,
                    'course': course,
                    'teacher': teacher,
                    'program': Section.CCR,
                    'seats': 20,
                    'start_time': datetime.time(9, 0),
                    'end_time': datetime.time(11, 0),
                    'monday': True,
                    'wednesday': True,
                },
            )
            sections.append(section)

        students, enrollments = [], []
        for i in range(6):
            student, _ = Student.objects.get_or_create(
                slug=f'stu{i:02d}',
                defaults={
                    'first_name': 'Seed', 'last_name': f'Student{i}',
                    'email': f'seedstudent{i}@example.com',
                    'phone': '5045552000',
                    'street_address_1': '456 Test Ave', 'city': 'New Orleans',
                    'state': 'LA', 'zip_code': '70119',
                    'dob': datetime.date(1995, 6, 15),
                    'WRU_ID': f'{900000 + i}',
                },
            )
            students.append(student)

            history, _ = TestHistory.objects.get_or_create(
                student=student, defaults={'student_wru': student.WRU_ID}
            )
            Tabe.objects.get_or_create(
                student=history,
                test_date=datetime.date(2026, 1, 10),
                form='11',
                defaults={
                    'read_level': 'M', 'math_level': 'M', 'lang_level': 'M',
                    'read_ss': 520, 'math_comp_ss': 520, 'app_math_ss': 520,
                    'lang_ss': 520, 'total_math_ss': 520, 'total_batt_ss': 520,
                    'read_nrs': '2', 'math_nrs': '2', 'lang_nrs': '2',
                },
            )
            enrollment, _ = Enrollment.objects.get_or_create(
                student=student,
                section=sections[i % len(sections)],
                defaults={'creator': system_user, 'status': Enrollment.ACTIVE},
            )
            enrollments.append(enrollment)
            Attendance.objects.get_or_create(
                enrollment=enrollment,
                attendance_date=datetime.date(2026, 1, 7),
                defaults={
                    'attendance_type': Attendance.PRESENT,
                    'time_in': datetime.time(9, 0),
                    'time_out': datetime.time(11, 0),
                },
            )

        # Satellite records that detail views reverse into. Only the first
        # student needs them -- the sweep always takes objects.first().
        first_student = students[0]
        AceRecord.objects.get_or_create(student=first_student)
        ElearnRecord.objects.get_or_create(student=first_student)
        prospect, _ = Prospect.objects.get_or_create(
            first_name='Seed',
            last_name='Prospect',
            defaults={
                'phone': '5045553000',
                'dob': datetime.date(1994, 3, 2),
                'contact_preference': 'Email',
                'student': first_student,
            },
        )

        # coaching.Profile has ~19 required free-text/choice fields; fill them
        # generically rather than spelling out values the sweep never reads.
        if not CoachingProfile.objects.filter(student=first_student).exists():
            profile_kwargs = {}
            for field in CoachingProfile._meta.get_fields():
                if not field.concrete or field.primary_key:
                    continue
                if field.blank or field.null or field.has_default():
                    continue
                if field.name == 'student':
                    continue
                choices = getattr(field, 'choices', None)
                if choices:
                    profile_kwargs[field.name] = choices[0][0]
                else:
                    profile_kwargs[field.name] = 'seed'
            CoachingProfile.objects.create(student=first_student, **profile_kwargs)

        # One row per model that a detail/update route reverses into. The sweep
        # always takes objects.first(), so one of each is enough.
        first_history = TestHistory.objects.get(student=first_student)

        test_event, _ = TestEvent.objects.get_or_create(
            title='Seed Test Event',
            defaults={
                'test': 'TABE',
                'seats': 20,
                'start': timezone.make_aware(
                    datetime.datetime(2026, 2, 3, 9, 0)
                ),
                'end': timezone.make_aware(
                    datetime.datetime(2026, 2, 3, 12, 0)
                ),
            },
        )
        TestAppointment.objects.get_or_create(
            student=first_student, event=test_event
        )
        clas_e, _ = Clas_E.objects.get_or_create(
            student=first_history,
            test_date=datetime.date(2026, 1, 12),
            form='A',
            defaults={'read_level': 'M', 'read_nrs': '2'},
        )
        Gain.objects.get_or_create(
            student=first_history,
            test_date=datetime.date(2026, 1, 13),
            form='A',
            subject='Math',
            defaults={'scale_score': 500, 'grade_eq': 8.0, 'nrs': '2'},
        )
        HiSET.objects.get_or_create(
            student=first_history,
            test_date=datetime.date(2026, 1, 14),
            subject='Math',
            defaults={'score': 12},
        )
        HiSet_Practice.objects.get_or_create(
            student=first_history,
            test_date=datetime.date(2026, 1, 15),
            subject='Math',
            defaults={
                'grade': 'Prepared',
                'score': 12,
                'reported_by': system_user,
            },
        )
        Accuplacer.objects.get_or_create(
            student=first_history, test_date=datetime.date(2026, 1, 16)
        )

        coaching_rel, _ = Coaching.objects.get_or_create(
            coachee=first_student,
            coach=teacher,
            defaults={
                'start_date': timezone.make_aware(
                    datetime.datetime(2026, 1, 6, 9, 0)
                ),
                'active': True,
            },
        )
        MeetingNote.objects.get_or_create(
            coaching=coaching_rel,
            meeting_date=datetime.date(2026, 1, 20),
            defaults={'meeting_type': 'Open Coaching'},
        )

        Ticket.objects.get_or_create(
            item=item,
            issued_date=datetime.date(2026, 1, 8),
            defaults={'student': first_student},
        )
        ProspectNote.objects.get_or_create(
            prospect=prospect,
            contact_date=datetime.date(2026, 1, 9),
            defaults={'contact_method': 'Call', 'notes': 'Seed note'},
        )
        cancellation, _ = Cancellation.objects.get_or_create(
            section=sections[0],
            cancellation_date=datetime.date(2026, 2, 10),
            defaults={'cancelled_by': system_user},
        )
        first_tabe = Tabe.objects.filter(student=first_history).first()

        return {
            'semester': semester,
            'site': site,
            'course': course,
            'skill': skill,
            'category': category,
            'item': item,
            'teacher': teacher,
            'prospect': prospect,
            'test_event': test_event,
            'tabe': first_tabe,
            'clas_e': clas_e,
            'cancellation': cancellation,
            'sections': sections,
            'students': students,
            'enrollments': enrollments,
            'system_user': system_user,
        }
