import csv
import os
import time
from datetime import datetime, timedelta
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.db.models import Sum, Min, Max, Count, Q, Case, When, Exists, OuterRef
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from core.utils import state_session, get_fiscal_year_start_date, get_fiscal_year_end_date
from core.tasks import send_mail_task
from people.models import full_merge

logger = get_task_logger(__name__)

@shared_task
def send_to_state_task(wioa_id_list, action):
    records = apps.get_model('people', 'WIOA').objects.filter(id__in=wioa_id_list)
    session = state_session()
    for record in records:
        match action:
            case 'send':
                record.send(session)
            case 'check_for_state_id':
                record.check_for_state_id(session)
            case 'send_to_state':
                record.send_to_state(session)
            case 'verify':
                record.verify(session)

@shared_task
def send_orientation_confirmation_task(student_id):
    student = apps.get_model('people', 'Student').objects.get(pk=student_id)
    if student.email:
        context = {
            'student': student.first_name,
        }
        html_message = render_to_string('emails/orientation_confirmation.html', context)
        message = strip_tags(html_message)
        send_mail_task.delay(
            subject="Orientation Completed for Delgado Adult Education Program!",
            message=message,
            html_message=html_message,
            from_email="robot@elearnclass.org",
            recipient_list=[student.email],
        )

