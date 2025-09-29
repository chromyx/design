"""
Forms for HR system
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    User, Employee, Department, JobPosition, Attendance, 
    LeaveRequest, Payroll, Document, Notification
)


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form with role selection
    """
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Only HR and Admin can create users with HR or Admin roles
        if self.request_user and not self.request_user.can_edit_employee_data():
            self.fields['role'].choices = [('employee', 'Employee')]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form
    """
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Only HR and Admin can change roles
        if self.request_user and not self.request_user.can_edit_employee_data():
            self.fields['role'].widget = forms.HiddenInput()


class DepartmentForm(forms.ModelForm):
    """
    Department form
    """
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager', 'budget', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users who can be managers (HR, Admin, or existing managers)
        self.fields['manager'].queryset = User.objects.filter(
            role__in=['hr', 'admin']
        ).union(
            User.objects.filter(managed_departments__isnull=False)
        ).distinct()


class JobPositionForm(forms.ModelForm):
    """
    Job position form
    """
    class Meta:
        model = JobPosition
        fields = ['title', 'department', 'description', 'requirements', 'min_salary', 'max_salary', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Job Description'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Requirements'}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data


class EmployeeForm(forms.ModelForm):
    """
    Employee form
    """
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'department', 'position', 'manager',
            'date_of_birth', 'gender', 'address',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'employment_type', 'status', 'hire_date', 'termination_date', 'probation_end_date',
            'base_salary', 'hourly_rate',
            'work_start_time', 'work_end_time', 'work_days_per_week',
            'fingerprint_id',
            'vacation_days_remaining', 'sick_days_remaining', 'personal_days_remaining'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'termination_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'probation_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'work_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'work_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'work_days_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 7}),
            'fingerprint_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fingerprint ID'}),
            'vacation_days_remaining': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'sick_days_remaining': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'personal_days_remaining': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter managers to only show employees
        self.fields['manager'].queryset = Employee.objects.filter(status='active')
    
    def clean(self):
        cleaned_data = super().clean()
        hire_date = cleaned_data.get('hire_date')
        termination_date = cleaned_data.get('termination_date')
        probation_end_date = cleaned_data.get('probation_end_date')
        
        if termination_date and hire_date and termination_date < hire_date:
            raise ValidationError('Termination date cannot be before hire date.')
        
        if probation_end_date and hire_date and probation_end_date < hire_date:
            raise ValidationError('Probation end date cannot be before hire date.')
        
        return cleaned_data


class AttendanceForm(forms.ModelForm):
    """
    Attendance form
    """
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in_time', 'check_out_time', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_in_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'check_out_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Filter employees based on user permissions
        if self.request_user and self.request_user.is_employee():
            self.fields['employee'].queryset = Employee.objects.filter(user=self.request_user)
            self.fields['employee'].widget = forms.HiddenInput()
        else:
            self.fields['employee'].queryset = Employee.objects.filter(status='active')
    
    def clean(self):
        cleaned_data = super().clean()
        check_in_time = cleaned_data.get('check_in_time')
        check_out_time = cleaned_data.get('check_out_time')
        
        if check_in_time and check_out_time and check_out_time <= check_in_time:
            raise ValidationError('Check-out time must be after check-in time.')
        
        return cleaned_data


class LeaveRequestForm(forms.ModelForm):
    """
    Leave request form
    """
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'days_requested', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'days_requested': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for leave'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Set default dates
        if not self.instance.pk:
            self.fields['start_date'].initial = date.today()
            self.fields['end_date'].initial = date.today()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        days_requested = cleaned_data.get('days_requested')
        
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError('End date cannot be before start date.')
            
            # Calculate actual days between dates
            actual_days = (end_date - start_date).days + 1
            if days_requested and days_requested != actual_days:
                raise ValidationError(f'Days requested ({days_requested}) does not match date range ({actual_days} days).')
        
        # Check if dates are in the past
        if start_date and start_date < date.today():
            raise ValidationError('Cannot request leave for past dates.')
        
        return cleaned_data


class PayrollForm(forms.ModelForm):
    """
    Payroll form
    """
    class Meta:
        model = Payroll
        fields = [
            'employee', 'pay_period_start', 'pay_period_end',
            'base_salary', 'hours_worked', 'overtime_hours',
            'deductions', 'bonuses', 'status'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'pay_period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pay_period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hours_worked': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'bonuses': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Filter employees based on user permissions
        if self.request_user and self.request_user.is_employee():
            self.fields['employee'].queryset = Employee.objects.filter(user=self.request_user)
            self.fields['employee'].widget = forms.HiddenInput()
        else:
            self.fields['employee'].queryset = Employee.objects.filter(status='active')
    
    def clean(self):
        cleaned_data = super().clean()
        pay_period_start = cleaned_data.get('pay_period_start')
        pay_period_end = cleaned_data.get('pay_period_end')
        
        if pay_period_start and pay_period_end and pay_period_end < pay_period_start:
            raise ValidationError('Pay period end date cannot be before start date.')
        
        return cleaned_data


class DocumentForm(forms.ModelForm):
    """
    Document form
    """
    class Meta:
        model = Document
        fields = ['document_type', 'title', 'file', 'description', 'expiry_date']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 10MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
            import os
            file_ext = os.path.splitext(file.name)[1].lower()
            if file_ext not in allowed_extensions:
                raise ValidationError(f'File type {file_ext} not allowed. Allowed types: {", ".join(allowed_extensions)}')
        
        return file


class LeaveApprovalForm(forms.Form):
    """
    Form for approving/rejecting leave requests
    """
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for rejection (required if rejecting)'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise ValidationError('Rejection reason is required when rejecting a leave request.')
        
        return cleaned_data


class AttendanceSearchForm(forms.Form):
    """
    Form for searching attendance records
    """
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='active'),
        required=False,
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Filter employees based on user permissions
        if self.request_user and self.request_user.is_employee():
            self.fields['employee'].queryset = Employee.objects.filter(user=self.request_user)
            self.fields['employee'].widget = forms.HiddenInput()


class PayrollSearchForm(forms.Form):
    """
    Form for searching payroll records
    """
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='active'),
        required=False,
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Payroll.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Filter employees based on user permissions
        if self.request_user and self.request_user.is_employee():
            self.fields['employee'].queryset = Employee.objects.filter(user=self.request_user)
            self.fields['employee'].widget = forms.HiddenInput()
