from __future__ import absolute_import, unicode_literals
import csv
import os
from datetime import datetime, timedelta
from django.apps import apps
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q, Count
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from assessments import rules

logger = get_task_logger(__name__)


@shared_task
def orientation_reminder_task(event_id):
    event = apps.get_model('assessments', 'TestEvent').objects.get(pk=event_id)
    logger.info("Sending orientation reminder for {0}".format(event))
    event.orientation_reminder()
    return True

@shared_task
def test_reminder_task(event_id):
    event = apps.get_model('assessments', 'TestEvent').objects.get(pk=event_id)
    logger.info("Sending test reminder for {0}".format(event))
    event.test_reminder()

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
    os.remove(filename)
    return True

@shared_task
def orientation_status_task(student_id):
    student = apps.get_model('people', 'Student').objects.get(id=student_id)
    student.orientation = 'C'
    student.save()
    return True

@shared_task
def test_notification_task(test_type, test_id):
    tests = apps.get_model('assessments', test_type)
    try:
        test = tests.objects.get(id=test_id)
    except ObjectDoesNotExist:
        logger.info("Couldn't find {0} test {1}".format(test_type, test_id))
        return False
    student = test.student.student
    coaches = student.coaches.filter(active=True)
    emails = [
        coach.coach.email
        for coach
        in coaches
        if coach.coach.email is not None
    ]
    if len(emails) > 0:
        test_history_url = ''.join(['http://www.dccaep.org', test.student.get_absolute_url()])
        send_mail(
            "New Test Notification",
            "",
            'reporter@dccaep.org',
            emails,
            html_message="<p>A new test record has been created for {0}, "
            "WRU_ID: {1}. Here are the details:</p><ul><li>Date of Test: {2}"
            "</li><li>Assessment Type: {3}</li></ul><p>You can view the test"
            " results <a href={4}>here</a>".format(
                student,
                student.WRU_ID,
                test.test_date,
                test.get_test_type(),
                test_history_url
            )
        )
    return True

@shared_task
def test_process_task(test_type, test_id):
    tests = apps.get_model('assessments', test_type)
    try:
        test = tests.objects.get(id=test_id)
    except ObjectDoesNotExist:
        logger.info("Couldn't find {0} test {1}".format(test_type, test_id))
        return False
    logger.info("Processing {0} test {1}".format(test_type, test_id))
    test_history = test.student
    test_history.update_status(test)
#    PoP = apps.get_model('people', 'PoP')
#    student_pops = PoP.objects.filter(student=test_history.student)
#    if student_pops.count() == 0:
#        logger.info("{0} has no PoP records".format(test_history))
#        return False
#    pretest_limit = test.test_date - timedelta(days=180)
#    pops = student_pops.filter(
#        pretest_date__gte=pretest_limit
#    )
#    if pops.count() == 2:
#        pop = pops[1]
#        newer = pops[0]
#        newer.pretest_date = test.test_date
#        newer.pretest_type = test.get_test_type()
#        newer.save()
#    elif pops.count() == 1:
#        pop = pops[0]
#    elif pops.count() == 0:
#        start_limit = test.test_date + timedelta(days=180)
#        pops = student_pops.filter(
#            pretest_date=None,
#            start_date__gte=pretest_limit,
#            start_date__lte=start_limit,
#            )
#        pops.update(
#            pretest_date=test.test_date,
#            pretest_type=test.get_test_type()
#        )
#        logger.info("{0} logged as pretest for {1}".format(test, pops))
#        return False
#    if test_type == pop.pretest_type:
#        pretest = tests.objects.get(
#            student=test_history,
#            test_date=pop.pretest_date
#        )
#    else:
#        pretest = apps.get_model('assessments', pop.pretest_type).objects.get(
#                student=test_history,
#                test_date=pop.pretest_date
#            )
#    pop.made_gain = test.check_gain(pretest)
#    logger.info("gains checked for {0} with pretest {1} and postest {2}".format(pop, pretest, test))
#    pop.save()
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
    os.remove(filename)
    return True