@shared_task
def intake_retention_report_task(from_date, to_date, email_address):
    filename = 'intake_retention_report.csv'
    students = apps.get_model('people', 'Student').objects.filter(duplicate=False)
    from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    min_id = students.filter(intake_date__gte=from_date).aggregate(Min('id'))['id__min']
    max_id = students.filter(intake_date__lte=to_date).aggregate(Max('id'))['id__max']
    new_students = students.filter(id__gte=min_id, id__lte=max_id)
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            'Partner',
            "Email",
            "G Suite",
            "Phone",
            "Alt Phone",
            "City",
            "Other City",
            "DOB",
            "Profile Link",
            "Intake Date",
            "Orientation Status",
            "Last Test Date",
            "Last Scheduled Class Start",
            "Last Attendance Date"

        ]
        writer.writerow(headers)
        for student in new_students:
            try:
                last_test_date = str(student.tests.last_test_date)
            except ObjectDoesNotExist:
                last_test_date = "No Test History"
            try:
                latest_class_start = str(student.latest_class_start())
            except ObjectDoesNotExist:
                latest_class_start = "No Enrollments"
            try:
                last_attended = str(student.last_attendance())
            except ObjectDoesNotExist:
                last_attended = "No Attendance"
            try:
                g_suite = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite = "No elearn record found"
            s = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.partner,
                student.email,
                g_suite,
                student.phone,
                student.alt_phone,
                student.city,
                student.other_city,
                str(student.dob),
                "".join(["dccaep.org",
                    student.get_absolute_url()]),
                str(student.intake_date),
                student.get_orientation_display(),
                last_test_date,
                latest_class_start,
                last_attended,
            ]
            writer.writerow(s)

    email = EmailMessage(
        'Student Intake Retention Report',
        "Date range based report containing student contact information and student participation in orientation, testing, and scheduling.",
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    return True

@shared_task
def new_student_report_task(from_date, to_date, email_address):
    pass

@shared_task
def staff_report_task(email_address):
    with open('staff_report.csv', 'w', newline='') as out:
        writer = csv.writer(out)
        Staff = apps.get_model('people', 'Staff')
        Enrollment = apps.get_model('sections', 'Enrollment')
        Attendance = apps.get_model('sections', 'Attendance')
        all_staff = Staff.objects.all()

        headers = [
            'First Name',
            'Last Name',
            'Email',
            'Active',
            'Total Classes Taught',
            'Total Enrollments',
            'Unique Students', 
            'Enrollment Rate', # #Enrollments / Total Seats
            'Dropped Rate', # #Dropped / #Enrollments
            'Completed Rate', # #Completed / Enrollments
            'Total Student Attendance', # Total Present Attendance Records
            'Student Attendance Rate', # total present attendance / total attendance
            'Cancellation Rate', # total cancelled attendance hours / total attendance hours
        ]

        writer.writerow(headers)

        for staff in all_staff:
            classes = staff.classes.all()
            students = Enrollment.objects.filter(section__teacher=staff)
            attendance = Attendance.objects.filter(enrollment__section__teacher=staff)
            data = {
                'first_name': staff.first_name,
                'last_name': staff.last_name,
                'email': staff.email,
                'active': staff.active,
            }
            data['num_classes'] = staff.classes.count()
            data['num_students'] =  students.count()
            data['unique'] = students.distinct('student').count()
            seats = staff.classes.aggregate(Sum('seats'))['seats__sum']
            if seats is not None:
                data['enrollment_rate'] = students.count() / seats
            else:
                data['enrollment_rate'] = 'N/A'
            if data['num_students'] > 0:
                data['dropped'] = students.filter(status='D').count() / data['num_students']
                data['completed'] = students.filter(status='C').count() / data['num_students']
                data['total_att'] = attendance.filter(attendance_type='P').count()
                data['cancelled_att'] = attendance.filter(attendance_type='C').count()
                data['att_possible'] =  attendance.count()
                data['att_rate'] = data['total_att'] / data['att_possible']
                data['cancel_rate'] =  data['cancelled_att'] / data['att_possible']
            else:
                data['dropped'] = 'N/A'
                data['completed'] = 'N/A'
                data['total_att'] = 'N/A'
                data['cancelled_att'] = 'N/A'
                data['att_possible'] =  'N/A'
                data['att_rate'] = 'N/A'
                data['cancel_rate'] =  'N/A'

            writer.writerow(
                [
                    data['first_name'],
                    data['last_name'],
                    data['email'],
                    data['active'],
                    data['num_classes'],
                    data['num_students'],
                    data['unique'],
                    data['enrollment_rate'],
                    data['dropped'],
                    data['completed'],
                    data['total_att'],
                    data['att_rate'],
                    data['cancel_rate'],
                ]

            )

    email = EmailMessage('Staff Report Test', "Let's just see how it goes shall we?.", 'reporter@dccaep.org', [email_address])
    email.attach_file('staff_report.csv')
    email.send()
    os.remove('staff_report.csv')
    return True

@shared_task
def participation_summary_task():
    with open('participation_report.csv', 'w', newline='') as out:
        writer = csv.writer(out)
        Student = apps.get_model('people', 'Student')
        students = Student.objects.filter(duplicate=False)

        headers = [
            'WRU ID',
            'First Name',
            'Last Name',
            'Email',
            'G Suite',
            'Orientation',
            'Partner',
            '# Enrollments',
            'Dropped Rate',
            'Completed Rate',
            'Last Attendance',
            'Total Attendance',
            'Attendance Rate',
            'Total Hours',
        ]

        writer.writerow(headers)

        for student in students:
            record = {
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'orientation': student.get_orientation_display(),
                'partner': student.partner,
                'wru': student.WRU_ID,
                'num_classes': student.classes.count()
            }
            try:
                record['g_suite'] = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                record['g_suite'] = "No elearn record found"
            if record['num_classes'] > 0:
                record['completed_rate'] = student.classes.filter(status='C').count() / record['num_classes']
                record['dropped_rate'] = student.classes.filter(status='D').count() / record['num_classes']
                attendance = apps.get_model('sections', 'Attendance').objects.filter(enrollment__student=student)
                present = attendance.filter(attendance_type='P')
                if present.count() > 0:
                    record['last_attended'] = present.latest('attendance_date').attendance_date
                    record['total_attendance'] = present.count()
                    record['attendance_rate'] = present.count() / attendance.count()
                    total_hours = 0
                    for att in present:
                        total_hours += att.hours
                    record['total_hours'] = total_hours
                else:
                    record['last_attended'] = 'N/A'
                    record['total_attendance'] = 0
                    record['attendance_rate'] = 'N/A'
                    record['total_hours'] = 0

            else:
                record['completed_rate'] = 'N/A'
                record['dropped_rate'] = 'N/A'
                record['last_attended'] = 'N/A'
                record['total_attendance'] = 0
                record['attendance_rate'] = 'N/A'
                record['total_hours'] = 0

            writer.writerow(
                [
                    record['wru'],
                    record['first_name'],
                    record['last_name'],
                    record['email'],
                    record['g_suite'],
                    record['orientation'],
                    record['partner'],
                    record['num_classes'],
                    record['dropped_rate'],
                    record['completed_rate'],
                    record['last_attended'],
                    record['total_attendance'],
                    record['attendance_rate'],
                    record['total_hours'],
                ]
            )
    email = EmailMessage('Participation Report', "This is a detailed participation report for all students", 'reporter@dccaep.org', ['shane.dicks1@gmail.com'])
    email.attach_file('participation_report.csv')
    email.send()
    os.remove('participation_report.csv')
    return True

@shared_task
def summary_report_task(from_date, to_date, email_address):

    from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    Student = apps.get_model('people', 'Student')
    Attendance = apps.get_model('sections', 'Attendance')
    Tabe = apps.get_model('assessments', 'Tabe')
    Clas_E = apps.get_model('assessments', 'Clas_E')

    students = Student.objects.filter(duplicate=False)
    attendance = Attendance.objects.filter(
        attendance_type='P',
        attendance_date__gte=from_date,
        attendance_date__lte=to_date
    )
    tabe_tests = Tabe.objects.filter(
        test_date__gte=from_date,
        test_date__lte=to_date
    )
    clas_e_tests = Clas_E.objects.filter(
        test_date__gte=from_date,
        test_date__lte=to_date
    )

    notes = apps.get_model('people', 'ProspectNote').objects.filter(
        successful=True,
        contact_date__gte=from_date,
        contact_date__lte=to_date
    ).exclude(prospect__student=None)

    min_id = students.filter(intake_date=from_date).aggregate(Min('id'))['id__min']
    max_id = students.filter(intake_date=to_date).aggregate(Max('id'))['id__max']
    new_students = students.filter(id__gte=min_id, id__lte=max_id)

    attended_students = students.filter(classes__attendance__in=attendance).distinct()
    
    clas_e_tested = students.filter(tests__clas_e_tests__in=clas_e_tests).distinct()
    tabe_tested = students.filter(tests__tabe_tests__in=tabe_tests).distinct()
    tested_students = clas_e_tested.union(tabe_tested)

    all_students = new_students.union(attended_students, tested_students)

    with open('summary_report.csv', 'w', newline='') as out:
        writer = csv.writer(out)
        headers = [
            'WRU ID',
            'First Name',
            'Last Name',
            'Email',
            'G Suite',
            'Orientation',
            'Partner',
            '# Enrollments',
            'Last Attendance',
            'Class Attendance',
            'Prospect Attendance',
            'Testing Attendance',
            'Total Hours',
        ]
        writer.writerow(headers)

        for student in all_students:
            enrollments = student.classes.filter(attendance__in=attendance).distinct()
            student_attendance = attendance.filter(enrollment__in=enrollments)
            try:
                last_attended = student_attendance.last().attendance_date
            except AttributeError:
                last_attended = "No Attendance"
            att_hours = sum([a.hours for a in student_attendance])
            num_tabes = tabe_tests.filter(student__student=student).count() 
            num_clas_es = clas_e_tests.filter(student__student=student).count()
            test_hours = 2 * (num_tabes + num_clas_es)
            prospect = 1 if notes.filter(prospect__student=student).exists() else 0
            total_hours = sum([att_hours, prospect, test_hours])
            try:
                g_suite = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite = "No elearn record found"
            record = [
                student.WRU_ID,
                student.first_name,
                student.last_name,
                student.email,
                g_suite,
                student.get_orientation_display(),
                student.partner,
                enrollments.count(),
                last_attended,
                att_hours,
                prospect,
                test_hours,
                f"{total_hours:.2f}"
            ]
            writer.writerow(record)
    email = EmailMessage('Summary Report', "Student attendance summary report", 'reporter@dccaep.org', [email_address])
    email.attach_file('summary_report.csv')
    email.send()
    os.remove('summary_report.csv')
    return True

@shared_task
def pop_update_task(student_id, date):
    logger.info(f"Student ID: {student_id}, Date: {date}")
    student = apps.get_model('people', 'Student').objects.get(id=student_id)
    PoP = apps.get_model('people', 'PoP')
    exit = date - timedelta(days=90)
    try:
        pop = PoP.objects.filter(
            student=student,
            last_service_date__gte=exit,
        ).latest()
        if date > pop.last_service_date:
            pop.last_service_date=date
            pop.save()
    except PoP.DoesNotExist:
        PoP.objects.filter(student=student).update(active=False)
        pop = PoP(
            student=student,
            start_date=date,
            last_service_date=date
        )
        try:
            tests=student.tests
            pretest_limit = date - timedelta(days=180)
            if (tests.last_test_date is not None and
                pop.start_date > tests.last_test_date and
                tests.last_test_date > pretest_limit):
                pop.pretest_date = tests.last_test_date
                pop.pretest_type = tests.last_test_type
        except ObjectDoesNotExist:
            pass
        pop.save()
    return True

@shared_task
def coachee_export_task(staff_id, email):
    Attendance = apps.get_model('sections', 'Attendance')
    coach = apps.get_model('people', 'Staff').objects.get(id=staff_id)
    coachings = coach.coachees.filter(active=True)
    with open('coachees_export.csv', 'w', newline='') as out:
        writer = csv.writer(out)        
        headers = [
            'WRU_ID',
            'Last Name',
            'First Name',
            'Personal Email',
            'G Suite Email',
            'Phone',
            'Native Language (if not English)',
            'Orientation',
            'Status',
            'Intake Date',
            'Date of Last Note',
            'Last Note Content',
            'Date of Last Attendance',
            'Last Attendance Section',
            'Last Tabe',
            'Last Hiset Practice',
            "Current Classes",
        ]
        writer.writerow(headers)

        for coaching in coachings:
            try:
                last_note = coaching.notes.latest('meeting_date')
                last_note_date = last_note.meeting_date
                last_note_note = last_note.notes
            except ObjectDoesNotExist:
                last_note_date ="No notes found"
                last_note_note = ""
            try:
                attendance = Attendance.objects.filter(
                    enrollment__student=coaching.coachee,
                    attendance_type = 'P'
                )
                last_attendance = attendance.latest('attendance_date', 'time_in')
                last_attendance_date = last_attendance.attendance_date
                section = last_attendance.enrollment.section
            except ObjectDoesNotExist:
                last_attendance_date = "No attendance found"
                section = ""
            try:
                elearn_record = coaching.coachee.elearn_record
                if elearn_record.g_suite_email != '':
                    g_suite_email = elearn_record.g_suite_email
                else:
                    g_suite_email = 'Student has no g_suite_email'
            except ObjectDoesNotExist:
                g_suite_email = 'Student has no elearn_record'
            try:
                tests = coaching.coachee.tests
                try:
                    last_tabe = tests.latest_tabe.test_date
                except ObjectDoesNotExist:
                    last_tabe = 'Student has no TABE'
                try:
                    last_hiset = tests.latest_hiset_practice[0].test_date
                except ObjectDoesNotExist:
                    last_hiset = 'Student has no Practice Test'
            except ObjectDoesNotExist:
                last_tabe = 'Student has no Test History'
                last_hiset = 'Student has no Test History'
            try:
                language = coaching.coachee.WIOA.native_language
            except ObjectDoesNotExist:
                language = "Student has no WIOA Record"
            classes = []
            for i in coaching.coachee.current_classes():
                j = "{0} ({1})".format(i.section, i.status)
                classes.append(j)
            s = [
                coaching.coachee.WRU_ID,
                coaching.coachee.last_name,
                coaching.coachee.first_name,
                coaching.coachee.email,
                g_suite_email,
                coaching.coachee.phone,
                language,
                coaching.coachee.get_orientation_display(),
                coaching.status,
                coaching.coachee.intake_date,
                last_note_date,
                last_note_note,
                last_attendance_date,
                section,
                last_tabe,
                last_hiset,
                classes
            ]
            writer.writerow(s)

    email = EmailMessage('Coachee Export', "Here is the coachee export your requested", 'reporter@dccaep.org', [email])
    email.attach_file('coachees_export.csv')
    email.send()
    os.remove("coachees_export.csv")
    return True

@shared_task
def prospect_export_task(email, staff_id=None, from_date=None, to_date=None):
    if staff_id:
        advisor = apps.get_model('people', 'Staff').objects.get(id=staff_id)
        prospects = advisor.prospects.all()
    else:
        prospects = apps.get_model('people', 'Prospect').objects.all()
    if from_date:
        prospects = prospects.filter(registration_date__gte=from_date)
    if to_date:
        prospects = prospects.filter(registration_date__lte=to_date)
    with open('prospect_export.csv', 'w', newline='') as out:
        writer = csv.writer(out)
        headers = [
            'WRU_ID',
            'Prospect',
            'Last Name',
            'First Name',
            'Registration',
            'DOB',
            'Native Language',
            'Phone',
            'Email',
            'Status',
            'Orientation',
            'Paperwork',
            'Testing',
            'Folder',
            'Preferred Contact',
            'Num Contacts',
            'Last Contact',
            'Last Note Content',
            'Last Orientation',
            'URL to Orientation',
            'Enrollments',
            'URL to Prospect Record'
        ]
        writer.writerow(headers)

        for prospect in prospects:
            try:
                last_note = prospect.notes.latest('contact_date')
                last_note_date = last_note.contact_date
                last_note_note = last_note.notes
            except ObjectDoesNotExist:
                last_note_date ="No notes found"
                last_note_note = ""
            classes = []
            if prospect.student:
                wru_id = prospect.student.WRU_ID
                for i in prospect.student.current_classes():
                    j = "{0} ({1})".format(i.section, i.status)
                    classes.append(j)
                try:
                    tests = ['Orientation', 'Online Orientation']
                    last_orientation = prospect.student.test_appointments.filter(
                        event__test__in=tests,
                        attendance_type='P'
                    ).latest('event__start')
                    orientation_url = "".join(['dccaep.org', last_orientation.get_absolute_url()])
                except ObjectDoesNotExist:
                    last_orientation, orientation_url = '', ''
            else:
                last_orientation, orientation_url, wru_id = 'No Student', '', ''

            s = [
                wru_id,
                prospect.id,
                prospect.last_name,
                prospect.first_name,
                prospect.registration_date,
                prospect.dob,
                prospect.primary_language,
                prospect.phone,
                prospect.email,
                prospect.status,
                prospect.orientation,
                prospect.paperwork,
                prospect.testing,
                prospect.folder,
                prospect.contact_preference,
                prospect.num_contacts,
                last_note_date,
                last_note_note,
                last_orientation,
                orientation_url,
                classes,
                "".join(['dccaep.org',prospect.get_absolute_url()])
            ]
            writer.writerow(s)

    email = EmailMessage('Prospect Export', "Here is the prospect export your requested", 'reporter@dccaep.org', [email])
    email.attach_file('prospect_export.csv')
    email.send()
    os.remove('prospect_export.csv')
    return True

@shared_task
def prospect_check_task(prospect_id):
    Prospect = apps.get_model('people', 'Prospect')
    prospect = Prospect.objects.get(id=prospect_id)
    logger.info("Duplicate check for {0} - id={1}".format(prospect, prospect.id))
    duplicates = Prospect.objects.filter(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        email=prospect.email,
        phone=prospect.phone,
        dob=prospect.dob,
        primary_language=prospect.primary_language,
        contact_preference=prospect.contact_preference,
        active=True
    ).exclude(id=prospect.id)
    if duplicates.exists():
        prospect.duplicate = True
        prospect.active = False
        prospect.save()
        logger.info("{0} marked as duplicate".format(prospect))
    Student = apps.get_model('people', 'Student')
    logger.info("Returner check for {0} - id={1}".format(prospect, prospect.id))
    matches = Student.objects.filter(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        dob=prospect.dob,
    )
    if matches.exists():
        prospect.returning_student = True
        prospect.save()
        logger.info("{0} marked as returner".format(prospect))

@shared_task
def student_link_prospect_task(student_id):
    student = apps.get_model('people', "Student").objects.get(id=student_id)
    logger.info("Prospect match check for {0} - id={1}".format(student, student.id))
    matches = apps.get_model('people', 'Prospect').objects.filter(
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        phone=student.phone,
        dob=student.dob,
    )
    if matches.exists():
        matches.update(student=student)

@shared_task
def send_student_schedule_task(student_id):
    student = apps.get_model('people', "Student").objects.get(id=student_id)
    current = student.current_classes().filter(status='A')
    recipients = []
    try:
        recipients.append(student.elearn_record.g_suite_email)
    except ObjectDoesNotExist:
        pass
    if student.email:
        recipients.append(student.email)
    if len(recipients) > 0:
        current.update(schedule_sent=True)
        context = {
                'student': student.first_name,
                'current': [e.section for e in current]
        }
        html_message = render_to_string('emails/student_schedule.html', context)
        message = strip_tags(html_message)
        send_mail_task.delay(
            subject="Delgado Adult Education Class Schedule",
            message=message,
            html_message=html_message,
            from_email="robot@elearnclass.org",
            recipient_list=recipients,
        )

@shared_task
def send_paperwork_link_task(student_id, url_name):
    student = apps.get_model('people', "Student").objects.get(id=student_id)
    student.email_form_link(url_name)
    student.text_form_link(url_name)

@shared_task
def student_check_duplicate_task(student_id):
    Student = apps.get_model('people', 'Student')
    student = Student.objects.get(id=student_id)
    logger.info("Duplicate check for {0} - id={1}".format(student, student.id))
    ignore_ids = ['', 'No ID', None]
    def get_matches():
        matches = Student.objects.filter(
            first_name=student.first_name,
            last_name=student.last_name,
            dob=student.dob,
            duplicate=False,
            id__lt=student.id
        ).exclude(
            id=student.id
        ).exclude(
            WRU_ID__in=ignore_ids
        ).order_by('-pk')
        return matches
    matches = get_matches()
    if not matches.exists():
        logger.info(f"No matches found for {student}")
    else:
        while matches.exists():
            orig = matches[0]
            logger.info(f"Merging orig {orig}-{orig.slug} into dupe {student}-{student.slug}")
            full_merge(orig, student)
            matches = get_matches()

@shared_task
def minor_student_report_task(email_address):
    today = datetime.today().date()
    try:
        from_date = today.replace(year=today.year - 18)
    except ValueError:
        from_date = today.replace(year=today.year - 18, day=28)
    to_date = today.replace(year=today.year - 16)
    fy_start = get_fiscal_year_start_date()
    students = apps.get_model('people', 'Student').objects.filter(duplicate=False, dob__gte=from_date, dob__lte=to_date)
    orientation_event_types = ['Orientation', 'Online Orientation', 'Closed Orientation']
    orientation_events = apps.get_model('assessments', 'TestEvent').objects.filter(start__gte=fy_start, test__in=orientation_event_types)
    with open("minor_student_report.csv", 'w', newline='') as out:
        writer = csv.writer(out)
        headers = [
            "WRU_ID",
            "Last Name",
            "First Name",
            "DOB",
            "Phone",
            "Email",
            "Intake Date",
            "Last Tested",
            "Last Test NRS",
            "NRS Max",
            "Test Assignment",
            "Att Hours",
            "Last Attendance",
            "Total Enrollments",
            "Enrolled w/good attendance",
            "Current Classes",
            "Orientation Appointments in FY",
            'Upcoming Test Appointments',
            "Parish"
        ]
        writer.writerow(headers)

        for student in students:
            TH = getattr(student, 'tests', None)
            current_classes = student.current_classes().annotate(absences=Count('attendance', filter=Q(attendance__attendance_type='A')))
            orientation_appts = student.test_appointments.filter(event__in=orientation_events)
            upcoming_test_appts = student.test_appointments.filter(event__start__gte=timezone.now())
            row = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.dob,
                student.phone,
                student.email,
                student.intake_date,
                TH.last_test_date if TH else "No Test History",
                TH.last_test_nrs if TH else "No Test History",
                TH.nrs_max() if TH else "No Test History",
                TH.test_assignment if TH else "No Test History",
                student.total_hours(),
                student.last_attendance(),
                current_classes.count(),
                current_classes.filter(absences__lte=5).count(),
                [e.section.__str__() for e in current_classes],
                [a.event.title for a in orientation_appts],
                [a.event.title for a in upcoming_test_appts],
                student.get_parish_display()
            ]
            writer.writerow(row)
    email = EmailMessage('Minor Student Report', "Here is the minor student report requested", 'reporter@dccaep.org', [email_address])
    email.attach_file('minor_student_report.csv')
    email.send()
    os.remove("minor_student_report.csv")
    return True

