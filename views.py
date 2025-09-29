"""
Views for HR system with role-based access control
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import csv
from io import StringIO
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta, datetime
import json
import logging

from .models import (
    User, Employee, Department, JobPosition, Attendance, 
    LeaveRequest, Payroll, Document, Notification, AuditLog
)
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, DepartmentForm, JobPositionForm,
    EmployeeForm, AttendanceForm, LeaveRequestForm, PayrollForm, DocumentForm,
    LeaveApprovalForm, AttendanceSearchForm, PayrollSearchForm
)
from .permissions import (
    RoleBasedPermission, role_required, hr_required, admin_required,
    hr_or_admin_required, can_edit_employee_data, can_approve_requests,
    can_view_all_data, owner_or_hr_required, audit_log, validate_employee_access,
    validate_department_access, rate_limit
)

logger = logging.getLogger(__name__)


# Authentication Views
def login_view(request):
    """
    Custom login view with audit logging
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Log login
                AuditLog.objects.create(
                    user=user,
                    action='login',
                    model_name='User',
                    object_id=user.id,
                    object_repr=str(user),
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Redirect based on role
                if user.is_admin():
                    return redirect('admin_dashboard')
                elif user.is_hr():
                    return redirect('hr_dashboard')
                else:
                    return redirect('employee_dashboard')
            else:
                messages.error(request, 'Account is disabled.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'hr/auth/login.html')


@login_required
def logout_view(request):
    """
    Custom logout view with audit logging
    """
    user = request.user
    
    # Log logout
    AuditLog.objects.create(
        user=user,
        action='logout',
        model_name='User',
        object_id=user.id,
        object_repr=str(user),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# Dashboard Views
@login_required
def admin_dashboard(request):
    """
    Admin dashboard with system overview
    """
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    # Get statistics
    total_employees = Employee.objects.filter(status='active').count()
    total_departments = Department.objects.filter(is_active=True).count()
    pending_leave_requests = LeaveRequest.objects.filter(status='pending').count()
    pending_payrolls = Payroll.objects.filter(status='draft').count()
    
    # Recent activities
    recent_audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'pending_leave_requests': pending_leave_requests,
        'pending_payrolls': pending_payrolls,
        'recent_audit_logs': recent_audit_logs,
    }
    
    return render(request, 'hr/dashboards/admin_dashboard.html', context)


@login_required
def hr_dashboard(request):
    """
    HR dashboard with HR-specific data
    """
    if not request.user.is_hr():
        messages.error(request, 'Access denied.')
        return redirect('employee_dashboard')
    
    # Get statistics
    total_employees = Employee.objects.filter(status='active').count()
    pending_leave_requests = LeaveRequest.objects.filter(status='pending').count()
    pending_payrolls = Payroll.objects.filter(status='draft').count()
    late_attendances_today = Attendance.objects.filter(
        date=date.today(),
        is_late=True
    ).count()
    
    # Recent leave requests
    recent_leave_requests = LeaveRequest.objects.select_related('employee__user').filter(
        status='pending'
    ).order_by('-created_at')[:5]
    
    # Department statistics
    department_stats = Department.objects.annotate(
        employee_count=Count('employees', filter=Q(employees__status='active'))
    ).filter(is_active=True)
    
    context = {
        'total_employees': total_employees,
        'pending_leave_requests': pending_leave_requests,
        'pending_payrolls': pending_payrolls,
        'late_attendances_today': late_attendances_today,
        'recent_leave_requests': recent_leave_requests,
        'department_stats': department_stats,
    }
    
    return render(request, 'hr/dashboards/hr_dashboard.html', context)


@login_required
def employee_dashboard(request):
    """
    Employee dashboard with personal data
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')
    
    # Get employee statistics
    total_attendance_days = Attendance.objects.filter(employee=employee).count()
    late_days = Attendance.objects.filter(employee=employee, is_late=True).count()
    pending_leave_requests = LeaveRequest.objects.filter(
        employee=employee,
        status='pending'
    ).count()
    
    # Recent attendance
    recent_attendance = Attendance.objects.filter(employee=employee).order_by('-date')[:5]
    
    # Recent leave requests
    recent_leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:5]
    
    # Recent payrolls
    recent_payrolls = Payroll.objects.filter(employee=employee).order_by('-pay_period_end')[:3]
    
    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'employee': employee,
        'total_attendance_days': total_attendance_days,
        'late_days': late_days,
        'pending_leave_requests': pending_leave_requests,
        'recent_attendance': recent_attendance,
        'recent_leave_requests': recent_leave_requests,
        'recent_payrolls': recent_payrolls,
        'unread_notifications': unread_notifications,
    }
    
    return render(request, 'hr/dashboards/employee_dashboard.html', context)


# Employee Management Views
@login_required
@hr_or_admin_required
def employee_list(request):
    """
    List all employees with filtering and search
    """
    employees = Employee.objects.select_related('user', 'department', 'position', 'manager').all()
    
    # Filtering
    search = request.GET.get('search')
    department_id = request.GET.get('department')
    status_filter = request.GET.get('status')
    
    if search:
        employees = employees.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if status_filter:
        employees = employees.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get departments for filter
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'search': search,
        'department_id': department_id,
        'status_filter': status_filter,
    }
    
    return render(request, 'hr/employees/employee_list.html', context)


@login_required
@hr_or_admin_required
def employee_detail(request, pk):
    """
    Employee detail view
    """
    employee = get_object_or_404(Employee, pk=pk)
    
    # Get related data
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')[:10]
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:10]
    payroll_records = Payroll.objects.filter(employee=employee).order_by('-pay_period_end')[:5]
    documents = Document.objects.filter(employee=employee).order_by('-created_at')
    
    context = {
        'employee': employee,
        'attendance_records': attendance_records,
        'leave_requests': leave_requests,
        'payroll_records': payroll_records,
        'documents': documents,
    }
    
    return render(request, 'hr/employees/employee_detail.html', context)


@login_required
@hr_or_admin_required
def employee_create(request):
    """
    Create new employee
    """
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request_user=request.user)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.created_by = request.user
            employee.save()
            
            # Log creation
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='Employee',
                object_id=employee.id,
                object_repr=str(employee),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Employee {employee.user.get_full_name()} created successfully.')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(request_user=request.user)
    
    return render(request, 'hr/employees/employee_form.html', {'form': form, 'title': 'Create Employee'})


@login_required
@hr_or_admin_required
def employee_edit(request, pk):
    """
    Edit employee
    """
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee, request_user=request.user)
        if form.is_valid():
            employee = form.save()
            
            # Log update
            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='Employee',
                object_id=employee.id,
                object_repr=str(employee),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Employee {employee.user.get_full_name()} updated successfully.')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee, request_user=request.user)
    
    return render(request, 'hr/employees/employee_form.html', {'form': form, 'title': 'Edit Employee'})


# Attendance Views
@login_required
def attendance_list(request):
    """
    List attendance records with filtering
    """
    if request.user.can_view_all_data():
        attendances = Attendance.objects.select_related('employee__user').all()
    else:
        attendances = Attendance.objects.filter(employee__user=request.user)
    
    # Apply search form
    search_form = AttendanceSearchForm(request.GET, request_user=request.user)
    if search_form.is_valid():
        employee = search_form.cleaned_data.get('employee')
        start_date = search_form.cleaned_data.get('start_date')
        end_date = search_form.cleaned_data.get('end_date')
        
        if employee:
            attendances = attendances.filter(employee=employee)
        if start_date:
            attendances = attendances.filter(date__gte=start_date)
        if end_date:
            attendances = attendances.filter(date__lte=end_date)
    
    # Pagination
    paginator = Paginator(attendances.order_by('-date'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    
    return render(request, 'hr/attendance/attendance_list.html', context)


@login_required
@hr_or_admin_required
def attendance_create(request):
    """
    Create attendance record
    """
    if request.method == 'POST':
        form = AttendanceForm(request.POST, request_user=request.user)
        if form.is_valid():
            attendance = form.save()
            
            # Log creation
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='Attendance',
                object_id=attendance.id,
                object_repr=str(attendance),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Attendance record created successfully.')
            return redirect('attendance_list')
    else:
        form = AttendanceForm(request_user=request.user)
    
    return render(request, 'hr/attendance/attendance_form.html', {'form': form, 'title': 'Create Attendance Record'})


# Leave Request Views
@login_required
def leave_request_list(request):
    """
    List leave requests
    """
    if request.user.can_view_all_data():
        leave_requests = LeaveRequest.objects.select_related('employee__user').all()
    else:
        leave_requests = LeaveRequest.objects.filter(employee__user=request.user)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(leave_requests.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    
    return render(request, 'hr/leave/leave_request_list.html', context)


@login_required
def leave_request_create(request):
    """
    Create leave request
    """
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request_user=request.user)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user.employee_profile
            leave_request.save()
            
            # Log creation
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='LeaveRequest',
                object_id=leave_request.id,
                object_repr=str(leave_request),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Create notification for HR
            hr_users = User.objects.filter(role='hr')
            for hr_user in hr_users:
                Notification.objects.create(
                    recipient=hr_user,
                    title='New Leave Request',
                    message=f'{request.user.get_full_name()} has submitted a leave request.',
                    notification_type='leave_approval',
                    related_object_id=leave_request.id,
                    related_object_type='LeaveRequest'
                )
            
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('leave_request_list')
    else:
        form = LeaveRequestForm(request_user=request.user)
    
    return render(request, 'hr/leave/leave_request_form.html', {'form': form, 'title': 'Create Leave Request'})


@login_required
@can_approve_requests
def leave_request_approve(request, pk):
    """
    Approve or reject leave request
    """
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            rejection_reason = form.cleaned_data.get('rejection_reason')
            
            if action == 'approve':
                leave_request.approve(request.user)
                message = 'Leave request approved successfully.'
                
                # Create notification for employee
                Notification.objects.create(
                    recipient=leave_request.employee.user,
                    title='Leave Request Approved',
                    message=f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been approved.',
                    notification_type='leave_approval',
                    related_object_id=leave_request.id,
                    related_object_type='LeaveRequest'
                )
            else:
                leave_request.reject(request.user, rejection_reason)
                message = 'Leave request rejected.'
                
                # Create notification for employee
                Notification.objects.create(
                    recipient=leave_request.employee.user,
                    title='Leave Request Rejected',
                    message=f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been rejected. Reason: {rejection_reason}',
                    notification_type='leave_approval',
                    related_object_id=leave_request.id,
                    related_object_type='LeaveRequest'
                )
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name='LeaveRequest',
                object_id=leave_request.id,
                object_repr=str(leave_request),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, message)
            return redirect('leave_request_list')
    else:
        form = LeaveApprovalForm()
    
    context = {
        'leave_request': leave_request,
        'form': form,
    }
    
    return render(request, 'hr/leave/leave_request_approve.html', context)


# Payroll Views
@login_required
def payroll_list(request):
    """
    List payroll records
    """
    if request.user.can_view_all_data():
        payrolls = Payroll.objects.select_related('employee__user').all()
    else:
        payrolls = Payroll.objects.filter(employee__user=request.user)
    
    # Apply search form
    search_form = PayrollSearchForm(request.GET, request_user=request.user)
    if search_form.is_valid():
        employee = search_form.cleaned_data.get('employee')
        status_filter = search_form.cleaned_data.get('status')
        start_date = search_form.cleaned_data.get('start_date')
        end_date = search_form.cleaned_data.get('end_date')
        
        if employee:
            payrolls = payrolls.filter(employee=employee)
        if status_filter:
            payrolls = payrolls.filter(status=status_filter)
        if start_date:
            payrolls = payrolls.filter(pay_period_start__gte=start_date)
        if end_date:
            payrolls = payrolls.filter(pay_period_end__lte=end_date)
    
    # Pagination
    paginator = Paginator(payrolls.order_by('-pay_period_end'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    
    return render(request, 'hr/payroll/payroll_list.html', context)


@login_required
@hr_or_admin_required
def payroll_create(request):
    """
    Create payroll record
    """
    if request.method == 'POST':
        form = PayrollForm(request.POST, request_user=request.user)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.created_by = request.user
            payroll.save()
            
            # Log creation
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='Payroll',
                object_id=payroll.id,
                object_repr=str(payroll),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Payroll record created successfully.')
            return redirect('payroll_list')
    else:
        form = PayrollForm(request_user=request.user)
    
    return render(request, 'hr/payroll/payroll_form.html', {'form': form, 'title': 'Create Payroll Record'})


# API Views for AJAX requests
@login_required
@require_http_methods(["GET"])
def get_employee_data(request, pk):
    """
    Get employee data for AJAX requests
    """
    employee = get_object_or_404(Employee, pk=pk)
    
    # Check permissions
    if not request.user.can_view_all_data() and employee.user != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    data = {
        'id': employee.id,
        'employee_id': employee.employee_id,
        'name': employee.user.get_full_name(),
        'email': employee.user.email,
        'department': employee.department.name if employee.department else None,
        'position': employee.position.title if employee.position else None,
        'status': employee.status,
        'hire_date': employee.hire_date.isoformat(),
        'base_salary': float(employee.base_salary),
    }
    
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, pk):
    """
    Mark notification as read
    """
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    
    return JsonResponse({'status': 'success'})


@login_required
@require_http_methods(["GET"])
def attendance_summary(request, employee_id):
    """
    Get attendance summary for employee
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # Check permissions
    if not request.user.can_view_all_data() and employee.user != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get current month data
    today = date.today()
    start_of_month = today.replace(day=1)
    
    attendances = Attendance.objects.filter(
        employee=employee,
        date__gte=start_of_month
    )
    
    total_days = attendances.count()
    present_days = attendances.filter(check_in_time__isnull=False).count()
    late_days = attendances.filter(is_late=True).count()
    absent_days = attendances.filter(is_absent=True).count()
    
    data = {
        'total_days': total_days,
        'present_days': present_days,
        'late_days': late_days,
        'absent_days': absent_days,
        'attendance_rate': round((present_days / total_days * 100) if total_days > 0 else 0, 2),
    }
    
    return JsonResponse(data)


@login_required
def attendance_calendar(request):
    """
    Calendar view for attendance tracking
    """
    # Get date range (default to current month)
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Calculate date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get attendance data based on user role
    if request.user.is_admin() or request.user.is_hr():
        # HR/Admin can see all employees
        employee_id = request.GET.get('employee_id')
        if employee_id:
            attendances = Attendance.objects.filter(
                employee_id=employee_id,
                date__range=[start_date, end_date]
            ).select_related('employee__user')
        else:
            attendances = Attendance.objects.filter(
                date__range=[start_date, end_date]
            ).select_related('employee__user')
        
        # Get all employees for filter dropdown
        employees = Employee.objects.filter(status='active').select_related('user')
    else:
        # Employees can only see their own attendance
        attendances = Attendance.objects.filter(
            employee=request.user.employee_profile,
            date__range=[start_date, end_date]
        ).select_related('employee__user')
        employees = None
    
    # Create calendar data structure
    calendar_data = {}
    for att in attendances:
        day = att.date.day
        if day not in calendar_data:
            calendar_data[day] = []
        
        calendar_data[day].append({
            'employee_name': att.employee.user.get_full_name(),
            'employee_id': att.employee.employee_id,
            'check_in': att.check_in_time.strftime('%H:%M') if att.check_in_time else 'N/A',
            'check_out': att.check_out_time.strftime('%H:%M') if att.check_out_time else 'N/A',
            'work_hours': float(att.work_hours),
            'overtime_hours': float(att.overtime_hours),
            'is_late': att.is_late,
            'is_absent': att.is_absent,
            'status': 'absent' if att.is_absent else ('late' if att.is_late else 'present')
        })
    
    # Calculate month statistics
    total_attendance_records = attendances.count()
    present_records = attendances.filter(is_absent=False).count()
    absent_records = attendances.filter(is_absent=True).count()
    late_records = attendances.filter(is_late=True).count()
    
    # Navigation dates
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'year': year,
        'month': month,
        'start_date': start_date,
        'end_date': end_date,
        'calendar_data': calendar_data,
        'employees': employees,
        'selected_employee_id': request.GET.get('employee_id', ''),
        'total_records': total_attendance_records,
        'present_records': present_records,
        'absent_records': absent_records,
        'late_records': late_records,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'month_name': start_date.strftime('%B %Y'),
    }
    
    return render(request, 'hr/attendance_calendar.html', context)


# Export Functions
@login_required
@hr_or_admin_required
def export_employees_csv(request):
    """
    Export employee data to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Department', 
        'Position', 'Manager', 'Employment Type', 'Status', 'Hire Date', 
        'Base Salary', 'Work Start Time', 'Work End Time', 'Vacation Days', 
        'Sick Days', 'Personal Days'
    ])
    
    employees = Employee.objects.select_related(
        'user', 'department', 'position', 'manager__user'
    ).all()
    
    for emp in employees:
        writer.writerow([
            emp.employee_id,
            emp.user.first_name,
            emp.user.last_name,
            emp.user.email,
            emp.user.phone_number,
            emp.department.name if emp.department else '',
            emp.position.title if emp.position else '',
            emp.manager.user.get_full_name() if emp.manager else '',
            emp.get_employment_type_display(),
            emp.get_status_display(),
            emp.hire_date,
            emp.base_salary,
            emp.work_start_time,
            emp.work_end_time,
            emp.vacation_days_remaining,
            emp.sick_days_remaining,
            emp.personal_days_remaining,
        ])
    
    return response


@login_required
@hr_or_admin_required
def export_attendance_csv(request):
    """
    Export attendance data to CSV
    """
    # Get date range from request
    start_date = request.GET.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'Employee Name', 'Date', 'Check In', 'Check Out', 
        'Work Hours', 'Overtime Hours', 'Is Late', 'Is Absent', 'Notes'
    ])
    
    attendances = Attendance.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('employee__user').order_by('date', 'employee__employee_id')
    
    for att in attendances:
        writer.writerow([
            att.employee.employee_id,
            att.employee.user.get_full_name(),
            att.date,
            att.check_in_time.strftime('%H:%M') if att.check_in_time else '',
            att.check_out_time.strftime('%H:%M') if att.check_out_time else '',
            att.work_hours,
            att.overtime_hours,
            'Yes' if att.is_late else 'No',
            'Yes' if att.is_absent else 'No',
            att.notes,
        ])
    
    return response


@login_required
@hr_or_admin_required
def export_payroll_csv(request):
    """
    Export payroll data to CSV
    """
    # Get date range from request
    start_date = request.GET.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payroll_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'Employee Name', 'Pay Period Start', 'Pay Period End',
        'Base Salary', 'Hours Worked', 'Overtime Hours', 'Overtime Pay',
        'Deductions', 'Bonuses', 'Net Salary', 'Status', 'Created By', 'Approved By'
    ])
    
    payrolls = Payroll.objects.filter(
        pay_period_start__gte=start_date,
        pay_period_end__lte=end_date
    ).select_related('employee__user', 'created_by', 'approved_by').order_by('pay_period_start')
    
    for payroll in payrolls:
        writer.writerow([
            payroll.employee.employee_id,
            payroll.employee.user.get_full_name(),
            payroll.pay_period_start,
            payroll.pay_period_end,
            payroll.base_salary,
            payroll.hours_worked,
            payroll.overtime_hours,
            payroll.overtime_pay,
            payroll.deductions,
            payroll.bonuses,
            payroll.net_salary,
            payroll.get_status_display(),
            payroll.created_by.get_full_name() if payroll.created_by else '',
            payroll.approved_by.get_full_name() if payroll.approved_by else '',
        ])
    
    return response


@login_required
@hr_or_admin_required
def export_leave_requests_csv(request):
    """
    Export leave requests data to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leave_requests.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'Employee Name', 'Leave Type', 'Start Date', 'End Date',
        'Days Requested', 'Reason', 'Status', 'Approved By', 'Approved At',
        'Rejection Reason'
    ])
    
    leave_requests = LeaveRequest.objects.select_related(
        'employee__user', 'approved_by'
    ).order_by('-created_at')
    
    for req in leave_requests:
        writer.writerow([
            req.employee.employee_id,
            req.employee.user.get_full_name(),
            req.get_leave_type_display(),
            req.start_date,
            req.end_date,
            req.days_requested,
            req.reason,
            req.get_status_display(),
            req.approved_by.get_full_name() if req.approved_by else '',
            req.approved_at.strftime('%Y-%m-%d %H:%M') if req.approved_at else '',
            req.rejection_reason,
        ])
    
    return response


