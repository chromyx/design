from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import os


def user_avatar_upload_path(instance, filename):
    """Generate upload path for user avatars"""
    ext = filename.split('.')[-1]
    filename = f"{instance.id}_{instance.username}.{ext}"
    return os.path.join('avatars', filename)


def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    ext = filename.split('.')[-1]
    filename = f"{instance.employee.id}_{instance.document_type}_{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join('documents', filename)


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('hr', 'HR Manager'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    avatar = models.ImageField(upload_to=user_avatar_upload_path, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_hr(self):
        return self.role == 'hr'
    
    def is_employee(self):
        return self.role == 'employee'
    
    def can_view_all_data(self):
        return self.is_admin() or self.is_hr()
    
    def can_edit_employee_data(self):
        return self.is_hr()
    
    def can_approve_requests(self):
        return self.is_hr()
    
    def get_employee_profile(self):
        """
        Get the employee profile for this user
        """
        try:
            return self.employee_profile
        except Employee.DoesNotExist:
            return None
    
    def has_employee_profile(self):
        """
        Check if user has an employee profile
        """
        return hasattr(self, 'employee_profile')


class Department(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='managed_departments')
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class JobPosition(models.Model):
    """
    Job position model
    """
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_job_position'
        verbose_name = 'Job Position'
        verbose_name_plural = 'Job Positions'
        unique_together = ['title', 'department']
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"


class Employee(models.Model):
    """
    Employee model with comprehensive information
    """
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('suspended', 'Suspended'),
        ('on_leave', 'On Leave'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    position = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, related_name='employees')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Employment Information
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    
    # Salary Information
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Work Schedule (Fixed 9 AM - 5 PM)
    work_start_time = models.TimeField(default='09:00:00')
    work_end_time = models.TimeField(default='17:00:00')
    work_days_per_week = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(7)])
    
    # Fingerprint Scanner Integration
    fingerprint_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Leave Balances
    vacation_days_remaining = models.IntegerField(default=0)
    sick_days_remaining = models.IntegerField(default=0)
    personal_days_remaining = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_employees')
    
    class Meta:
        db_table = 'hr_employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    def is_active(self):
        return self.status == 'active'
    
    def is_on_probation(self):
        if self.probation_end_date:
            return timezone.now().date() <= self.probation_end_date
        return False
    
    def get_work_hours_per_day(self):
        """Calculate work hours per day based on start and end time"""
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.work_start_time)
        end = datetime.combine(datetime.today(), self.work_end_time)
        if end < start:  # Handle overnight shifts
            end += timedelta(days=1)
        return (end - start).total_seconds() / 3600
    
    def generate_employee_id(self):
        """Generate HR-style employee ID (EMP001, EMP002, etc.)"""
        if not self.employee_id:
            # Get the highest existing employee ID
            last_employee = Employee.objects.filter(
                employee_id__startswith='EMP'
            ).order_by('-employee_id').first()
            
            if last_employee and last_employee.employee_id:
                # Extract the number part and increment
                try:
                    last_number = int(last_employee.employee_id[3:])  # Skip 'EMP'
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            self.employee_id = f"EMP{new_number:03d}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate employee ID"""
        if not self.employee_id:
            self.generate_employee_id()
        super().save(*args, **kwargs)
    
    def clean(self):
        super().clean()
        if self.termination_date and self.termination_date < self.hire_date:
            raise ValidationError('Termination date cannot be before hire date.')
        if self.probation_end_date and self.probation_end_date < self.hire_date:
            raise ValidationError('Probation end date cannot be before hire date.')


class Attendance(models.Model):
    """
    Attendance tracking model for fingerprint scanner integration
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_late = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_attendance'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.date}"
    
    def calculate_work_hours(self):
        """Calculate work hours based on check-in and check-out times"""
        if self.check_in_time and self.check_out_time:
            duration = self.check_out_time - self.check_in_time
            hours = duration.total_seconds() / 3600
            # Cap at maximum work hours (8 hours for full-time)
            max_hours = self.employee.get_work_hours_per_day()
            self.work_hours = min(hours, max_hours)
            self.overtime_hours = max(0, hours - max_hours)
        else:
            self.work_hours = 0
            self.overtime_hours = 0
    
    def check_lateness(self):
        """Check if employee is late based on work start time"""
        if self.check_in_time:
            from datetime import datetime, time
            work_start = datetime.combine(self.date, self.employee.work_start_time)
            work_start = timezone.make_aware(work_start)
            # Allow 15 minutes grace period
            grace_period = timezone.timedelta(minutes=15)
            self.is_late = self.check_in_time > (work_start + grace_period)
        else:
            self.is_late = False
    
    def save(self, *args, **kwargs):
        if self.check_in_time and self.check_out_time:
            self.calculate_work_hours()
        if self.check_in_time:
            self.check_lateness()
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    """
    Leave request model for vacation, sick leave, etc.
    """
    LEAVE_TYPE_CHOICES = [
        ('vacation', 'Vacation'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('bereavement', 'Bereavement Leave'),
        ('unpaid', 'Unpaid Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leave_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_leave_request'
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date.')
        if self.days_requested <= 0:
            raise ValidationError('Days requested must be greater than 0.')
    
    def approve(self, approved_by):
        """Approve the leave request"""
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, approved_by, reason):
        """Reject the leave request"""
        self.status = 'rejected'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()


class Payroll(models.Model):
    """
    Payroll model for salary calculations
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payrolls')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payrolls')
    approved_at = models.DateTimeField(null=True, blank=True)
    payslip_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_payroll'
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payrolls'
        unique_together = ['employee', 'pay_period_start', 'pay_period_end']
        ordering = ['-pay_period_end']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.pay_period_start} to {self.pay_period_end}"
    
    def calculate_net_salary(self):
        """Calculate net salary based on hours worked and deductions"""
        from decimal import Decimal
        
        # Base calculation for fixed 9 AM - 5 PM schedule
        expected_hours = Decimal(str(self.employee.get_work_hours_per_day() * self.employee.work_days_per_week * 2))  # Bi-weekly
        hourly_rate = self.base_salary / (expected_hours * Decimal('26'))  # 26 pay periods per year
        
        # Calculate pay based on actual hours worked (capped at expected hours)
        actual_hours = Decimal(str(min(float(self.hours_worked), float(expected_hours))))
        regular_pay = actual_hours * hourly_rate
        
        # Overtime pay (if any, though system caps at regular hours)
        overtime_hours = Decimal(str(self.overtime_hours))
        overtime_pay = overtime_hours * hourly_rate * Decimal('1.5')
        
        # Calculate net salary
        gross_pay = regular_pay + overtime_pay + self.bonuses
        self.net_salary = gross_pay - self.deductions
        return self.net_salary
    
    def save(self, *args, **kwargs):
        self.calculate_net_salary()
        super().save(*args, **kwargs)


class Document(models.Model):
    """
    Document model for employee documents
    """
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Employment Contract'),
        ('id_card', 'ID Card'),
        ('passport', 'Passport'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('resume', 'Resume'),
        ('other', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=document_upload_path)
    description = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hr_document'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.title}"
    
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False


class Notification(models.Model):
    """
    Notification model for system alerts
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('late_checkin', 'Late Check-in'),
        ('missed_checkout', 'Missed Check-out'),
        ('leave_approval', 'Leave Approval'),
        ('payroll_ready', 'Payroll Ready'),
        ('document_expiry', 'Document Expiry'),
        ('general', 'General'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'hr_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class AuditLog(models.Model):
    """
    Audit log model for tracking all changes
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hr_audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} at {self.timestamp}"
