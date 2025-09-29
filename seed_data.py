"""
Management command to seed initial data for HR system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta, datetime
import random

from hr.models import (
    Department, JobPosition, Employee, Attendance, 
    LeaveRequest, Payroll, Document, Notification
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial data for HR system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Seeding initial data...')
        
        # Create users
        self.create_users()
        
        # Create departments
        self.create_departments()
        
        # Create job positions
        self.create_job_positions()
        
        # Create employees
        self.create_employees()
        
        # Create sample attendance records
        self.create_attendance_records()
        
        # Create sample leave requests
        self.create_leave_requests()
        
        # Create sample payroll records
        self.create_payroll_records()
        
        # Create sample documents
        self.create_documents()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded initial data!')
        )

    def clear_data(self):
        """Clear existing data"""
        Document.objects.all().delete()
        Payroll.objects.all().delete()
        LeaveRequest.objects.all().delete()
        Attendance.objects.all().delete()
        Employee.objects.all().delete()
        JobPosition.objects.all().delete()
        Department.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self):
        """Create initial users"""
        self.stdout.write('Creating users...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@company.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')

        # Create HR user
        hr_user, created = User.objects.get_or_create(
            username='hr_manager',
            defaults={
                'email': 'hr@company.com',
                'first_name': 'HR',
                'last_name': 'Manager',
                'role': 'hr',
                'is_staff': True,
                'is_verified': True,
            }
        )
        if created:
            hr_user.set_password('hr123')
            hr_user.save()
            self.stdout.write(f'Created HR user: {hr_user.username}')

        # Create sample employee users
        employee_data = [
            ('john.doe', 'john.doe@company.com', 'John', 'Doe'),
            ('jane.smith', 'jane.smith@company.com', 'Jane', 'Smith'),
            ('mike.johnson', 'mike.johnson@company.com', 'Mike', 'Johnson'),
            ('sarah.wilson', 'sarah.wilson@company.com', 'Sarah', 'Wilson'),
            ('david.brown', 'david.brown@company.com', 'David', 'Brown'),
            ('lisa.davis', 'lisa.davis@company.com', 'Lisa', 'Davis'),
            ('tom.miller', 'tom.miller@company.com', 'Tom', 'Miller'),
            ('emma.garcia', 'emma.garcia@company.com', 'Emma', 'Garcia'),
        ]

        for username, email, first_name, last_name in employee_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'employee',
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('employee123')
                user.save()
                self.stdout.write(f'Created employee user: {user.username}')

    def create_departments(self):
        """Create departments"""
        self.stdout.write('Creating departments...')
        
        departments_data = [
            ('Human Resources', 'Human Resources Department', 500000),
            ('Information Technology', 'IT Department', 800000),
            ('Finance', 'Finance and Accounting Department', 600000),
            ('Marketing', 'Marketing Department', 400000),
            ('Operations', 'Operations Department', 700000),
        ]

        hr_user = User.objects.get(username='hr_manager')
        
        for name, description, budget in departments_data:
            department, created = Department.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'budget': budget,
                    'manager': hr_user if name == 'Human Resources' else None,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created department: {department.name}')

    def create_job_positions(self):
        """Create job positions"""
        self.stdout.write('Creating job positions...')
        
        positions_data = [
            ('HR Manager', 'Human Resources', 'Manage HR operations', 80000, 100000),
            ('Software Developer', 'Information Technology', 'Develop software applications', 70000, 90000),
            ('Senior Developer', 'Information Technology', 'Lead software development', 90000, 120000),
            ('Financial Analyst', 'Finance', 'Analyze financial data', 65000, 85000),
            ('Accountant', 'Finance', 'Handle accounting tasks', 55000, 75000),
            ('Marketing Specialist', 'Marketing', 'Develop marketing strategies', 60000, 80000),
            ('Operations Manager', 'Operations', 'Manage operations', 75000, 95000),
            ('Operations Coordinator', 'Operations', 'Coordinate operations', 50000, 70000),
        ]

        for title, dept_name, description, min_salary, max_salary in positions_data:
            department = Department.objects.get(name=dept_name)
            position, created = JobPosition.objects.get_or_create(
                title=title,
                department=department,
                defaults={
                    'description': description,
                    'requirements': f'Requirements for {title}',
                    'min_salary': min_salary,
                    'max_salary': max_salary,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created position: {position.title}')

    def create_employees(self):
        """Create employees"""
        self.stdout.write('Creating employees...')
        
        employees_data = [
            ('john.doe', 'Information Technology', 'Software Developer'),
            ('jane.smith', 'Information Technology', 'Senior Developer'),
            ('mike.johnson', 'Finance', 'Financial Analyst'),
            ('sarah.wilson', 'Finance', 'Accountant'),
            ('david.brown', 'Marketing', 'Marketing Specialist'),
            ('lisa.davis', 'Operations', 'Operations Manager'),
            ('tom.miller', 'Operations', 'Operations Coordinator'),
            ('emma.garcia', 'Human Resources', 'HR Manager'),
        ]

        hr_user = User.objects.get(username='hr_manager')
        
        for username, dept_name, position_title in employees_data:
            user = User.objects.get(username=username)
            department = Department.objects.get(name=dept_name)
            position = JobPosition.objects.get(title=position_title, department=department)
            
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'user': user,
                    'department': department,
                    'position': position,
                    'date_of_birth': date(1990, 1, 1) + timedelta(days=random.randint(0, 10000)),
                    'gender': random.choice(['male', 'female']),
                    'address': f'{random.randint(100, 999)} Main St, City, State',
                    'emergency_contact_name': f'Emergency Contact {user.first_name}',
                    'emergency_contact_phone': f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'emergency_contact_relationship': 'Spouse',
                    'employment_type': 'full_time',
                    'status': 'active',
                    'hire_date': date.today() - timedelta(days=random.randint(30, 1000)),
                    'base_salary': position.min_salary + random.randint(0, int(position.max_salary - position.min_salary)),
                    'work_start_time': '09:00:00',
                    'work_end_time': '17:00:00',
                    'work_days_per_week': 5,
                    'fingerprint_id': f'FP{user.username.upper()}',
                    'vacation_days_remaining': random.randint(10, 25),
                    'sick_days_remaining': random.randint(5, 15),
                    'personal_days_remaining': random.randint(2, 8),
                    'created_by': hr_user,
                }
            )
            if created:
                self.stdout.write(f'Created employee: {employee.user.get_full_name()}')

    def create_attendance_records(self):
        """Create sample attendance records"""
        self.stdout.write('Creating attendance records...')
        
        employees = Employee.objects.all()
        start_date = date.today() - timedelta(days=30)
        
        for employee in employees:
            for i in range(30):
                current_date = start_date + timedelta(days=i)
                
                # Skip weekends
                if current_date.weekday() >= 5:
                    continue
                
                # Random attendance
                if random.random() > 0.1:  # 90% attendance rate
                    check_in_time = timezone.make_aware(
                        datetime.combine(current_date, datetime.min.time().replace(hour=9, minute=random.randint(0, 30)))
                    )
                    
                    check_out_time = timezone.make_aware(
                        datetime.combine(current_date, datetime.min.time().replace(hour=17, minute=random.randint(0, 30)))
                    )
                    
                    attendance, created = Attendance.objects.get_or_create(
                        employee=employee,
                        date=current_date,
                        defaults={
                            'check_in_time': check_in_time,
                            'check_out_time': check_out_time,
                            'work_hours': 8.0,
                            'is_late': check_in_time.hour > 9 or (check_in_time.hour == 9 and check_in_time.minute > 15),
                            'is_absent': False,
                        }
                    )
                    if created:
                        attendance.calculate_work_hours()
                        attendance.check_lateness()
                        attendance.save()

    def create_leave_requests(self):
        """Create sample leave requests"""
        self.stdout.write('Creating leave requests...')
        
        employees = Employee.objects.all()
        leave_types = ['vacation', 'sick', 'personal']
        
        for employee in employees:
            # Create 1-3 leave requests per employee
            for _ in range(random.randint(1, 3)):
                start_date = date.today() + timedelta(days=random.randint(1, 30))
                days_requested = random.randint(1, 5)
                end_date = start_date + timedelta(days=days_requested - 1)
                
                leave_request, created = LeaveRequest.objects.get_or_create(
                    employee=employee,
                    start_date=start_date,
                    end_date=end_date,
                    defaults={
                        'leave_type': random.choice(leave_types),
                        'days_requested': days_requested,
                        'reason': f'Leave request for {random.choice(leave_types)}',
                        'status': random.choice(['pending', 'approved', 'rejected']),
                    }
                )
                if created:
                    self.stdout.write(f'Created leave request for {employee.user.get_full_name()}')

    def create_payroll_records(self):
        """Create sample payroll records"""
        self.stdout.write('Creating payroll records...')
        
        employees = Employee.objects.all()
        hr_user = User.objects.get(username='hr_manager')
        
        # Create payroll for last 3 months
        for month_offset in range(3):
            pay_period_start = date.today().replace(day=1) - timedelta(days=30 * month_offset)
            pay_period_end = pay_period_start + timedelta(days=14)  # Bi-weekly
            
            for employee in employees:
                payroll, created = Payroll.objects.get_or_create(
                    employee=employee,
                    pay_period_start=pay_period_start,
                    pay_period_end=pay_period_end,
                    defaults={
                        'base_salary': employee.base_salary,
                        'hours_worked': 80.0,  # 2 weeks * 40 hours
                        'overtime_hours': random.randint(0, 10),
                        'deductions': random.randint(100, 500),
                        'bonuses': random.randint(0, 1000),
                        'status': random.choice(['draft', 'approved', 'paid']),
                        'created_by': hr_user,
                    }
                )
                if created:
                    payroll.calculate_net_salary()
                    payroll.save()

    def create_documents(self):
        """Create sample documents"""
        self.stdout.write('Creating documents...')
        
        employees = Employee.objects.all()
        document_types = ['contract', 'id_card', 'certificate', 'resume']
        
        for employee in employees:
            for doc_type in document_types:
                document, created = Document.objects.get_or_create(
                    employee=employee,
                    document_type=doc_type,
                    defaults={
                        'title': f'{employee.user.get_full_name()} - {doc_type.title()}',
                        'description': f'{doc_type.title()} document for {employee.user.get_full_name()}',
                        'expiry_date': date.today() + timedelta(days=random.randint(30, 365)) if doc_type == 'certificate' else None,
                        'is_verified': random.choice([True, False]),
                    }
                )
                if created:
                    self.stdout.write(f'Created document: {document.title}')
