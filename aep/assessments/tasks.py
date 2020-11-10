from __future__ import absolute_import, unicode_literals
import csv
from datetime import datetime, timedelta
from django.apps import apps
from django.core.mail.message import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q
from django.utils import timezone
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
    return True

@shared_task
def orientation_status_task(student_id):
    student = apps.get_model('people', 'Student').objects.get(id=student_id)
    student.orientation = 'C'
    student.save()
    return True

@shared_task
def test_process_task(test_history_id, test_type, test_id):
    tests = apps.get_model('assessments', test_type)
    try:
        test = tests.objects.get(id=test_id)
    except ObjectDoesNotExist:
        logger.info("Couldn't find {0} test {1}".format(test_type, test_id))
        return False
    logger.info("Processing {0} test {1}".format(test_type, test_id))
    test_history = apps.get_model('assessments', 'TestHistory').objects.get(id=test_history_id)
    PoP = apps.get_model('people', 'PoP')
    student_pops = PoP.objects.filter(student=test_history.student)
    test_history.update_status(test)
    if student_pops.count() == 0:
        logger.info("{0} has no PoP records".format(test_history))
        return False
    pretest_limit = test.test_date - timedelta(days=180)
    pops = student_pops.filter(
        pretest_date__gte=pretest_limit
    )
    if pops.count() == 2:
        pop = pops[1]
        newer = pops[0]
        newer.pretest_date = test.test_date
        newer.pretest_type = test.get_test_type()
        newer.save()
    elif pops.count() == 1:
        pop = pops[0]
    elif pops.count() == 0:
        start_limit = test.test_date + timedelta(days=180)
        pops = student_pops.filter(
            pretest_date=None,
            start_date__gte=pretest_limit,
            start_date__lte=start_limit,
            )
        pops.update(
            pretest_date=test.test_date,
            pretest_type=test.get_test_type()
        )
        logger.info("{0} logged as pretest for {1}".format(test, pops))
        return False
    if test_type == pop.pretest_type:
        pretest = tests.objects.get(
            student=test_history,
            test_date=pop.pretest_date
        )
    else:
        pretest = apps.get_model('assessments', pop.pretest_type).objects.get(
                student=test_history,
                test_date=pop.pretest_date
            )
    pop.made_gain = test.check_gain(pretest)
    logger.info("gains checked for {0} with pretest {1} and postest {2}".format(pop, pretest, test))
    pop.save()
    return True

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
                student.tests.last_test_date,
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

@shared_task
def testing_eligibility_report(email_address):
    filename = 'testing_eligibility_report.csv'
    records = apps.get_model('assessments', 'TestHistory').objects.all()
    today = timezone.now().date()

    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        headers = [
            "WRU_ID",
            "Last Name",
            "First Name",
            "DOB",
            "G Suite Email",
            "Email",
            "Phone",
            "Native Language",
            "Program Area",
            "Last Test Type",
            "Last Test Date",
            "Test Assignment",
            "Accumulated Hours",
            "Coach(es)",
            "Current Enrollments",
            "Current Teachers"
        ]
        writer.writerow(headers)

        for record in records:
            student = record.student
            coaches = [c.coach for c in student.coaches.filter(active=True)]
            sections = [s.section for s in student.current_classes()]
            teachers = [s.teacher for s in sections]
            try:
                g_suite_email = record.student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite_email = ''
            try:
                native_language = student.WIOA.native_language
            except ObjectDoesNotExist:
                native_language = ''
            s = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.dob,
                g_suite_email,
                student.email,
                student.phone,
                native_language,
                student.program,
                record.last_test_type,
                record.last_test_date,
                record.test_assignment,
                record.active_hours,
                coaches,
                sections,
                teachers
            ]
            writer.writerow(s)
    logger.info("Report Complete, composing email to {0}".format(email_address))
    email = EmailMessage(
        'Testing Eligibility Report',
        'The attached report includes a list of all student Testing Histories with contact information',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    return True
