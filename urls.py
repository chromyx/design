"""
URL configuration for HR app
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'hr'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('', views.employee_dashboard, name='employee_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    
    # Employee Management URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    
    # Attendance URLs
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/calendar/', views.attendance_calendar, name='attendance_calendar'),
    
    # Leave Request URLs
    path('leave/', views.leave_request_list, name='leave_request_list'),
    path('leave/create/', views.leave_request_create, name='leave_request_create'),
    path('leave/<int:pk>/approve/', views.leave_request_approve, name='leave_request_approve'),
    
    # Payroll URLs
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/create/', views.payroll_create, name='payroll_create'),
    path('payroll/<int:pk>/approve/', views.payroll_approve, name='payroll_approve'),
    path('payroll/<int:pk>/reject/', views.payroll_reject, name='payroll_reject'),
    path('payroll/bulk-process/', views.payroll_bulk_process, name='payroll_bulk_process'),
    path('payroll/generate-payslips/', views.payroll_generate_payslips, name='payroll_generate_payslips'),
    
    # API URLs for AJAX requests
    path('api/employee/<int:pk>/', views.get_employee_data, name='get_employee_data'),
    path('api/notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/attendance/<int:employee_id>/summary/', views.attendance_summary, name='attendance_summary'),
    
    # Export URLs
    path('export/employees/csv/', views.export_employees_csv, name='export_employees_csv'),
    path('export/attendance/csv/', views.export_attendance_csv, name='export_attendance_csv'),
    path('export/payroll/csv/', views.export_payroll_csv, name='export_payroll_csv'),
    path('export/leave-requests/csv/', views.export_leave_requests_csv, name='export_leave_requests_csv'),
    path('export/documents/csv/', views.export_documents_csv, name='export_documents_csv'),
    
    # Document URLs
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:pk>/approve/', views.document_approve, name='document_approve'),
    path('documents/<int:pk>/reject/', views.document_reject, name='document_reject'),
    path('documents/bulk-upload/', views.document_bulk_upload, name='document_bulk_upload'),
    path('documents/expiry-alerts/', views.document_expiry_alerts, name='document_expiry_alerts'),
]
