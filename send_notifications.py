"""
Management command to send scheduled notifications
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta

from hr.notifications import NotificationScheduler


class Command(BaseCommand):
    help = 'Send scheduled notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['daily', 'weekly', 'monthly'],
            default='daily',
            help='Type of notifications to send',
        )

    def handle(self, *args, **options):
        notification_type = options['type']
        
        self.stdout.write(f'Sending {notification_type} notifications...')
        
        if notification_type == 'daily':
            NotificationScheduler.run_daily_checks()
        elif notification_type == 'weekly':
            NotificationScheduler.run_weekly_checks()
        elif notification_type == 'monthly':
            NotificationScheduler.run_monthly_checks()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {notification_type} notifications!')
        )
