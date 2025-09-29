"""
Custom permissions and decorators for role-based access control
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class RoleBasedPermission(BasePermission):
    """
    Custom permission class for role-based access control
    """
    
    def has_permission(self, request, view):
        """
        Check if user has permission based on their role
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required roles from view
        required_roles = getattr(view, 'required_roles', [])
        if not required_roles:
            return True
        
        # Check if user's role is in required roles
        return request.user.role in required_roles
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin and HR can access all objects
        if request.user.can_view_all_data():
            return True
        
        # Employees can only access their own data
        if request.user.is_employee():
            return self._check_employee_object_access(request.user, obj)
        
        return False
    
    def _check_employee_object_access(self, user, obj):
        """
        Check if employee can access specific object
        """
        # Employee can access their own profile
        if hasattr(obj, 'user') and obj.user == user:
            return True
        
        # Employee can access their own employee profile
        if hasattr(obj, 'employee') and obj.employee.user == user:
            return True
        
        # Employee can access their own attendance records
        if hasattr(obj, 'employee') and obj.employee.user == user:
            return True
        
        # Employee can access their own leave requests
        if hasattr(obj, 'employee') and obj.employee.user == user:
            return True
        
        # Employee can access their own payroll records
        if hasattr(obj, 'employee') and obj.employee.user == user:
            return True
        
        # Employee can access their own documents
        if hasattr(obj, 'employee') and obj.employee.user == user:
            return True
        
        return False


def role_required(*roles):
    """
    Decorator to require specific roles for view access
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if request.user.role not in roles:
                logger.warning(f"Access denied for user {request.user.username} with role {request.user.role}")
                return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator to require admin role
    """
    return role_required('admin')(view_func)


def hr_required(view_func):
    """
    Decorator to require HR role
    """
    return role_required('hr')(view_func)


def hr_or_admin_required(view_func):
    """
    Decorator to require HR or admin role
    """
    return role_required('hr', 'admin')(view_func)


def employee_required(view_func):
    """
    Decorator to require employee role
    """
    return role_required('employee')(view_func)


def can_edit_employee_data(view_func):
    """
    Decorator to check if user can edit employee data
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not request.user.can_edit_employee_data():
            logger.warning(f"Edit access denied for user {request.user.username}")
            return JsonResponse({'error': 'Insufficient permissions to edit employee data'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def can_approve_requests(view_func):
    """
    Decorator to check if user can approve requests
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not request.user.can_approve_requests():
            logger.warning(f"Approval access denied for user {request.user.username}")
            return JsonResponse({'error': 'Insufficient permissions to approve requests'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def can_view_all_data(view_func):
    """
    Decorator to check if user can view all data
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not request.user.can_view_all_data():
            logger.warning(f"View all data access denied for user {request.user.username}")
            return JsonResponse({'error': 'Insufficient permissions to view all data'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def owner_or_hr_required(model_class, employee_field='employee'):
    """
    Decorator to require that user is either the owner of the object or HR/Admin
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # HR and Admin can access all objects
            if request.user.can_view_all_data():
                return view_func(request, *args, **kwargs)
            
            # Get object ID from kwargs
            obj_id = kwargs.get('pk') or kwargs.get('id')
            if not obj_id:
                return JsonResponse({'error': 'Object ID required'}, status=400)
            
            try:
                obj = get_object_or_404(model_class, pk=obj_id)
                
                # Check if user is the owner
                if hasattr(obj, employee_field):
                    employee = getattr(obj, employee_field)
                    if hasattr(employee, 'user') and employee.user == request.user:
                        return view_func(request, *args, **kwargs)
                
                # Check if object has user field directly
                if hasattr(obj, 'user') and obj.user == request.user:
                    return view_func(request, *args, **kwargs)
                
                logger.warning(f"Object access denied for user {request.user.username}")
                return JsonResponse({'error': 'Access denied to this object'}, status=403)
                
            except Exception as e:
                logger.error(f"Error checking object access: {str(e)}")
                return JsonResponse({'error': 'Error accessing object'}, status=500)
        
        return wrapper
    return decorator


class RoleBasedMixin:
    """
    Mixin for class-based views to implement role-based access control
    """
    required_roles = []
    permission_classes = [RoleBasedPermission]
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if self.required_roles and request.user.role not in self.required_roles:
            logger.warning(f"Access denied for user {request.user.username} with role {request.user.role}")
            return JsonResponse({'error': 'Insufficient permissions'}, status=403)
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleBasedMixin):
    """
    Mixin requiring admin role
    """
    required_roles = ['admin']


class HRRequiredMixin(RoleBasedMixin):
    """
    Mixin requiring HR role
    """
    required_roles = ['hr']


class HROrAdminRequiredMixin(RoleBasedMixin):
    """
    Mixin requiring HR or admin role
    """
    required_roles = ['hr', 'admin']


class EmployeeRequiredMixin(RoleBasedMixin):
    """
    Mixin requiring employee role
    """
    required_roles = ['employee']


def audit_log(action, model_name=None, object_id=None, object_repr=None, changes=None):
    """
    Decorator to log user actions for audit purposes
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get request information
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Execute the view
            response = view_func(request, *args, **kwargs)
            
            # Log the action if user is authenticated
            if request.user.is_authenticated:
                from .models import AuditLog
                
                # Get object information if available
                obj_id = object_id or kwargs.get('pk') or kwargs.get('id')
                obj_repr = object_repr or str(request.user)
                
                # Create audit log entry
                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name=model_name or view_func.__name__,
                    object_id=obj_id,
                    object_repr=obj_repr,
                    changes=changes,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            
            return response
        return wrapper
    return decorator


def validate_employee_access(user, employee):
    """
    Validate if user can access employee data
    """
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required")
    
    # Admin and HR can access all employees
    if user.can_view_all_data():
        return True
    
    # Employee can only access their own data
    if user.is_employee():
        if hasattr(employee, 'user') and employee.user == user:
            return True
        if employee == user.employee_profile:
            return True
    
    raise PermissionDenied("Insufficient permissions to access this employee data")


def validate_department_access(user, department):
    """
    Validate if user can access department data
    """
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required")
    
    # Admin and HR can access all departments
    if user.can_view_all_data():
        return True
    
    # Department managers can access their department
    if hasattr(department, 'manager') and department.manager == user:
        return True
    
    # Employees can access their own department
    if user.is_employee() and hasattr(user, 'employee_profile'):
        if user.employee_profile.department == department:
            return True
    
    raise PermissionDenied("Insufficient permissions to access this department data")


class SecureFileUploadMixin:
    """
    Mixin for secure file uploads with validation
    """
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def validate_file(self, file):
        """
        Validate uploaded file
        """
        import os
        
        # Check file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(f"File type {file_ext} not allowed")
        
        # Check file size
        if file.size > self.MAX_FILE_SIZE:
            raise ValidationError(f"File size exceeds {self.MAX_FILE_SIZE / (1024*1024)}MB limit")
        
        return True


def rate_limit(max_requests=100, window_seconds=3600):
    """
    Decorator for rate limiting API requests
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Simple rate limiting using cache (implement with Redis in production)
            from django.core.cache import cache
            
            cache_key = f"rate_limit_{request.user.id}_{view_func.__name__}"
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= max_requests:
                return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
            # Increment counter
            cache.set(cache_key, current_requests + 1, window_seconds)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
