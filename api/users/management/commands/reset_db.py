"""
module for resetting the database in api testing environment
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Reset the database and run the development server'

    def handle(self, *args, **options):
        # Reset the database
        call_command('flush', interactive=False)
        self.stdout.write(self.style.SUCCESS('Database reset successfully.'))