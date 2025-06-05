import csv
import os
from django.apps import apps
from django.core.mail.message import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def student_checkout_report_task(email_address):
    """Report of items checked out by students with their recent attendance activity"""
    
    Ticket = apps.get_model('inventory', 'Ticket')
    Attendance = apps.get_model('sections', 'Attendance')
    
    # Get all active checkouts by students
    student_checkouts = Ticket.objects.filter(
        student__isnull=False,
        issued_date__isnull=False,
        returned_date__isnull=True
    ).select_related('item', 'student').order_by('student__last_name', 'student__first_name')
    
    filename = f'student_checkout_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        
        headers = [
            'Student_WRU_ID',
            'Student_Name',
            'Student_Email',
            'Student_Phone',
            'Item_Category',
            'Item_Name',
            'Item_Serial',
            'Checkout_Date',
            'Days_Checked_Out',
            'Return_Required_Date',
            'Last_Attendance_Date',
            'Days_Since_Last_Attendance',
            'Recent_Attendance_Count_30_Days',
            'Total_Hours_30_Days'
        ]
        writer.writerow(headers)
        
        for ticket in student_checkouts:
            student = ticket.student
            item = ticket.item
            
            # Calculate days checked out
            days_checked_out = (timezone.now().date() - ticket.issued_date).days
            
            # Get student's recent attendance (last 30 days)
            thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
            recent_attendance = Attendance.objects.filter(
                enrollment__student=student,
                attendance_date__gte=thirty_days_ago,
                attendance_type='P'
            )
            
            # Get last attendance date
            try:
                last_attendance = Attendance.objects.filter(
                    enrollment__student=student,
                    attendance_type='P'
                ).latest('attendance_date')
                last_attendance_date = last_attendance.attendance_date
                days_since_attendance = (timezone.now().date() - last_attendance_date).days
            except ObjectDoesNotExist:
                last_attendance_date = 'Never'
                days_since_attendance = 'N/A'
            
            # Calculate recent activity metrics
            recent_attendance_count = recent_attendance.count()
            total_hours_30_days = sum([att.hours for att in recent_attendance])
            
            row = [
                student.WRU_ID or 'No ID',
                f"{student.last_name}, {student.first_name}",
                student.email,
                student.phone,
                item.category.name,
                item.name,
                item.item_id,
                ticket.issued_date.strftime('%Y-%m-%d'),
                days_checked_out,
                ticket.return_req_date.strftime('%Y-%m-%d') if ticket.return_req_date else 'Not Set',
                last_attendance_date.strftime('%Y-%m-%d') if last_attendance_date != 'Never' else last_attendance_date,
                days_since_attendance,
                recent_attendance_count,
                round(total_hours_30_days, 2)
            ]
            writer.writerow(row)
    
    email = EmailMessage(
        'Student Equipment Checkout Report',
        'Report of items currently checked out by students with their recent attendance activity',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    
    logger.info(f"Student checkout report sent to {email_address}")
    return True


@shared_task
def staff_checkout_report_task(email_address):
    """Report of items checked out by staff with their recent class activity"""
    
    Ticket = apps.get_model('inventory', 'Ticket')
    Section = apps.get_model('sections', 'Section')
    
    # Get all active checkouts by staff
    staff_checkouts = Ticket.objects.filter(
        staff__isnull=False,
        issued_date__isnull=False,
        returned_date__isnull=True
    ).select_related('item', 'staff').order_by('staff__last_name', 'staff__first_name')
    
    filename = f'staff_checkout_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        
        headers = [
            'Staff_Name',
            'Staff_Email',
            'Staff_Phone',
            'Item_Category',
            'Item_Name',
            'Item_Serial',
            'Checkout_Date',
            'Days_Checked_Out',
            'Return_Required_Date',
            'Current_Classes_Count',
            'Current_Classes_List',
            'Upcoming_Classes_Count',
            'Upcoming_Classes_List',
            'Last_Class_End_Date'
        ]
        writer.writerow(headers)
        
        for ticket in staff_checkouts:
            staff = ticket.staff
            item = ticket.item
            
            # Calculate days checked out
            days_checked_out = (timezone.now().date() - ticket.issued_date).days
            
            # Get staff's current and upcoming classes
            current_classes = staff.current_classes()
            upcoming_classes = staff.upcoming_classes()
            past_classes = staff.past_classes()
            
            # Format class lists
            current_classes_list = "; ".join([str(section) for section in current_classes[:3]])
            if current_classes.count() > 3:
                current_classes_list += f" ... (+{current_classes.count() - 3} more)"
                
            upcoming_classes_list = "; ".join([str(section) for section in upcoming_classes[:3]])
            if upcoming_classes.count() > 3:
                upcoming_classes_list += f" ... (+{upcoming_classes.count() - 3} more)"
            
            # Get last class end date
            try:
                last_class = past_classes.first()  # Already ordered by -ending, -semester__end_date
                if last_class:
                    last_end_date = last_class.end_date
                else:
                    last_end_date = 'No Past Classes'
            except:
                last_end_date = 'No Past Classes'
            
            row = [
                f"{staff.last_name}, {staff.first_name}",
                staff.email,
                staff.phone,
                item.category.name,
                item.name,
                item.item_id,
                ticket.issued_date.strftime('%Y-%m-%d'),
                days_checked_out,
                ticket.return_req_date.strftime('%Y-%m-%d') if ticket.return_req_date else 'Not Set',
                current_classes.count(),
                current_classes_list or 'None',
                upcoming_classes.count(),
                upcoming_classes_list or 'None',
                last_end_date.strftime('%Y-%m-%d') if last_end_date != 'No Past Classes' else last_end_date
            ]
            writer.writerow(row)
    
    email = EmailMessage(
        'Staff Equipment Checkout Report',
        'Report of items currently checked out by staff with their recent class activity',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    
    logger.info(f"Staff checkout report sent to {email_address}")
    return True


@shared_task
def combined_checkout_report_task(email_address):
    """Combined report of all checked out items with appropriate activity metrics"""
    
    Ticket = apps.get_model('inventory', 'Ticket')
    
    # Get all active checkouts
    all_checkouts = Ticket.objects.filter(
        issued_date__isnull=False,
        returned_date__isnull=True
    ).select_related('item', 'student', 'staff').order_by('item__category__name', 'item__name')
    
    filename = f'combined_checkout_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        
        headers = [
            'Item_Category',
            'Item_Name',
            'Item_Serial',
            'Holder_Type',
            'Holder_Name',
            'Holder_Phone',
            'Holder_Email',
            'Checkout_Date',
            'Days_Checked_Out',
            'Return_Required_Date',
            'Recent_Activity_Summary'
        ]
        writer.writerow(headers)
        
        for ticket in all_checkouts:
            item = ticket.item
            days_checked_out = (timezone.now().date() - ticket.issued_date).days
            
            if ticket.student:
                # Student checkout
                holder_type = 'Student'
                holder = ticket.student
                holder_name = f"{holder.last_name}, {holder.first_name}"
                holder_email = holder.email
                holder_phone = holder.phone
                
                # Get recent attendance summary
                thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
                recent_attendance = apps.get_model('sections', 'Attendance').objects.filter(
                    enrollment__student=holder,
                    attendance_date__gte=thirty_days_ago,
                    attendance_type='P'
                ).count()
                activity_summary = f"{recent_attendance} classes attended in last 30 days"
                
            else:
                # Staff checkout
                holder_type = 'Staff'
                holder = ticket.staff
                holder_name = f"{holder.last_name}, {holder.first_name}"
                holder_email = holder.email
                holder_phone = holder.phone
                
                # Get current classes summary
                current_classes_count = holder.current_classes().count()
                activity_summary = f"{current_classes_count} current classes teaching"
            
            row = [
                item.category.name,
                item.name,
                item.item_id,
                holder_type,
                holder_name,
                holder_phone,
                holder_email,
                ticket.issued_date.strftime('%Y-%m-%d'),
                days_checked_out,
                ticket.return_req_date.strftime('%Y-%m-%d') if ticket.return_req_date else 'Not Set',
                activity_summary
            ]
            writer.writerow(row)
    
    email = EmailMessage(
        'Combined Equipment Checkout Report',
        'Report of all items currently checked out with activity summaries',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)
    
    logger.info(f"Combined checkout report sent to {email_address}")
    return True
