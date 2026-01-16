import csv
import argparse
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tracker.models import FollowUp
from datetime import datetime

class Command(BaseCommand):
    help = 'Imports follow-ups from a CSV file linked to a specific user and their clinic.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, required=True, help='Path to the CSV file')
        parser.add_argument('--username', type=str, required=True, help='Username of the user importing the data')

    def handle(self, *args, **options):
        csv_file_path = options['csv']
        username = options['username']

        # 1. Validate User and Clinic
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        try:
            clinic = user.userprofile.clinic
        except AttributeError:
             raise CommandError(f'User "{username}" does not have a linked UserProfile/Clinic.')

        self.stdout.write(self.style.SUCCESS(f'Importing for User: {username}, Clinic: {clinic.name}'))

        # 2. Process CSV
        created_count = 0
        skipped_count = 0

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Verify headers
                required_headers = {'patient_name', 'phone', 'language', 'due_date', 'notes'}
                if not required_headers.issubset(reader.fieldnames):
                     missing = required_headers - set(reader.fieldnames)
                     raise CommandError(f'CSV missing required columns: {missing}')

                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Validate mandatory fields
                        if not row['patient_name'] or not row['phone'] or not row['due_date']:
                            self.stdout.write(self.style.WARNING(f'Row {row_num}: Skipped - Missing mandatory fields.'))
                            skipped_count += 1
                            continue

                        # Parse Date
                        try:
                            due_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                        except ValueError:
                             self.stdout.write(self.style.WARNING(f'Row {row_num}: Skipped - Invalid date format "{row["due_date"]}". Use YYYY-MM-DD.'))
                             skipped_count += 1
                             continue

                        # Create FollowUp
                        FollowUp.objects.create(
                            clinic=clinic,
                            created_by=user,
                            patient_name=row['patient_name'],
                            phone=row['phone'],
                            language=row['language'],
                            due_date=due_date,
                            notes=row.get('notes', ''),
                            status='pending' 
                        )
                        created_count += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Row {row_num}: Failed - {e}'))
                        skipped_count += 1

        except FileNotFoundError:
            raise CommandError(f'CSV file "{csv_file_path}" not found.')
        except Exception as e:
            raise CommandError(f'An error occurred: {e}')

        # 3. Summary
        self.stdout.write(self.style.SUCCESS('----------------------'))
        self.stdout.write(self.style.SUCCESS(f'Import Complete.'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count}'))