@login_required
@hr_or_admin_required
def export_documents_csv(request):
    """
    Export document data to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="documents.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'Employee Name', 'Document Type', 'Title', 'Description',
        'Upload Date', 'Expiry Date', 'Is Verified', 'Verified By', 'Verified At'
    ])
    
    documents = Document.objects.select_related(
        'employee__user', 'verified_by'
    ).order_by('-created_at')
    
    for doc in documents:
        writer.writerow([
            doc.employee.employee_id,
            doc.employee.user.get_full_name(),
            doc.get_document_type_display(),
            doc.title,
            doc.description,
            doc.created_at.strftime('%Y-%m-%d'),
            doc.expiry_date.strftime('%Y-%m-%d') if doc.expiry_date else '',
            'Yes' if doc.is_verified else 'No',
            doc.verified_by.get_full_name() if doc.verified_by else '',
            doc.verified_at.strftime('%Y-%m-%d %H:%M') if doc.verified_at else '',
        ])
    
    return response


# Payroll Approval Workflow
@login_required
@hr_or_admin_required
def payroll_approve(request, pk):
    """
    Approve payroll record
    """
    payroll = get_object_or_404(Payroll, pk=pk)
    
    if request.method == 'POST':
        if payroll.status == 'pending':
            payroll.status = 'approved'
            payroll.approved_by = request.user
            payroll.approved_at = timezone.now()
            payroll.save()
            
            # Create notification for employee
            Notification.objects.create(
                recipient=payroll.employee.user,
                title='Payroll Approved',
                message=f'Your payroll for {payroll.pay_period_start} to {payroll.pay_period_end} has been approved.',
                notification_type='payroll_approved',
                related_object_id=payroll.id,
                related_object_type='payroll'
            )
            
            messages.success(request, 'Payroll has been approved successfully.')
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='approve_payroll',
                model_name='Payroll',
                object_id=payroll.id,
                object_repr=str(payroll),
                changes=f'Status changed from pending to approved'
            )
        else:
            messages.error(request, 'This payroll has already been processed.')
    
    return redirect('hr:payroll_list')


@login_required
@hr_or_admin_required
def payroll_reject(request, pk):
    """
    Reject payroll record
    """
    payroll = get_object_or_404(Payroll, pk=pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if payroll.status == 'pending':
            payroll.status = 'rejected'
            payroll.approved_by = request.user
            payroll.approved_at = timezone.now()
            payroll.save()
            
            # Create notification for employee
            Notification.objects.create(
                recipient=payroll.employee.user,
                title='Payroll Rejected',
                message=f'Your payroll for {payroll.pay_period_start} to {payroll.pay_period_end} has been rejected. Reason: {rejection_reason}',
                notification_type='payroll_rejected',
                related_object_id=payroll.id,
                related_object_type='payroll'
            )
            
            messages.success(request, 'Payroll has been rejected.')
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='reject_payroll',
                model_name='Payroll',
                object_id=payroll.id,
                object_repr=str(payroll),
                changes=f'Status changed from pending to rejected. Reason: {rejection_reason}'
            )
        else:
            messages.error(request, 'This payroll has already been processed.')
    
    return redirect('hr:payroll_list')


@login_required
@hr_or_admin_required
def payroll_bulk_process(request):
    """
    Bulk process payroll for multiple employees
    """
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employee_ids')
        pay_period_start = request.POST.get('pay_period_start')
        pay_period_end = request.POST.get('pay_period_end')
        
        if not employee_ids or not pay_period_start or not pay_period_end:
            messages.error(request, 'Please select employees and specify pay period.')
            return redirect('hr:payroll_list')
        
        created_count = 0
        for employee_id in employee_ids:
            employee = get_object_or_404(Employee, id=employee_id)
            
            # Check if payroll already exists for this period
            existing_payroll = Payroll.objects.filter(
                employee=employee,
                pay_period_start=pay_period_start,
                pay_period_end=pay_period_end
            ).first()
            
            if not existing_payroll:
                # Calculate hours worked for the period
                attendances = Attendance.objects.filter(
                    employee=employee,
                    date__range=[pay_period_start, pay_period_end]
                )
                
                total_hours = sum(float(att.work_hours) for att in attendances)
                total_overtime = sum(float(att.overtime_hours) for att in attendances)
                
                # Create payroll record
                payroll = Payroll.objects.create(
                    employee=employee,
                    pay_period_start=pay_period_start,
                    pay_period_end=pay_period_end,
                    base_salary=employee.base_salary,
                    hours_worked=total_hours,
                    overtime_hours=total_overtime,
                    status='pending',
                    created_by=request.user
                )
                
                # Calculate net salary
                payroll.calculate_net_salary()
                payroll.save()
                
                created_count += 1
        
        messages.success(request, f'Created {created_count} payroll records.')
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='bulk_create_payroll',
            model_name='Payroll',
            object_id=None,
            object_repr=f'Bulk payroll creation for {created_count} employees',
            changes=f'Created {created_count} payroll records for period {pay_period_start} to {pay_period_end}'
        )
    
    return redirect('hr:payroll_list')


@login_required
@hr_or_admin_required
def payroll_generate_payslips(request):
    """
    Generate PDF payslips for approved payroll records
    """
    if request.method == 'POST':
        payroll_ids = request.POST.getlist('payroll_ids')
        
        if not payroll_ids:
            messages.error(request, 'Please select payroll records to generate payslips.')
            return redirect('hr:payroll_list')
        
        generated_count = 0
        for payroll_id in payroll_ids:
            payroll = get_object_or_404(Payroll, id=payroll_id)
            
            if payroll.status == 'approved' and not payroll.payslip_generated:
                # Mark as payslip generated (in a real system, you'd generate actual PDF)
                payroll.payslip_generated = True
                payroll.save()
                
                # Create notification for employee
                Notification.objects.create(
                    recipient=payroll.employee.user,
                    title='Payslip Available',
                    message=f'Your payslip for {payroll.pay_period_start} to {payroll.pay_period_end} is now available.',
                    notification_type='payslip_available',
                    related_object_id=payroll.id,
                    related_object_type='payroll'
                )
                
                generated_count += 1
        
        messages.success(request, f'Generated {generated_count} payslips.')
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='generate_payslips',
            model_name='Payroll',
            object_id=None,
            object_repr=f'Generated {generated_count} payslips',
            changes=f'Generated payslips for {generated_count} payroll records'
        )
    
    return redirect('hr:payroll_list')


# Document Workflow
@login_required
@hr_or_admin_required
def document_approve(request, pk):
    """
    Approve document verification
    """
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        if not document.is_verified:
            document.is_verified = True
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.save()
            
            # Create notification for employee
            Notification.objects.create(
                recipient=document.employee.user,
                title='Document Verified',
                message=f'Your document "{document.title}" has been verified.',
                notification_type='document_verified',
                related_object_id=document.id,
                related_object_type='document'
            )
            
            messages.success(request, 'Document has been verified successfully.')
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='verify_document',
                model_name='Document',
                object_id=document.id,
                object_repr=str(document),
                changes=f'Document verified: {document.title}'
            )
        else:
            messages.error(request, 'This document has already been verified.')
    
    return redirect('hr:document_list')


@login_required
@hr_or_admin_required
def document_reject(request, pk):
    """
    Reject document verification
    """
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if not document.is_verified:
            # Create notification for employee
            Notification.objects.create(
                recipient=document.employee.user,
                title='Document Rejected',
                message=f'Your document "{document.title}" has been rejected. Reason: {rejection_reason}',
                notification_type='document_rejected',
                related_object_id=document.id,
                related_object_type='document'
            )
            
            messages.success(request, 'Document has been rejected.')
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='reject_document',
                model_name='Document',
                object_id=document.id,
                object_repr=str(document),
                changes=f'Document rejected: {document.title}. Reason: {rejection_reason}'
            )
        else:
            messages.error(request, 'This document has already been verified.')
    
    return redirect('hr:document_list')


@login_required
@hr_or_admin_required
def document_bulk_upload(request):
    """
    Bulk upload documents for multiple employees
    """
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employee_ids')
        document_type = request.POST.get('document_type')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        expiry_date = request.POST.get('expiry_date')
        
        if not employee_ids or not document_type or not title:
            messages.error(request, 'Please select employees and provide document details.')
            return redirect('hr:document_list')
        
        uploaded_files = request.FILES.getlist('files')
        
        if len(uploaded_files) != len(employee_ids):
            messages.error(request, 'Number of files must match number of selected employees.')
            return redirect('hr:document_list')
        
        created_count = 0
        for i, employee_id in enumerate(employee_ids):
            employee = get_object_or_404(Employee, id=employee_id)
            file = uploaded_files[i]
            
            # Create document record
            document = Document.objects.create(
                employee=employee,
                document_type=document_type,
                title=title,
                file=file,
                description=description,
                expiry_date=expiry_date if expiry_date else None,
                is_verified=False
            )
            
            created_count += 1
        
        messages.success(request, f'Uploaded {created_count} documents.')
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='bulk_upload_documents',
            model_name='Document',
            object_id=None,
            object_repr=f'Bulk document upload for {created_count} employees',
            changes=f'Uploaded {created_count} documents of type {document_type}'
        )
    
    return redirect('hr:document_list')


@login_required
@hr_or_admin_required
def document_expiry_alerts(request):
    """
    Check for documents expiring soon and send alerts
    """
    # Get documents expiring in the next 30 days
    expiry_date = date.today() + timedelta(days=30)
    expiring_documents = Document.objects.filter(
        expiry_date__lte=expiry_date,
        expiry_date__gte=date.today(),
        is_verified=True
    ).select_related('employee__user')
    
    alert_count = 0
    for doc in expiring_documents:
        # Create notification for employee
        Notification.objects.create(
            recipient=doc.employee.user,
            title='Document Expiring Soon',
            message=f'Your document "{doc.title}" will expire on {doc.expiry_date}. Please renew it soon.',
            notification_type='document_expiring',
            related_object_id=doc.id,
            related_object_type='document'
        )
        
        alert_count += 1
    
    messages.success(request, f'Sent {alert_count} document expiry alerts.')
    
    # Log the action
    AuditLog.objects.create(
        user=request.user,
        action='send_expiry_alerts',
        model_name='Document',
        object_id=None,
        object_repr=f'Sent {alert_count} document expiry alerts',
        changes=f'Generated alerts for {alert_count} expiring documents'
    )
    
    return redirect('hr:document_list')


@login_required
def document_list(request):
    """
    List all documents with filtering and search
    """
    if not request.user.is_authenticated:
        return redirect('hr:login')
    
    # Get documents based on user role
    if request.user.is_admin() or request.user.is_hr():
        documents = Document.objects.select_related('employee__user', 'verified_by').all()
    else:
        documents = Document.objects.filter(
            employee=request.user.employee_profile
        ).select_related('employee__user', 'verified_by')
    
    # Apply filters
    document_type = request.GET.get('document_type')
    is_verified = request.GET.get('is_verified')
    search = request.GET.get('search')
    
    if document_type:
        documents = documents.filter(document_type=document_type)
    
    if is_verified is not None:
        documents = documents.filter(is_verified=is_verified == 'true')
    
    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(employee__user__first_name__icontains=search) |
            Q(employee__user__last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)
    
    context = {
        'documents': documents,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'filters': {
            'document_type': document_type,
            'is_verified': is_verified,
            'search': search,
        }
    }
    
    return render(request, 'hr/document_list.html', context)
