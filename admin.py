from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Employee, Department, JobPosition, Attendance, 
    LeaveRequest, Payroll, Document, Notification, AuditLog
)


class EmployeeInline(admin.StackedInline):
    """
    Inline admin for Employee model
    """
    model = Employee
    fk_name = 'user'  # Specify which ForeignKey to use
    can_delete = False
    verbose_name_plural = 'Employee Profile'
    fieldsets = (
        ('Basic Info', {
            'fields': ('department', 'position', 'manager')
        }),
        ('Personal Info', {
            'fields': ('date_of_birth', 'gender', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
            'classes': ('collapse',)
        }),
        ('Employment Info', {
            'fields': ('employment_type', 'status', 'hire_date', 'termination_date', 'probation_end_date')
        }),
        ('Salary Info', {
            'fields': ('base_salary', 'hourly_rate')
        }),
        ('Work Schedule', {
            'fields': ('work_start_time', 'work_end_time', 'work_days_per_week', 'fingerprint_id'),
            'classes': ('collapse',)
        }),
        ('Leave Balances', {
            'fields': ('vacation_days_remaining', 'sick_days_remaining', 'personal_days_remaining'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department', 'position', 'manager')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with role-based fields and Employee inline
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'get_department', 'get_position', 'is_active', 'is_verified', 'created_at')
    list_filter = ('role', 'is_active', 'is_verified', 'employee_profile__department', 'employee_profile__position', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_profile__employee_id')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'avatar', 'phone_number', 'is_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number')}),
    )
    
    inlines = [EmployeeInline]
    
    def get_inline_instances(self, request, obj=None):
        # Only show Employee inline for existing users (not during creation)
        if obj:
            return super().get_inline_instances(request, obj)
        return []
    
    def get_department(self, obj):
        """Get department name for list display"""
        if obj.has_employee_profile() and obj.employee_profile.department:
            return obj.employee_profile.department.name
        return '-'
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'employee_profile__department__name'
    
    def get_position(self, obj):
        """Get position title for list display"""
        if obj.has_employee_profile() and obj.employee_profile.position:
            return obj.employee_profile.position.title
        return '-'
    get_position.short_description = 'Position'
    get_position.admin_order_field = 'employee_profile__position__title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee_profile__department', 'employee_profile__position')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Department admin
    """
    list_display = ('name', 'manager', 'budget', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    """
    Job Position admin
    """
    list_display = ('title', 'department', 'min_salary', 'max_salary', 'is_active', 'created_at')
    list_filter = ('department', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('title',)


# Employee is now managed as an inline in UserAdmin
# Keeping a separate admin for advanced management if needed
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Employee admin for advanced management
    """
    list_display = ('employee_id', 'user', 'department', 'position', 'status', 'hire_date', 'base_salary')
    list_filter = ('status', 'employment_type', 'department', 'position', 'hire_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('employee_id',)
    readonly_fields = ('employee_id',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'employee_id', 'department', 'position', 'manager')
        }),
        ('Personal Info', {
            'fields': ('date_of_birth', 'gender', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
            'classes': ('collapse',)
        }),
        ('Employment Info', {
            'fields': ('employment_type', 'status', 'hire_date', 'termination_date', 'probation_end_date')
        }),
        ('Salary Info', {
            'fields': ('base_salary', 'hourly_rate')
        }),
        ('Work Schedule', {
            'fields': ('work_start_time', 'work_end_time', 'work_days_per_week', 'fingerprint_id'),
            'classes': ('collapse',)
        }),
        ('Leave Balances', {
            'fields': ('vacation_days_remaining', 'sick_days_remaining', 'personal_days_remaining'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'department', 'position', 'manager')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Attendance admin
    """
    list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 'work_hours', 'is_late', 'is_absent')
    list_filter = ('date', 'is_late', 'is_absent', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    ordering = ('-date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee__user')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """
    Leave Request admin
    """
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'status', 'created_at')
    list_filter = ('leave_type', 'status', 'start_date', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee__user', 'approved_by')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    """
    Payroll admin
    """
    list_display = ('employee', 'pay_period_start', 'pay_period_end', 'base_salary', 'net_salary', 'status', 'created_at')
    list_filter = ('status', 'pay_period_start', 'pay_period_end', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    ordering = ('-pay_period_end',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee__user', 'created_by', 'approved_by')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Document admin
    """
    list_display = ('employee', 'document_type', 'title', 'is_verified', 'expiry_date', 'created_at')
    list_filter = ('document_type', 'is_verified', 'expiry_date', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'title')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee__user', 'verified_by')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Notification admin
    """
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Audit Log admin
    """
    list_display = ('user', 'action', 'model_name', 'object_repr', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'object_repr', 'ip_address')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
