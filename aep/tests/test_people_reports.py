"""Student-population reports: creation-window boundaries, summary and activity reports."""
import csv
import datetime
import io

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from assessments.models import TestAppointment, TestEvent
from people.models import Prospect, ProspectNote, Student
from people.tasks import (
    intake_retention_report_task, student_activity_report_task,
    students_created_between, summary_report_task,
)
from sections.models import Enrollment
from tests.factories import (
    AttendanceFactory, EnrollmentFactory, StudentFactory, TestHistoryFactory,
)

pytestmark = pytest.mark.django_db

D = datetime.date


def attachment_rows(message):
    _, content, _ = message.attachments[0]
    return list(csv.reader(io.StringIO(content)))


def rows_by_wru(rows):
    return {row[0]: row for row in rows[1:]}


@pytest.fixture
def cohort():
    """Students created in pk order. `merged` re-registered after c and carries
    an older record's backdated intake, as full_merge leaves it."""
    a = StudentFactory(intake_date=D(2001, 1, 10))
    b = StudentFactory(intake_date=D(2001, 2, 10))
    c = StudentFactory(intake_date=D(2001, 3, 10))
    merged = StudentFactory(intake_date=D(2000, 6, 1))
    e = StudentFactory(intake_date=D(2001, 4, 10))
    qs = Student.objects.filter(pk__in=[s.pk for s in (a, b, c, merged, e)])
    return qs, a, b, c, merged, e


class TestStudentsCreatedBetween:

    def test_boundaries_need_not_fall_on_intake_days(self, cohort):
        qs, a, b, c, merged, e = cohort
        result = students_created_between(qs, D(2001, 2, 1), D(2001, 2, 28))
        assert set(result) == {b}

    def test_backdated_survivor_does_not_stretch_window(self, cohort):
        qs, a, b, c, merged, e = cohort
        result = students_created_between(qs, D(2001, 1, 1), D(2001, 2, 28))
        assert set(result) == {a, b}

    def test_backdated_survivor_counts_where_it_was_created(self, cohort):
        qs, a, b, c, merged, e = cohort
        result = students_created_between(qs, D(2001, 3, 1), D(2001, 12, 31))
        assert set(result) == {c, merged, e}

    def test_open_ended_window(self, cohort):
        qs, a, b, c, merged, e = cohort
        result = students_created_between(qs, D(2001, 4, 1), D(2030, 1, 1))
        assert set(result) == {e}

    def test_no_intakes_after_from_date(self, cohort):
        qs, *_ = cohort
        assert not students_created_between(qs, D(2002, 1, 1), D(2002, 12, 31)).exists()


def test_summary_report_runs_without_boundary_intakes():
    student = StudentFactory(intake_date=D(2001, 1, 10))
    AttendanceFactory(enrollment=EnrollmentFactory(student=student), attendance_date=D(2001, 1, 15))

    summary_report_task('2001-01-01', '2001-01-31', 'staff@example.com')

    rows = rows_by_wru(attachment_rows(mail.outbox[0]))
    assert student.WRU_ID in rows


def test_intake_retention_report_runs_without_boundary_intakes():
    # Future intake: the reused test DB holds lower-pk students with recent
    # intakes, and the window relies on intake order following pk order.
    student = StudentFactory(intake_date=D(2030, 1, 10))

    intake_retention_report_task('2030-01-01', '2030-01-31', 'staff@example.com')

    assert student.WRU_ID in mail.outbox[0].attachments[0][1]


def make_event(test, start):
    start = timezone.make_aware(datetime.datetime.combine(start, datetime.time(9)))
    return TestEvent.objects.create(
        test=test, seats=20, start=start, end=start + datetime.timedelta(hours=3)
    )


