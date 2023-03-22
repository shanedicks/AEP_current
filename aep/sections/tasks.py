from __future__ import absolute_import, unicode_literals
from datetime import datetime
import csv
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from core.tasks import send_sms_task, send_mail_task
from core.utils import directory_service, classroom_service

logger = get_task_logger(__name__)

def get_enrollment(enrollment_id):
    Enrollment = apps.get_model('sections', 'Enrollment')
    return Enrollment.objects.get(id=enrollment_id)

@shared_task
def activate_task(enrollment_id):
    enrollment = get_enrollment(enrollment_id)
    return enrollment.activate()

@shared_task
def end_task(enrollment_id):
    enrollment = get_enrollment(enrollment_id)
    if enrollment.status == enrollment.ACTIVE:
        enrollment.status = enrollment.COMPLETED
    return enrollment.save()

@shared_task
def drop_task(enrollment_id):
    logger.info('Dropping enrollment {0}'.format(enrollment_id))
    enrollment = get_enrollment(enrollment_id)
    return enrollment.attendance_drop()

@shared_task
def participation_detail_task(email_address):
    enrollments = apps.get_model('sections', 'Enrollment').objects.all()
    sites = apps.get_model('sections', 'Site').objects.all()
    students = apps.get_model('people', 'Student').objects.filter(duplicate=False)
    with open('participation_detail_report.csv', 'w', newline='') as out:
        writer = csv.writer(out)

        headers = [
            'WRU_ID',
            'Name',
            'G_suite_email',
            'Total',
            'completed',
            'MW',
            'completed',
            'TR',
            'completed',
            'Morning',
            'completed',
            'Afternoon',
            'completed',
            'Evening',
            'completed',
        ]
        for site in sites:
            headers.extend([site.code, 'completed'])
        writer.writerow(headers)

        for student in students:
            enrolled = student.classes.all()
            if enrolled.count() == 0:
                continue
            completed = enrolled.filter(status='C')
            try:
                g_suite_email = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite_email = ''
            data = [
                student.WRU_ID,
                ", ".join([student.last_name, student.first_name]),
                g_suite_email,
                enrolled.count(),
                completed.count(),
                enrolled.filter(section__monday=True).count(),
                completed.filter(section__monday=True).count(),
                enrolled.filter(section__tuesday=True).count(),
                completed.filter(section__tuesday=True).count(),
                enrolled.filter(section__start_time__lte='11:30').count(),
                completed.filter(section__start_time__lte='11:30').count(),
                enrolled.filter(section__start_time__gt='11:30', section__start_time__lt='16:00').count(),
                completed.filter(section__start_time__gt='11:30', section__start_time__lt='16:00').count(),
                enrolled.filter(section__start_time__gte='16:00').count(),
                completed.filter(section__start_time__gte='16:00').count(),
            ]
            for site in sites:
                data.append(enrolled.filter(section__site=site).count())
                data.append(completed.filter(section__site=site).count())

            writer.writerow(data)

    email = EmailMessage(
        'Student Participation Report',
        'Report on student enrollment and class completion for various days, times, and sites',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file('participation_detail_report.csv')
    email.send()
    return True

@shared_task
def mondo_attendance_report_task(email_address, semesters, from_date, to_date):
    enrollments = apps.get_model('sections', 'Enrollment').objects.all()
    if semesters is not None:
        enrollments = enrollments.filter(section__semester__in=semesters)
        print("Enrollments in semester: ", enrollments.count())
    if from_date is not None:
        from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S').date()
        print(from_date)
        enrollments = enrollments.filter(
            Q(section__starting__gte=from_date) | 
            Q(section__semester__start_date__gte=from_date)
        )
        print("Enrollments after from_date: ", enrollments.count())
    if to_date is not None:
        to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M:%S').date()
        print(to_date)
        enrollments = enrollments.filter(
            Q(section__ending__lte=to_date) | 
            Q(section__semester__end_date__lte=to_date)
        )
        print("Enrollments before to_date: ", enrollments.count())
    with open('mondo_attendance_report.csv', 'w', newline='') as out:
        writer = csv.writer(out)

        headers = [
            'SID',
            'LAST_NAME',
            'FIRST_NAME',
            'MIDDLE_INITIAL',
            'Orientation Status',
            'COURSE_NAME',
            'GB_COURSE_SECTION_ID', 
            'WRU_ID',
            'Course',
            'Partner',
            'Teacher_First',
            'Teacher_Last',
            'Teacher_First_Teacher_Last',
            'Program',
            'Coach_First',
            'Coach_Last',
            'Coach_First_Coach_Last',
            'Last_Coaching_Meeting',
            'Site',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday',
            'Semester',
            'Start_Date',
            'End_Date',
            'Start_Time',
            'End_Time',
            'Seats',
            'Last_Test_Date',
            'AssessmentName',   
            'AssessmentForm',
            'AssessmentLevel',  
            'NRS_Math',
            'NRS_Reading',
            'NRS_Language', 
            'Total_Attendance_Hours',
        ]
        for i in range(48):
            headers.extend(['HOURS_{}'.format(i+1), 'HOURS_DATE_{}'.format(i+1)])

        writer.writerow(headers)

        for e in enrollments:
            section = e.section
            student = e.student
            try:
                teacher = section.teacher
            except:
                ObjectDoesNotExist
                teacher = None
            teacher_last = getattr(teacher, 'last_name', '')
            teacher_first = getattr(teacher, 'first_name', '')
            try:
                coaching = student.coaches.latest('start_date')
                coach = coaching.coach
            except ObjectDoesNotExist:
                coach = None
            if coach:
                try:
                    last_meeting = coaching.notes.latest('meeting_date').meeting_date
                except ObjectDoesNotExist:
                    last_meeting = ''
            else:
                last_meeting = ''
            coach_last = getattr(coach, 'last_name', '')
            coach_first = getattr(coach, 'first_name', '')
            try:
                last_test = student.tests.last_test
            except ObjectDoesNotExist:
                last_test = None
            lt_date = getattr(last_test, 'test_date', '')
            lt_name = type(last_test).__name__
            lt_form = getattr(last_test, 'form', '')
            lt_level = getattr(last_test, 'level', '')
            lt_read = getattr(last_test, 'read_nrs', '')
            lt_math = getattr(last_test, 'math_nrs', '')
            lt_lang = getattr(last_test, 'lang_nrs', '')
            data = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                '',
                student.get_orientation_display(),
                section.title,
                section.id,
                section.WRU_ID,
                section.course,
                student.partner,
                teacher_first,
                teacher_last,
                "{0} {1}".format(teacher_first, teacher_last),
                section.program,
                coach_first,
                coach_last,
                "{0} {1}".format(coach_first, coach_last),
                last_meeting,
                section.site,
                section.monday,
                section.tuesday,
                section.wednesday,
                section.thursday,
                section.friday,
                section.saturday,
                section.sunday,
                section.semester,
                section.start_date,
                section.end_date,
                section.start_time,
                section.end_time,
                section.seats,
                lt_date,
                lt_name,
                lt_form,
                lt_level,
                lt_math,
                lt_read,
                lt_lang,
                e.total_hours()
            ]
            for att in e.attendance.filter(attendance_type='P'):
                data.extend([att.hours, att.attendance_date])

            writer.writerow(data)

        email = EmailMessage(
        'Mondo Attendance Report',
        'An attendance report with all the extra bells and whistles',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file('mondo_attendance_report.csv')
    email.send()
    return True

@shared_task
def roster_to_classroom_task(section_id):
    Section = apps.get_model('sections', 'Section')
    section = Section.objects.get(id=section_id)
    logger.info('Exporting roster for {0} to google classroom'.format(section))
    return section.roster_to_classroom()

@shared_task
def send_g_suite_info_task(section_id):
    ElearnRecord = apps.get_model('coaching', 'ElearnRecord')
    students = ElearnRecord.objects.filter(student__classes__section__id=section_id).distinct()
    logger.info('Sending G Suite Account Info to roster for section {0}'.format(section_id))
    for student in students:
        student.send_g_suite_info()
    return True

@shared_task
def send_link_task(section_id, url_name):
    section = apps.get_model('sections', 'Section').objects.get(id=section_id)
    students = section.students.all()
    for student in students:
        student.email_form_link(url_name)
        student.text_form_link(url_name)

@shared_task
def enrollment_notification_task(enrollment_id):
    enrollment = apps.get_model('sections', 'Enrollment').objects.get(id=enrollment_id)
    email = EmailMessage(
        'Roster change for {section}'.format(section=enrollment.section.title),
        '{student} enrollment status for {section} is {status}'.format(
            student=enrollment.student,
            status=enrollment.get_status_display(),
            section=enrollment.section.title,
        ),
        'enrollment_bot@dccaep.org',
        [enrollment.section.teacher.email]
    )
    email.send()
    return True

@shared_task
def missed_class_report_task():
    pass

@shared_task
def section_skill_mastery_report_task(section_id, email_address):
    section = apps.get_model('sections', 'Section').objects.get(id=section_id)
    students = apps.get_model('people', 'Student').objects.filter(classes__section=section)
    skills = section.course.skills.all()
    SM = apps.get_model('academics', 'SkillMastery')
    skill_masteries = SM.objects.filter(skill__in=skills, student__in=students)

    filename = "skill_mastery_report_{0}.csv".format(section.slug)

    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)

        headers = [
            'student',
            'id',
            'cert_date',
            'certifier',
            'skill_title',
            'mastered'
        ]
        writer.writerow(headers)

        for sm in skill_masteries:
            data = [
                sm.student.WRU_ID,
                sm.id,
                sm.cert_date,
                sm.certifier.id,
                sm.skill.title,
                int(sm.mastered)
            ]

            writer.writerow(data)

    email = EmailMessage(
        'Skill Mastery Report',
        'Report on student enrollment and class completion for various days, times, and sites',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    return True

@shared_task
def create_missing_g_suite_task(section_id):
    section = apps.get_model('sections', 'Section').objects.get(id=section_id)
    Student = apps.get_model('people', 'Student')
    Elearn = apps.get_model('coaching', 'ElearnRecord')
    students = Student.objects.filter(classes__section=section).distinct()
    need_elearn = students.filter(elearn_record=None)
    logger.info("{0} students need elearn records".format(need_elearn.count()))
    for student in need_elearn:
        Elearn.objects.create(
            student=student,
            intake_date=timezone.now().date()
        )
        logger.info("Created elearn record for {0}".format(student))
    logger.info('Creating missing GSuite accounts for {0}'.format(section.title))
    logger.info("Creating G Suite Service")
    service = directory_service()
    for student in students:
        logger.info("Creating GSuite account for {0}".format(student))
        try:
            student.elearn_record.create_g_suite_account(service)
        except HttpError as e:
            logger.info("{0}".format(e))

@shared_task
def create_classroom_section_task(section_id_list):
    sections = apps.get_model('sections', 'Section').objects.filter(id__in=section_id_list)
    service = classroom_service()
    for obj in sections:
        if obj.g_suite_id:
            pass
        else:
            record = {
                "name": obj.title,
                "section": obj.semester.title,
                "ownerId": obj.teacher.g_suite_email
            }
            logger.info(f"Creating classroom section for {obj}")
            post = service.courses().create(body=record).execute()
            obj.g_suite_id = post.get('id')
            obj.g_suite_link = post.get('alternateLink')
            obj.save()
            service.courses().create(courseId=obj.g_suite_id)

@shared_task
def add_TA_task(section_id_list):
    sections = apps.get_model('sections', 'Section').objects.filter(id__in=section_id_list)
    service = classroom_service()
    program_ta = {
        'ELL': 'eslta@elearnclass.org',
        'ELRN': 'elearnta@elearnclass.org', 
        'CCR': 'onlineta@elearnclass.org'
    }
    for obj in sections:
        ta = {
            "courseId": obj.g_suite_id,
            "userId": program_ta[obj.program]
        }
        service.courses().create(body=ta).execute()

@shared_task
def send_message_task(message_id):
    message = apps.get_model('sections', 'Message').objects.get(id=message_id)
    logger.info('Sending message {0}'.format(message.title))
    message.send_message()

@shared_task
def cancel_class_task(cancellation_id):
    cancellation = apps.get_model('sections', 'Cancellation').objects.get(id=cancellation_id)
    section = cancellation.section
    attendance = apps.get_model('sections', 'Attendance').objects.filter(
        enrollment__section=section,
        attendance_date=cancellation.cancellation_date
    )
    attendance.update(attendance_type='C')
    if cancellation.send_notification:
        students = apps.get_model('people', 'Student').objects.filter(classes__section=section)
        cancellation_date = cancellation.cancellation_date.strftime("%m/%d/%y")
        recipient_list = []
        for student in students:
            context = {
                'student': student.first_name,
                'class_title': section.title,
                'teacher': section.teacher.first_name,
                'start_time': section.start_time.strftime("%I:%M %p"),
                'site': section.site.name,
                'date': cancellation_date
            }
            if student.email:
                recipient_list.append(student.email)
            if student.elearn_record and student.elearn_record.g_suite_email:
                recipient_list.append(student.elearn_record.g_suite_email)
            if student.phone:
                send_sms_task.delay(
                    dst=student.phone,
                    message="Delgado Adult Ed Alert: {0} at {1} at {2} with {3} is cancelled on {4}. Sorry for any hassle".format(
                        context['class_title'],
                        context['start_time'],
                        context['site'],
                        context['teacher'],
                        context['date']
                    )
                )
        html_message = render_to_string('emails/cancelled_class.html', context)
        send_mail(
            subject="{0} has been cancelled for {1}".format(cancellation.section.title, cancellation_date),
            message=strip_tags(html_message),
            html_message=html_message,
            from_email='noreply@elearnclass.org',
            recipient_list=recipient_list
        )
        cancellation.notification_sent = True
        cancellation.save()