@shared_task
def student_nrs_report_task(email_address):
    filename = "student_nrs_report.csv"
    start_date = get_fiscal_year_start_date()
    end_date =  get_fiscal_year_end_date()
    attendance = apps.get_model('sections', 'Attendance').objects.filter(
            attendance_date__gte=start_date,
            attendance_date__lte=end_date
        )
    appointments = apps.get_model('assessments', 'TestAppointment').objects.filter(
            attendance_date__gte=start_date,
            attendance_date__lte=end_date
        )
    fiscal_tabes = apps.get_model('assessments', 'Tabe').objects.filter(
            test_date__gte=start_date,
            test_date__lte=end_date
        )
    fiscal_clas_es = apps.get_model('assessments', 'Clas_E').objects.filter(
            test_date__gte=start_date,
            test_date__lte=end_date
        )
    Student = apps.get_model('people', 'Student')
    students = Student.objects.filter(
            Q(duplicate=False),
            Q(classes__attendance__in=attendance) | Q(test_appointments__in=appointments)
        ).distinct()
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            "Intake Date",
            "Orientation",
            "Class Hours",
            "Test Hours",
            "Total Hours",
            "Num Tabes",
            "Num Clas-Es",
            "Tabes",
            "Clas-Es"
        ]
        writer.writerow(headers)

        for student in students:
            student_attendance = attendance.filter(
                    attendance_type='P',
                    enrollment__student=student
                )
            att_hours = sum([a.hours for a in student_attendance])
            tabes = fiscal_tabes.filter(student__student=student)
            clas_es = fiscal_clas_es.filter(student__student=student)
            test_hours = 2 * (tabes.count() + clas_es.count())
            row = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.intake_date,
                student.orientation,
                att_hours,
                test_hours,
                att_hours + test_hours,
                tabes.count(),
                clas_es.count()
            ]
            if tabes.exists():
                cell = "\n".join([f"{t.test_date} {t.nrs()}" for t in tabes])
                row.append(cell)
            else:
                row.append("None")
            if clas_es.exists():
                cell = "\n".join([f"{t.test_date} {t.nrs()}" for t in clas_es])
                row.append(cell)
            else:
                row.append("None")
            writer.writerow(row)


    email = EmailMessage(
        'Student NRS Report',
        "Student attendance and testing progress for students active in current fiscal year",
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    return True

@shared_task
def possible_duplicate_report_task(email_address, id_list=None):
    filename = "possible_duplicates_report.csv"
    Student = apps.get_model('people', 'Student')
    if id_list is not None:
        new_students = Student.objects.filter(id__in=id_list)
    else:
        new_students = Student.objects.filter(WRU_ID=None)
    students = Student.objects.filter(duplicate=False).exclude(id__in=id_list)
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        data = []
        headers1 = [
            "Last Name",
            "First Name",
            "DOB",
            "Intake"
        ]
        writer.writerow(headers1)
        headers2 = [
            "",
            "",
            "DOB",
            "Last Name",
            "First Name",
        ]
        writer.writerow(headers2)

        for student in new_students:
            row = [student.last_name, student.first_name, student.dob, student.intake_date]
            writer.writerow(row)
            l_search = student.last_name[:3]
            f_search = student.first_name[:3]
            dob_start = student.dob - timedelta(days=365*3)
            dob_end = student.dob + timedelta(days=365*3)
            name_match = students.filter(
                last_name__istartswith=l_search,
                first_name__istartswith=f_search,
                dob__gte=dob_start,
                dob__lte=dob_end
            ).order_by('-dob')
            for match in name_match:
                match_row = [
                    "",
                    "Name Match",
                    match.dob,
                    match.last_name,
                    match.first_name
                ]
                writer.writerow(match_row)

    email = EmailMessage(
        'Possible Duplicate Report',
        "Report on possible duplicates for all unregistered students",
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    return True

@shared_task
def intercession_report_task(email_address):
    filename = 'intercession_report.csv'
    Enrollments = apps.get_model('sections', 'Enrollment')
    target = timezone.now() - timedelta(days=70)
    last_session_enrollments = Enrollments.objects.filter(
        section__semester__start_date__gte=target,
        section__semester__start_date__lte=timezone.now().date()
    )
    upcoming_enrollments = Enrollments.objects.filter(
        section__semester__start_date__gte=timezone.now().date()
    )
    students = apps.get_model('people', 'Student').objects.filter(
        classes__in=last_session_enrollments
    ).distinct()

    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        headers = [
            'WRU ID',
            'Last Name',
            'First Name',
            'Email',
            'Site',
            'Attendance Rate',
            'Test Status',
            'Last Test Date',
            'Last Test NRS',
            'Test Assignment',
            'Hours',
            'Test Appointments',
            'Upcoming Enrollments',
        ]
        writer.writerow(headers)

        for student in students:
            enrollments = last_session_enrollments.filter(student=student)
            site = {e.section.site.code for e in enrollments}
            present = sum([e.times_attended() for e in enrollments])
            absent = sum([e.times_absent() for e in enrollments])
            if present > 0: 
                attendance_rate = present / (absent + present)
            else:
                attendance_rate = 0
            try:
                tests = student.tests
                last_test_date = tests.last_test_date
                last_test_nrs = f"{tests.last_test_type}: {tests.last_test_nrs}"
                assignment = tests.test_assignment
                active_hours = tests.active_hours
            except ObjectDoesNotExist:
                last_test = "No Test History"
                last_test_nrs = "No Test History"
                assignment = "No Test History"
                active_hours = "No Test History"
            appointments = student.test_appointments.filter(
                event__start__gte=timezone.now(),
                event__test__in=['TABE', 'CLAS-E']
            )
            has_appointments = appointments.count() > 0
            row = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.email,
                ", ".join(list(site)),
                "{:.2f}".format(attendance_rate),
                student.testing_status(),
                last_test_date,
                last_test_nrs,
                assignment,
                active_hours,
                has_appointments,
                upcoming_enrollments.filter(student=student).count()
            ]
            writer.writerow(row)

    email = EmailMessage(
        'Intercession Report',
        """Attached report lists students active in the current session with attendance rate, test status,
        test appointments, last test date, and attendance hours""",
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename) 

@shared_task
def wru_student_intake_csv_task(email_address, id_list):
    filename = "wru_student_intake.csv"
    Student = apps.get_model('people', 'Student')
    students = Student.objects.filter(id__in=id_list)
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        data = []
        headers = [
            "FirstName",
            "MiddleInitial",
            "LastName",
            "DOB",
            "SSN",
            "Age",
            "Gender Code",
            "PhoneNumber",
            "EmergencyFName",
            "EmergencyLName",
            "Emergency Relationship Code",
            "USCitizen",
            "StreetAddress",
            "City",
            "State",
            "ZipCode",
            "Hispanic/Latino",
            "AmericanIndian",
            "Asian",
            "Black",
            "Hawaiian",
            "Foreign/Allien",
            "HighestDegreeOrLevelCompleted Code",
            "Location(Highest Degree Or Level Completed) Code",
            "Employment Status Code",

        ]
        writer.writerow(headers)

        for student in students:
            data = student.get_intake_import_data()
            row = [
                student.first_name,
                "",
                student.last_name,
                student.dob.strftime('%Y-%m-%d'),
                student.WIOA.SID,
                student.get_age_at_intake(),
                student.get_gender_code(),
                student.phone,
                data["ec_first_name"],  
                data["ec_last_name"],
                data["ec_relationship"],
                int(student.US_citizen),
                student.street_address_1,
                student.city,
                student.state,
                student.zip_code,
                int(student.WIOA.hispanic_latino),  
                int(student.WIOA.amer_indian),
                int(student.WIOA.asian),
                int(student.WIOA.black),
                int(student.WIOA.pacific_islander),
                data["highest_degree"],
                data["school_location"],
                data["employmen_status"],
            ]
            writer.writerow(row)

    email = EmailMessage(
        'WRU Student Intake Report',
        "File for student intake import",
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    return True

@shared_task
def process_student_import_task(email, student_ids):
    time.sleep(10)
    Student = apps.get_model('people', 'Student')
    for sid in student_ids:
        student_link_prospect_task.delay(sid)
        student_check_duplicate_task.delay(sid)
        Student.objects.get(id=sid).testify()
    possible_duplicate_report_task.delay(email, student_ids)


@shared_task
def advanced_student_report_task(email_address):
    Enrollment = apps.get_model('sections', 'Enrollment')
    Student = apps.get_model('people', 'Student')
    Tabe = apps.get_model('assessments', 'Tabe')

    target = timezone.now() - timedelta(days=90)
    today = timezone.now().date()

    filename = f'advanced_student_report_{today.strftime("%Y%m%d")}.csv'

    two_years_ago = (today - timedelta(days=730)).strftime('%Y-%m-%d')

    last_session_enrollments = Enrollment.objects.filter(
        section__semester__start_date__gte=target,
        section__semester__start_date__lte=today
    )
    upcoming_enrollments = Enrollment.objects.filter(
        section__semester__start_date__gt=today
    )

    recent_student_ids = list(Student.objects.filter(
        Q(classes__in=last_session_enrollments) |
        Q(classes__in=upcoming_enrollments)
    ).distinct().values_list('id', flat=True))

    qualified_students = Student.objects.filter(
            id__in=recent_student_ids
        ).annotate(
        read_3plus_count=Count('tests__tabe_tests', filter=Q(
            tests__tabe_tests__test_date__gte=two_years_ago,
            tests__tabe_tests__read_nrs__gte='3'
        ) & ~Q(tests__tabe_tests__read_level='E')),
        math_3plus_count=Count('tests__tabe_tests', filter=Q(
            tests__tabe_tests__test_date__gte=two_years_ago,
            tests__tabe_tests__math_nrs__gte='3'
        ) & ~Q(tests__tabe_tests__math_level='E')),
        lang_3plus_count=Count('tests__tabe_tests', filter=Q(
            tests__tabe_tests__test_date__gte=two_years_ago,
            tests__tabe_tests__lang_nrs__gte='3'
        ) & ~Q(tests__tabe_tests__lang_level='E')),
        read_4plus_count=Count('tests__tabe_tests', filter=Q(
            tests__tabe_tests__test_date__gte=two_years_ago,
            tests__tabe_tests__read_nrs__gte='4',
            tests__tabe_tests__read_level__in=['A', 'D']
        )),
        math_4plus_count=Count('tests__tabe_tests', filter=Q(
            tests__tabe_tests__test_date__gte=two_years_ago,
            tests__tabe_tests__math_nrs__gte='4',
            tests__tabe_tests__math_level__in=['A', 'D']
        )),
        lang_4plus_count=Count('tests__tabe_tests', filter=Q(
            tests__tabe_tests__test_date__gte=two_years_ago,
            tests__tabe_tests__lang_nrs__gte='4',
            tests__tabe_tests__lang_level__in=['A', 'D']
        )),
        total_subtests_with_3plus=Case(
            When(read_3plus_count__gt=0, then=1), default=0
        ) + Case(
            When(math_3plus_count__gt=0, then=1), default=0  
        ) + Case(
            When(lang_3plus_count__gt=0, then=1), default=0
        ),
       accuplacer_prep_completed=Exists(
           Enrollment.objects.filter(
               student=OuterRef('pk'),
               status='C',
               section__title__icontains='accuplacer'
           )
       )
    ).filter(
        total_subtests_with_3plus__gte=2
    ).filter(
        Q(read_4plus_count__gt=0) | Q(math_4plus_count__gt=0) | Q(lang_4plus_count__gt=0)
    ).distinct()

    reporting_tabe_tests = Tabe.objects.filter(
        test_date__gte=two_years_ago
    ).filter(
        Q(read_nrs__gte='3') | Q(math_nrs__gte='3') | Q(lang_nrs__gte='3')
    )

    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        headers = [
            "Partner",
            "Student ID",
            "Student Last Name", 
            "Student First Name",
            "Eligibility Verified",
            "Last Test Date",
            "Test Assignment",
            "Testing Status",
            "Qualifying Tests",
            "Read NRS 3+ Count",
            "Read NRS 4+ Count",
            "Math NRS 3+ Count",
            "Math NRS 4+ Count",
            "Lang NRS 3+ Count",
            "Lang NRS 4+ Count",
            "Accuplacer Prep Completed",
            "Intake Date",
            "Language",
            "CCR On Campus",
            "CCR Online",
            "ELL On Campus",
            "ELL Online", 
            "Success",
            "Accuplacer",
            "Certifications",
            "Gender",
            "Date of Birth",
            "Marital Status",
            "Address",
            "City",
            "State",
            "Zip",
            "Parish",
            "Email",
            "G-Suite Email",
            "Phone",
            "Alt Phone",
            "Emergency Contact",
            "Emergency Contact Phone"
        ]
        writer.writerow(headers)

        for student in qualified_students:
            try:
                g_suite_email = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite_email = ""

            test_assignment = student.tests.test_assignment
            last_test_date = student.tests.last_test_date
            reporting_tests_for_student = reporting_tabe_tests.filter(student__student=student)
            test_details = "\n".join([test.nrs_level_format() for test in reporting_tests_for_student])

            row = [
                student.partner,
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.eligibility_verified,
                last_test_date,
                test_assignment,
                student.testing_status(),
                test_details,
                student.read_3plus_count,
                student.read_4plus_count,
                student.math_3plus_count,
                student.math_4plus_count,
                student.lang_3plus_count,
                student.lang_4plus_count,
                student.accuplacer_prep_completed,
                student.intake_date,
                "|".join(sorted(set(student.prospects.values_list('primary_language', flat=True)))),
                student.ccr_app,
                student.e_learn_app,
                student.ell_app,
                student.ell_online_app,
                student.success_app,
                student.accuplacer_app,
                student.certifications_app,
                student.gender,
                student.dob.strftime('%Y-%m-%d'),
                student.get_marital_status_display(),
                " ".join([
                    student.street_address_1,
                    student.street_address_2
                ]),
                student.city,
                student.state,
                student.zip_code,
                student.get_parish_display(),
                student.email,
                g_suite_email,
                student.phone,
                student.alt_phone,
                student.emergency_contact,
                student.ec_phone
            ]
            writer.writerow(row)

    email = EmailMessage(
        'Advanced Student Report',
        'Attached is a report of students who:\n'
        '1. Were enrolled in classes starting in the last 90 days or have upcoming enrollments\n'
        '2. Have achieved NRS level 3 or higher in at least 2 different TABE subtests (Reading, Math, Language)\n'
        '3. Have achieved NRS level 4 or higher on A or D level tests in at least 1 of those subtests\n'
        '4. Based on TABE tests from the past 2 years only (excludes any Level E scores)',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()

    os.remove(filename)


@shared_task
def update_eligibility_task(wru_id_list, user_email):
    Student = apps.get_model('people', 'Student')
    not_found = []
    multiple_found = []
    
    for wru_id in wru_id_list:
        # Try original ID
        students = Student.objects.filter(WRU_ID=wru_id, duplicate=False)
        
        if students.count() == 0:
            # Try with 'd' prefix to find merged duplicate
            try:
                dup = Student.objects.get(WRU_ID='d' + wru_id)
                # Follow the duplicate_of chain to the end
                while dup.duplicate and dup.duplicate_of is not None:
                    dup = dup.duplicate_of
                dup.eligibility_verified = True
                dup.save()
            except Student.DoesNotExist:
                not_found.append(wru_id)
            except Student.MultipleObjectsReturned:
                not_found.append(wru_id)
        elif students.count() > 1:
            # Multiple non-duplicate students with same WRU_ID - update all
            students.update(eligibility_verified=True)
            multiple_found.append(wru_id)
        else:
            students.update(eligibility_verified=True)
    
    # Email results
    message = 'Eligibility update complete.\n'
    if multiple_found:
        message += f'\n{len(multiple_found)} WRU_IDs had multiple non-duplicate records (all updated).\n'
    if not_found:
        message += f'\n{len(not_found)} WRU_IDs not found.\n'
    
    attachments = []
    if not_found:
        with open('not_found.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['WRU_ID'])
            for wru_id in not_found:
                writer.writerow([wru_id])
        attachments.append('not_found.csv')
    
    if multiple_found:
        with open('multiple_found.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['WRU_ID'])
            for wru_id in multiple_found:
                writer.writerow([wru_id])
        attachments.append('multiple_found.csv')
    
    email = EmailMessage(
        'Eligibility Update Report',
        message,
        'admin@dccaep.org',
        [user_email]
    )
    for attachment in attachments:
        email.attach_file(attachment)
    email.send()
    
    for attachment in attachments:
        os.remove(attachment)
