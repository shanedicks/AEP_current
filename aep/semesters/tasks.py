from datetime import timedelta
import csv
import os
from apiclient.errors import HttpError
from django.apps import apps
from django.conf import settings
from django.core.mail.message import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from core.tasks import send_mail_task
from core.utils import directory_service

logger = get_task_logger(__name__)

@shared_task
def waitlist_update_task(section_id_list):
    for section_id in section_id_list:
        logger.info('Waitlist Update for Section {0}'.format(section_id))
        section = apps.get_model('sections', 'Section').objects.get(id=section_id)
        section.waitlist_update()

@shared_task
def semester_end_task(section_id_list):
    for section_id in section_id_list:
        logger.info('Ending Section {0}'.format(section_id))
        section = apps.get_model('sections', 'Section').objects.get(id=section_id)
        section.end()

@shared_task
def semester_begin_task(section_id_list):
    for section_id in section_id_list:
        logger.info('Beginning Section {0}'.format(section_id))
        section = apps.get_model('sections', 'Section').objects.get(id=section_id)
        section.begin()

@shared_task
def g_suite_attendance_task(section_id_list):
    for section_id in section_id_list:
        logger.info('Getting G Suite Attendance for Section {0}'.format(section_id))
        section = apps.get_model('sections', 'Section').objects.get(id=section_id)
        section.g_suite_attendance()

@shared_task
def enforce_attendance_task(section_id_list):
    for section_id in section_id_list:
        logger.info('Enforcing Attendance for Section {0}'.format(section_id))
        section = apps.get_model('sections', 'Section').objects.get(id=section_id)
        section.enforce_attendance()

@shared_task
def send_g_suite_info_task(semester_id):
    ElearnRecord = apps.get_model('coaching', 'ElearnRecord')
    students = ElearnRecord.objects.filter(student__classes__section__semester__id=semester_id).distinct()
    logger.info('Sending G Suite Account Info to roster for semester {0}'.format(semester_id))
    for student in students:
        student.send_g_suite_info()
    return True

@shared_task
def send_survey_task(survey_id):
    survey = apps.get_model('semesters', 'Survey').objects.get(id=survey_id)
    logger.info('Sending survey {0}'.format(survey.title))
    survey.send_survey()

@shared_task
def send_message_task(message_id):
    message = apps.get_model('semesters', 'Message').objects.get(id=message_id)
    logger.info('Sending message {0}'.format(message.title))
    message.send_message()

@shared_task
def create_missing_g_suite_task(semester_id):
    semester = apps.get_model('semesters', 'Semester').objects.get(id=semester_id)
    Student = apps.get_model('people', 'Student')
    Elearn = apps.get_model('coaching', 'ElearnRecord')
    students = Student.objects.filter(classes__section__semester=semester).distinct()
    need_elearn = students.filter(elearn_record=None)
    logger.info("{0} students need elearn records".format(need_elearn.count()))
    for student in need_elearn:
        Elearn.objects.create(
            student=student,
            intake_date=timezone.now().date()
        )
        logger.info("Created elearn record for {0}".format(student))
    logger.info('Creating missing GSuite accounts for {0}'.format(semester.title))
    logger.info("Creating G Suite Service")
    service = directory_service()
    missing_g_suite = students.filter(elearn_record__g_suite_email='')
    for student in missing_g_suite:
        logger.info("Creating GSuite account for {0}".format(student))
        try:
            student.elearn_record.create_g_suite_account(service)
        except HttpError as e:
            logger.info("{0}".format(e))

