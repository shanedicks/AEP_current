from __future__ import absolute_import, unicode_literals
import csv
from datetime import datetime
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.db.models import Sum, Min, Max
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def orientation_email_task(name, email_address, appt_id):
    orientation = apps.get_model('assessments', 'TestAppointment').objects.get(id=appt_id)
    logger.info('Sent orientation confirmation to {0}.'.format(email_address))
    return send_mail(
        subject="Thank you for registering for the Delgado "
                "Community College Adult Education Program!",
        message="",
        html_message="<p>Hi, {student}</p><p>You have successfully registered for Delgado’s Adult Education Program!</p>"
        "<p><strong>Your next step is to complete the program’s Online Orientation.</strong></p>"
        "<p>Be on the lookout for the <strong>{event}</strong>, so please check your email on that day!"
        " (You may also want to check your spam folder too, just in case.)</p>"
        "<p>Once you get your email invitation, it will give instructions on how to complete your Orientation. "
        "Students need to finish their Orientation before they can begin classes.</p>"
        "<p>If you have any difficulties, you can also reach out to our coaching staff for help at coach@elearnclass.org</p>"
        "<p>Thank you,<br>The Adult Education Program<br>Delgado Community College</p>"
        "<hr>"
        "<p>Hola {student},</p><p>¡Te has registrado con éxito en el Programa de educación para adultos de Delgado!</p>"
        "<p><strong>El siguiente paso es completar la orientación en línea del programa.</strong></p>"
        "<p>Esté atento a su <strong>{event}</strong>, así que revise su correo electrónico ese día."
        " (También puede consultar su carpeta de correo no deseado, por si acaso).</p>"
        "<p>Una vez que reciba su invitación por correo electrónico, le dará instrucciones sobre cómo completar su Orientación."
        " Los estudiantes necesitan terminar su Orientación antes de que puedan comenzar las clases.</p>"
        "Si tiene alguna dificultad, también puede comunicarse con nuestro personal de coaching para obtener ayuda en coach@elearnclass.org "
        "<p>Gracias,<br>The Adult Education Program<br>Delgado Community College</p>".format(
                    student=name,
                    event=orientation.event
                ),
        from_email="reminder@dccaep.org",
        recipient_list=[email_address]
    )


@shared_task
def intake_retention_report_task(from_date, to_date, email_address):
    filename = 'intake_retention_report.csv'
    students = apps.get_model('people', 'Student').objects.filter(duplicate=False)
    from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S').date()
    to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M:%S').date()
    min_id = students.filter(intake_date=from_date).aggregate(Min('id'))['id__min']
    max_id = students.filter(intake_date=to_date).aggregate(Max('id'))['id__max']
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
                last_test = str(student.tests.last_test)
            except ObjectDoesNotExist:
                last_test = "No Test History"
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
                str(student.dob),
                "".join(["dccaep.org",
                    student.get_absolute_url()]),
                str(student.intake_date),
                student.get_orientation_display(),
                last_test,
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
    return True

@shared_task
def new_student_report_task(from_date, to_date, email_address):
    pass

@shared_task
def staff_report_task():
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
            data['num_classes'] = staff.classes.count(),
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

    email = EmailMessage('Staff Report Test', "Let's just see how it goes shall we?.", 'reporter@dccaep.org', ['jalehrman@gmail.com', 'shane.dicks1@gmail.com'])
    email.attach_file('staff_report.csv')
    email.send()
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
    email = EmailMessage('Participation Report Test', "Missed a few things the first time. Second Attempt", 'reporter@dccaep.org', ['jalehrman@gmail.com', 'shane.dicks1@gmail.com'])
    email.attach_file('participation_report.csv')
    email.send()
    return True

@shared_task
def summary_report_task(from_date, to_date, email):

    from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S').date()
    to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M:%S').date()

    Student = apps.get_model('people', 'Student')
    Attendance = apps.get_model('sections', 'Attendance')
    Tabe = apps.get_model('assessments', 'Tabe')
    Clas_E = apps.get_model('assessments', 'Clas_E')

    students = Student.objects.filter(duplicate=False)
    attendance = Attendance.objects.filter(attendance_type='P', attendance_date__gte=from_date)
    tabe_tests = Tabe.objects.filter(test_date__gte=from_date)
    clas_e_tests = Clas_E.objects.filter(test_date__gte=from_date)

    min_id = students.filter(intake_date=from_date).aggregate(Min('id'))['id__min']
    max_id = students.filter(intake_date=to_date).aggregate(Max('id'))['id__max']
    new_students = students.filter(id__gte=min_id)

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
            'Partner',
            '# Enrollments',
            'Last Attendance',
            'Total Attendance',
            'Total Hours',
        ]
        writer.writerow(headers)

        for student in all_students:
            enrollments = student.classes.filter(attendance__in=attendance)
            try:
                g_suite = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite = "No elearn record found"
            record = {
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'g_suite': g_suite,
                'partner': student.partner,
                'wru': student.WRU_ID,
                'num_classes': enrollments.count()
            }
