"""
Notification system for HR alerts and reminders
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date, timedelta
import logging

from .models import Notification, Employee, Attendance, LeaveRequest, Document

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service class for managing notifications
    """
    
    @staticmethod
    def create_notification(recipient, title, message, notification_type='general', 
                          related_object=None, send_email=True):
        """
        Create a notification for a user
        """
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_object_id=related_object.id if related_object else None,
            related_object_type=related_object.__class__.__name__ if related_object else None
        )
        
        if send_email:
            NotificationService.send_email_notification(notification)
        
        return notification
    
    @staticmethod
    def send_email_notification(notification):
        """
        Send email notification
        """
        try:
            subject = f"HR System: {notification.title}"
            message = notification.message
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False,
            )
            
            notification.is_email_sent = True
            notification.save()
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
    
    @staticmethod
    def notify_late_checkin(attendance):
        """
        Notify employee about late check-in
        """
        if attendance.is_late:
            NotificationService.create_notification(
                recipient=attendance.employee.user,
                title="Late Check-in Alert",
                message=f"You checked in late on {attendance.date}. Please ensure you arrive on time.",
                notification_type='late_checkin',
                related_object=attendance
            )
    
    @staticmethod
    def notify_missed_checkout(employee, date):
        """
        Notify employee about missed check-out
        """
        NotificationService.create_notification(
            recipient=employee.user,
            title="Missed Check-out Alert",
            message=f"You forgot to check out on {date}. Please contact HR if this was an error.",
            notification_type='missed_checkout'
        )
    
    @staticmethod
    def notify_leave_request_submitted(leave_request):
        """
        Notify HR about new leave request
        """
        from .models import User
        
        hr_users = User.objects.filter(role='hr')
        for hr_user in hr_users:
            NotificationService.create_notification(
                recipient=hr_user,
                title="New Leave Request",
                message=f"{leave_request.employee.user.get_full_name()} has submitted a leave request for {leave_request.days_requested} days.",
                notification_type='leave_approval',
                related_object=leave_request
            )
    
    @staticmethod
    def notify_leave_request_approved(leave_request):
        """
        Notify employee about approved leave request
        """
        NotificationService.create_notification(
            recipient=leave_request.employee.user,
            title="Leave Request Approved",
            message=f"Your leave request from {leave_request.start_date} to {leave_request.end_date} has been approved.",
            notification_type='leave_approval',
            related_object=leave_request
        )
    
    @staticmethod
    def notify_leave_request_rejected(leave_request, reason):
        """
        Notify employee about rejected leave request
        """
        NotificationService.create_notification(
            recipient=leave_request.employee.user,
            title="Leave Request Rejected",
            message=f"Your leave request from {leave_request.start_date} to {leave_request.end_date} has been rejected. Reason: {reason}",
            notification_type='leave_approval',
            related_object=leave_request
        )
    
    @staticmethod
    def notify_payroll_ready(payroll):
        """
        Notify employee about ready payroll
        """
        NotificationService.create_notification(
            recipient=payroll.employee.user,
            title="Payroll Ready",
            message=f"Your payroll for {payroll.pay_period_start} to {payroll.pay_period_end} is ready for review.",
            notification_type='payroll_ready',
            related_object=payroll
        )
    
    @staticmethod
    def notify_document_expiry(document):
        """
        Notify about document expiry
        """
        if document.expiry_date:
            days_until_expiry = (document.expiry_date - date.today()).days
            
            if days_until_expiry <= 30:  # Notify 30 days before expiry
                NotificationService.create_notification(
                    recipient=document.employee.user,
                    title="Document Expiry Alert",
                    message=f"Your {document.get_document_type_display()} ({document.title}) will expire on {document.expiry_date}.",
                    notification_type='document_expiry',
                    related_object=document
                )
    
    @staticmethod
    def check_daily_attendance():
        """
        Check daily attendance and send notifications
        """
        today = date.today()
        
        # Check for late check-ins
        late_attendances = Attendance.objects.filter(
            date=today,
            is_late=True
        )
        
        for attendance in late_attendances:
            NotificationService.notify_late_checkin(attendance)
        
        # Check for missed check-outs (employees who checked in but didn't check out)
        employees_without_checkout = Employee.objects.filter(
            attendances__date=today,
            attendances__check_in_time__isnull=False,
            attendances__check_out_time__isnull=True
        ).distinct()
        
        for employee in employees_without_checkout:
            NotificationService.notify_missed_checkout(employee, today)
    
    @staticmethod
    def check_document_expiry():
        """
        Check for documents expiring soon
        """
        thirty_days_from_now = date.today() + timedelta(days=30)
        
        expiring_documents = Document.objects.filter(
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gte=date.today()
        )
        
        for document in expiring_documents:
            NotificationService.notify_document_expiry(document)
    
    @staticmethod
    def send_weekly_attendance_summary():
        """
        Send weekly attendance summary to HR
        """
        from .models import User
        
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # Get attendance statistics
        total_employees = Employee.objects.filter(status='active').count()
        present_employees = Attendance.objects.filter(
            date__range=[start_date, end_date],
            check_in_time__isnull=False
        ).values('employee').distinct().count()
        
        late_employees = Attendance.objects.filter(
            date__range=[start_date, end_date],
            is_late=True
        ).values('employee').distinct().count()
        
        absent_employees = total_employees - present_employees
        
        # Send to HR users
        hr_users = User.objects.filter(role='hr')
        for hr_user in hr_users:
            message = f"""
            Weekly Attendance Summary ({start_date} to {end_date}):
            
            Total Active Employees: {total_employees}
            Present Employees: {present_employees}
            Late Employees: {late_employees}
            Absent Employees: {absent_employees}
            
            Attendance Rate: {(present_employees/total_employees*100):.1f}%
            """
            
            NotificationService.create_notification(
                recipient=hr_user,
                title="Weekly Attendance Summary",
                message=message.strip(),
                notification_type='general',
                send_email=True
            )
    
    @staticmethod
    def send_monthly_payroll_reminder():
        """
        Send monthly payroll reminder to HR
        """
        from .models import User
        
        hr_users = User.objects.filter(role='hr')
        for hr_user in hr_users:
            NotificationService.create_notification(
                recipient=hr_user,
                title="Monthly Payroll Reminder",
                message="It's time to process monthly payroll. Please review and approve all pending payroll records.",
                notification_type='general',
                send_email=True
            )


class NotificationScheduler:
    """
    Scheduler for automated notifications
    """
    
    @staticmethod
    def run_daily_checks():
        """
        Run daily notification checks
        """
        try:
            NotificationService.check_daily_attendance()
            NotificationService.check_document_expiry()
            logger.info("Daily notification checks completed successfully")
        except Exception as e:
            logger.error(f"Error in daily notification checks: {str(e)}")
    
    @staticmethod
    def run_weekly_checks():
        """
        Run weekly notification checks
        """
        try:
            NotificationService.send_weekly_attendance_summary()
            logger.info("Weekly notification checks completed successfully")
        except Exception as e:
            logger.error(f"Error in weekly notification checks: {str(e)}")
    
    @staticmethod
    def run_monthly_checks():
        """
        Run monthly notification checks
        """
        try:
            NotificationService.send_monthly_payroll_reminder()
            logger.info("Monthly notification checks completed successfully")
        except Exception as e:
            logger.error(f"Error in monthly notification checks: {str(e)}")