@shared_task
def send_schedules_task(semester_id_list):
    semesters = apps.get_model('semesters', 'Semester').objects.filter(id__in=semester_id_list)
    enrollments = apps.get_model('sections', 'Enrollment').objects.filter(
        section__semester__in=semesters,
        status='A',
        schedule_sent=False,
        )
    students = apps.get_model('people', 'Student').objects.filter(
        classes__in=enrollments
    ).distinct()
    for student in students:
        current = student.classes.filter(section__semester__in=semesters, status='A')
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
def attendance_reminder_task(semester_id_list, email_address, send_mail=True):
    semesters = apps.get_model('semesters', 'Semester').objects.filter(id__in=semester_id_list)
    filename = 'teacher_attendance_report.csv'
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        headers = [
            'Session',
            'Section',
            'Teacher',
            'Count',
            'Completed'
        ]
        writer.writerow(headers)
        for semester in semesters:
            for section in semester.get_sections():
                count, sent = section.attendance_reminder(send_mail)
                completed = "No" if count > 0 else "Yes"
                data = [
                    semester,
                    section,
                    section.teacher,
                    count,
                    completed
                ]
                writer.writerow(data)
    email = EmailMessage(
        'Teacher Attendance Report',
        'Attached report lists the number of missing attendance for each section',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    return True

@shared_task
def send_link_task(semester_id, url_name):
    students = apps.get_model('people', 'Student').objects.filter(
            classes__section__semester__id=semester_id
        ).distinct()
    for student in students:
        student.email_form_link(url_name)
        student.text_form_link(url_name)

@shared_task
def first_class_warning_report_task(semester_id):
    """
    Generate report of students at risk of first-class drop and teachers with incomplete attendance.
    Runs Tuesday-Friday to check attendance from the previous day.
    """
    semester = apps.get_model('semesters', 'Semester').objects.get(id=semester_id)
    now = timezone.now()

    # Get yesterday's date and day name
    check_date = now.date() - timedelta(days=1)
    day_names = {
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    }
    report_day = day_names[check_date.weekday()]

    # Determine email recipient
    email_address = semester.first_class_report_to or settings.ADMINS[0][1]

    logger.info(f"Running first class warning report for {semester.title} checking {report_day} ({check_date})")

    # Get all enrollments for this semester
    enrollments = apps.get_model('sections', 'Enrollment').objects.filter(
        section__semester=semester,
        status='A'  # Only active enrollments
    )

    # Find students at risk (1 absent, 0 present)
    at_risk_students = []
    for enrollment in enrollments:
        absent_count = enrollment.attendance.filter(attendance_type='A').count()
        present_count = enrollment.attendance.filter(attendance_type='P').count()

        if absent_count == 1 and present_count == 0:
            try:
                elearn_email = enrollment.student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                elearn_email = ''

            at_risk_students.append({
                'wru_id': enrollment.student.WRU_ID,
                'first_name': enrollment.student.first_name,
                'last_name': enrollment.student.last_name,
                'email': enrollment.student.email,
                'elearn_email': elearn_email,
                'phone': enrollment.student.phone,
                'section': enrollment.section.title,
                'teacher': str(enrollment.section.teacher) if enrollment.section.teacher else 'No Teacher',
                'site': str(enrollment.section.site) if enrollment.section.site else 'No Site'
            })

    # Find sections with incomplete attendance for the check_date
    sections_with_incomplete_attendance = []
    for section in semester.get_sections():
        # Check if this section had class on the check_date
        section_days = section.get_days()
        check_weekday = check_date.weekday()  # 0=Monday, 1=Tuesday, etc.

        # Map weekday numbers to section day attributes
        day_mapping = {
            0: 'monday', 1: 'tuesday', 2: 'wednesday', 
            3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'
        }
        
        if check_weekday in day_mapping:
            day_attr = day_mapping[check_weekday]
            if hasattr(section, day_attr) and getattr(section, day_attr):
                # This section meets on the check_date day
                # Check if attendance has been completed
                attendance_count = apps.get_model('sections', 'Attendance').objects.filter(
                    attendance_date=check_date,
                    attendance_type='X',  # Pending attendance
                    enrollment__section=section,
                    enrollment__status='A'
                ).count()

                if attendance_count > 0:
                    sections_with_incomplete_attendance.append({
                        'section': section.title,
                        'teacher': str(section.teacher) if section.teacher else 'No Teacher',
                        'teacher_email': section.teacher.email if section.teacher and section.teacher.email else 'No Email',
                        'site': str(section.site) if section.site else 'No Site',
                        'pending_count': attendance_count
                    })
    
    # Generate CSV report
    filename = f'first_class_warning_report_{semester.title.replace(" ", "_")}_{check_date.strftime("%Y%m%d")}.csv'
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)

        # Students at Risk section
        writer.writerow([f'STUDENTS AT RISK OF BEING DROPPED - {report_day} {check_date}'])
        writer.writerow([])

        if at_risk_students:
            headers = [
                'WRU_ID', 'Last_Name', 'First_Name', 'Email', 'G_Suite_Email', 
                'Phone', 'Section', 'Teacher', 'Site'
            ]
            writer.writerow(headers)

            for student in at_risk_students:
                row = [
                    student['wru_id'], student['last_name'], student['first_name'],
                    student['email'], student['elearn_email'], student['phone'],
                    student['section'], student['teacher'], student['site']
                ]
                writer.writerow(row)
        else:
            writer.writerow(['No students at risk found'])

        writer.writerow([])
        writer.writerow([])

        # Incomplete Attendance section
        writer.writerow([f'TEACHERS WITH INCOMPLETE ATTENDANCE - {report_day} {check_date}'])
        writer.writerow([])

        if sections_with_incomplete_attendance:
            headers = [
                'Section', 'Teacher', 'Teacher_Email', 'Site', 'Pending_Records'
            ]
            writer.writerow(headers)

            for section_info in sections_with_incomplete_attendance:
                row = [
                    section_info['section'], section_info['teacher'], 
                    section_info['teacher_email'], section_info['site'],
                    section_info['pending_count']
                ]
                writer.writerow(row)
        else:
            writer.writerow(['All attendance completed for this day'])

    # Email the report
    email = EmailMessage(
        subject=f'First Class Drop Warning Report - {semester.title} - {report_day} {check_date}',
        body=f'Attached is the first class drop warning report for {semester.title}.\n\n'
             f'This report shows:\n'
             f'1. Students with 1 absence and 0 present attendance (at risk of being dropped)\n'
             f'2. Teachers who have not completed attendance for {report_day} {check_date}\n\n'
             f'Students with 2 absences and 0 present attendance will be automatically dropped during the next waitlist update (Fridays).',
        from_email='reporter@dccaep.org',
        to=[email_address]
    )
    email.attach_file(filename)
    email.send()

    # Clean up the file
    os.remove(filename)

    logger.info(f'First class warning report sent to {email_address} for {semester.title}')
    logger.info(f'Found {len(at_risk_students)} students at risk and {len(sections_with_incomplete_attendance)} sections with incomplete attendance')

    return True