@shared_task
def testing_eligibility_report(email_address):
    filename = 'testing_eligibility_report.csv'
    records = apps.get_model('assessments', 'TestHistory').objects.all()
    Attendance = apps.get_model('sections', "Attendance")
    today = timezone.now().date()
    target = today - timedelta(days=180)

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
            "Test Status",
            "Last Test Type",
            "Last Test Date",
            "Orienation Status",
            "Test Assignment",
            "Hours since last test",
            "Hours last 180 days",
            "Coach(es)",
            "Current Enrollments",
            "Current Teachers"
        ]
        writer.writerow(headers)

        for record in records:
            student = record.student
            attendance = Attendance.objects.filter(
                enrollment__student=student,
                attendance_date__gte=target
            )
            hours = sum([a.hours for a in attendance])
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
            try:
                active_hours = record.active_hours
            except TypeError:
                active_hours ="active_hours failed"
            if rules.has_valid_test_record(student):
                status = "No Test Needed"
            elif rules.needs_pretest(student):
                status = "Pretest needed"
            elif rules.needs_post_test(student):
                status = "Post test Needed"
            else:
                status = "Something is wrong"
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
                status,
                record.last_test_type,
                record.last_test_date,
                student.orientation,
                record.test_assignment,
                active_hours,
                hours,
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
    os.remove(filename)
    return True

@shared_task
def send_message_task(message_id):
    message = apps.get_model('assessments', 'Message').objects.get(id=message_id)
    logger.info('Sending message {0}'.format(message.title))
    message.send_message()

@shared_task
def remove_duplicate_assessments():
    tabes = apps.get_model('assessments', 'Tabe').objects.all()
    clas_es = apps.get_model('assessments', 'Clas_E').objects.all()

    tabe_dupes = tabes.values(
        'student',
        'test_date',
        'form',
        'read_level',
        'math_level',
        'lang_level',
        'read_nrs',
        'math_nrs',
        'lang_nrs'
    ).annotate(records=Count('student')).filter(records__gt=1)

    for dupes in tabe_dupes:
        dupes = tabes.filter(
        student=dupes['student'],
        test_date=dupes['test_date'],
        form=dupes['form'],
        read_level=dupes['read_level'],
        math_level=dupes['math_level'],
        lang_level=dupes['lang_level'],
        read_nrs=dupes['read_nrs'],
        math_nrs=dupes['math_nrs'],
        lang_nrs=dupes['lang_nrs']
        )
        print("Keeping {0}".format(dupes[0]))
        print("Removing {0}".format(dupes[1:]))
        remove = tabes.filter(pk__in=dupes[1:])
        remove.delete()

    clas_e_dupes = clas_es.values(
        'student',
        'test_date',
        'form',
        'read_level',
        'read_nrs',
    ).annotate(records=Count('student')).filter(records__gt=1)

    for dupes in clas_e_dupes:
        dupes = clas_es.filter(
        student=dupes['student'],
        test_date=dupes['test_date'],
        form=dupes['form'],
        read_level=dupes['read_level'],
        read_nrs=dupes['read_nrs'],
        )
        print("Keeping {0}".format(dupes[0]))
        print("Removing {0}".format(dupes[1:]))
        remove = clas_es.filter(pk__in=dupes[1:])
        remove.delete()


@shared_task
def send_score_report_link_task(test_id, test_type):
    test = apps.get_model('assessments', test_type).objects.get(id=test_id)
    student = test.student.student
    recipient_list = []
    if student.email:
        recipient_list.append(student.email)
    try:
        recipient_list.append(student.elearn_record.g_suite_email)
    except student._meta.model.elearn_record.RelatedObjectDoesNotExist:
        pass
    if len(recipient_list) > 0:
        test.score_report_sent = True
        test.save()
        context = {
            'student': student.first_name,
            'date': test.test_date,
            'link': test.score_report_link
        }
        html_message = render_to_string('emails/send_test_scores.html', context)
        send_mail(
            subject="Here is your score report",
            message=strip_tags(html_message),
            html_message=html_message,
            from_email="noreply@elearnclass.org",
            recipient_list=recipient_list
        )

@shared_task
def send_link_task(event_id, url_name):
    event = apps.get_model('asessments', 'TestEvent').objects.get(id=event_id)
    students = section.students.all()
    for student in students:
        student.student.email_form_link(url_name)
        student.student.text_form_link(url_name)
