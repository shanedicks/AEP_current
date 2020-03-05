from __future__ import absolute_import, unicode_literals
import csv
from datetime import datetime
from django.apps import apps
from django.core.mail.message import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def event_attendance_report_task(event_id, email_address):
    filename = '{0}_attendance_report.csv'.format(event_id)
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        event = apps.get_model('assessments', 'TestEvent').objects.get(id=event_id)
        students = event.students.all()
        headers = [
            'appt_id',
            'WRU ID',
            'Last Name',
            'First Name',
            'DOB',
            'Phone',
            'Email',
            'Date',
            'Attendance',
            'Hours'
        ]
        writer.writerow(headers)

        for appt in students:
            student = appt.student
            data = [
                appt.id,
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.dob,
                student.phone,
                student.email,
                appt.attendance_date,
                appt.attendance_type,
                appt.hours()
            ]
            writer.writerow(data)

    email = EmailMessage(
        'Test Event Attendance Report',
        "Per-event report containing student contact information and attendance status",
        'reporter@dccaep.org', 
        [email_address]
    )
    email.attach_file(filename)
    email.send()

@shared_task
def orientation_status_task(student_id):
    student = apps.get_model('people', 'Student').objects.get(id=student_id)
    student.orientation = 'C'
    student.save()

@shared_task
def accelerated_coaching_report_task(from_date, to_date, email_address):
    filename = 'accelerated_coaching_report.csv'
    from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S').date()
    to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M:%S').date()
    tabes = apps.get_model(
        'assessments',
        'Tabe'
        ).objects.filter(
        test_date__lte=to_date, 
        test_date__gte=from_date
    )
    tabes = tabes.filter(
        Q(read_nrs__gte=4)|
        Q(math_nrs__gte=4)|
        Q(lang_nrs__gte=4)
    )
    students = apps.get_model(
        'people',
        'Student'
        ).objects.filter(
        duplicate=False,
        tests__tabe_tests__in=tabes
        ).distinct()

    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        data = []
        headers = [
            "WRU_ID",
            "Last Name",
            "First Name",
            "Personal Email",
            "G Suite Email",
            "Phone",
            "Coach",
            "Last Attendance",
            "Last HiSet Practice",
            "Last Test Date",
            "Testing History"

        ]
        writer.writerow(headers)
        for student in students:
            try:
                elearn_email = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                elearn_email= "No elearn record found"
            try:
                coach = str(student.coaches.latest('pk').coach)
            except ObjectDoesNotExist:
                coach = "No coaching records found"
            try:
                last_attended = str(student.last_attendance())
            except ObjectDoesNotExist:
                last_attended = "No attendance found"
            try:
                last_hp = student.tests.latest_hiset_practice[0].test_date
            except ObjectDoesNotExist:
                last_hp = 'No practice test found'
            s = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.email,
                elearn_email,
                student.phone,
                coach,
                last_attended,
                last_hp,
                student.tests.last_test,
                "".join(["dccaep.org",
                    student.tests.get_absolute_url()])
            ]
            writer.writerow(s)

    email = EmailMessage(
        'Accelerated Coaching Report',
        'The attached report includes a list of all students with NRS Level 4 or above on any of the subtests (Reading, Language, Math) based on the date range selected when the report was run.',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    return True
