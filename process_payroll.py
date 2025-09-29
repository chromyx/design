"""
Management command to process payroll
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from hr.models import Employee, Payroll, Attendance
from hr.notifications import NotificationService


class Command(BaseCommand):
    help = 'Process payroll for employees'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            choices=['weekly', 'biweekly', 'monthly'],
            default='biweekly',
            help='Payroll period',
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for payroll period (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for payroll period (YYYY-MM-DD)',
        )

    def handle(self, *args, **options):
        period = options['period']
        start_date_str = options.get('start_date')
        end_date_str = options.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        else:
            # Calculate default dates based on period
            today = date.today()
            if period == 'weekly':
                start_date = today - timedelta(days=7)
                end_date = today
            elif period == 'biweekly':
                start_date = today - timedelta(days=14)
                end_date = today
            else:  # monthly
                start_date = today.replace(day=1) - timedelta(days=1)
                start_date = start_date.replace(day=1)
                end_date = today
        
        self.stdout.write(f'Processing {period} payroll from {start_date} to {end_date}...')
        
        employees = Employee.objects.filter(status='active')
        processed_count = 0
        
        for employee in employees:
            # Check if payroll already exists for this period
            existing_payroll = Payroll.objects.filter(
                employee=employee,
                pay_period_start=start_date,
                pay_period_end=end_date
            ).first()
            
            if existing_payroll:
                self.stdout.write(f'Payroll already exists for {employee.user.get_full_name()}')
                continue
            
            # Calculate hours worked from attendance
            attendances = Attendance.objects.filter(
                employee=employee,
                date__range=[start_date, end_date]
            )
            
            total_hours = sum(attendance.work_hours for attendance in attendances)
            total_overtime = sum(attendance.overtime_hours for attendance in attendances)
            
            # Create payroll record
            payroll = Payroll.objects.create(
                employee=employee,
                pay_period_start=start_date,
                pay_period_end=end_date,
                base_salary=employee.base_salary,
                hours_worked=total_hours,
                overtime_hours=total_overtime,
                deductions=Decimal('0.00'),
                bonuses=Decimal('0.00'),
                status='draft',
            )
            
            # Send notification
            NotificationService.notify_payroll_ready(payroll)
            
            processed_count += 1
            self.stdout.write(f'Processed payroll for {employee.user.get_full_name()}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed payroll for {processed_count} employees!')
        )