class TestStudentActivityReport:

    def run(self, cutoff='2021-11-18'):
        student_activity_report_task(cutoff, 'staff@example.com')
        return attachment_rows(mail.outbox[-1])

    def test_header(self):
        header = self.run()[0]
        assert header[-2:] == ['Last Activity', 'Active Since 2021-11-18']

    def test_dead_file(self):
        student = StudentFactory(intake_date=D(2015, 3, 1))
        row = rows_by_wru(self.run())[student.WRU_ID]
        assert row[6] == '2015-03-01'
        assert row[13] == '2015-03-01'
        assert row[14] == 'N'

    def test_each_activity_source(self):
        student = StudentFactory(intake_date=D(2015, 3, 1))
        TestAppointment.objects.create(
            student=student, event=make_event(TestEvent.ORIENTATION, D(2016, 1, 5)),
            attendance_type='P', attendance_date=D(2016, 1, 5),
        )
        TestAppointment.objects.create(
            student=student, event=make_event(TestEvent.TABE, D(2016, 2, 5)),
            attendance_type='P', attendance_date=D(2016, 2, 5),
        )
        TestHistoryFactory(student=student, last_test_date=D(2016, 2, 6))
        enrollment = EnrollmentFactory(student=student)
        Enrollment.objects.filter(pk=enrollment.pk).update(
            created=timezone.make_aware(datetime.datetime(2016, 3, 1, 12))
        )
        AttendanceFactory(enrollment=enrollment, attendance_date=D(2016, 3, 10))
        prospect = Prospect.objects.create(
            first_name='P', last_name='Q', phone='5045553000', dob=D(1990, 1, 1),
            contact_preference='Email', student=student,
        )
        ProspectNote.objects.create(
            prospect=prospect, contact_date=D(2016, 4, 1),
            contact_method='Call', successful=True,
        )

        row = rows_by_wru(self.run())[student.WRU_ID]

        assert row[6:14] == [
            '2015-03-01', '2016-01-05', '2016-02-05', '2016-02-06',
            '2016-03-01', '2016-03-10', '2016-04-01', '2016-04-01',
        ]

    def test_recent_activity_is_active(self):
        student = StudentFactory(intake_date=D(2015, 3, 1))
        enrollment = EnrollmentFactory(student=student)
        Enrollment.objects.filter(pk=enrollment.pk).update(
            created=timezone.make_aware(datetime.datetime(2024, 8, 20, 12))
        )
        AttendanceFactory(enrollment=enrollment, attendance_date=D(2024, 9, 1))
        row = rows_by_wru(self.run())[student.WRU_ID]
        assert row[13] == '2024-09-01'
        assert row[14] == 'Y'

    def test_absent_and_pending_appointments_ignored(self):
        student = StudentFactory(intake_date=D(2015, 3, 1))
        TestAppointment.objects.create(
            student=student, event=make_event(TestEvent.ORIENTATION, D(2024, 1, 5)),
            attendance_type='A',
        )
        TestAppointment.objects.create(
            student=student, event=make_event(TestEvent.TABE, D(2024, 2, 5)),
        )
        row = rows_by_wru(self.run())[student.WRU_ID]
        assert row[7:9] == ['', '']
        assert row[14] == 'N'

    def test_orientation_without_attendance_date_uses_event_start(self):
        student = StudentFactory(intake_date=D(2015, 3, 1))
        TestAppointment.objects.create(
            student=student, event=make_event(TestEvent.CLOSED_ORIENTATION, D(2023, 5, 2)),
            attendance_type='P',
        )
        row = rows_by_wru(self.run())[student.WRU_ID]
        assert row[7] == '2023-05-02'
        assert row[14] == 'Y'

    def test_unsuccessful_prospect_contact_ignored(self):
        student = StudentFactory(intake_date=D(2015, 3, 1))
        prospect = Prospect.objects.create(
            first_name='P', last_name='Q', phone='5045553000', dob=D(1990, 1, 1),
            contact_preference='Email', student=student,
        )
        ProspectNote.objects.create(
            prospect=prospect, contact_date=D(2024, 4, 1),
            contact_method='Call', successful=False,
        )
        row = rows_by_wru(self.run())[student.WRU_ID]
        assert row[12] == ''
        assert row[14] == 'N'

    def test_merged_reregistration_counts_despite_backdated_intake(self):
        survivor = StudentFactory(intake_date=D(2015, 3, 1))
        old = StudentFactory(
            duplicate=True, duplicate_of=survivor, dupl_date=D(2023, 8, 14),
            WRU_ID='d900001x',
        )
        rows = rows_by_wru(self.run())
        assert old.WRU_ID not in rows
        assert rows[survivor.WRU_ID][6] == '2023-08-14'
        assert rows[survivor.WRU_ID][14] == 'Y'


class TestReportViews:

    def test_summary_report_dispatches_task(self, auth_client, staff_user, celery_calls):
        response = auth_client.post(
            reverse('people:summary report csv'),
            {'from_date': '2026-01-01', 'to_date': '2026-06-30'},
        )
        assert response.status_code == 302
        _, args, _ = celery_calls.for_task('summary_report_task')[0]
        assert args == ('2026-01-01', '2026-06-30', staff_user.email)

    def test_summary_report_requires_dates(self, auth_client, celery_calls):
        response = auth_client.post(reverse('people:summary report csv'), {})
        assert response.status_code == 200
        assert not celery_calls.for_task('summary_report_task')

    def test_activity_report_defaults_to_five_years(self, auth_client):
        response = auth_client.get(reverse('people:student activity csv'))
        today = datetime.date.today()
        initial = response.context['form']['cutoff'].initial
        assert initial == today.replace(year=today.year - 5)

    def test_activity_report_dispatches_task(self, auth_client, staff_user, celery_calls):
        response = auth_client.post(
            reverse('people:student activity csv'), {'cutoff': '11/18/2021'}
        )
        assert response.status_code == 302
        _, args, _ = celery_calls.for_task('student_activity_report_task')[0]
        assert args == ('2021-11-18', staff_user.email)
