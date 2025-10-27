from django.core.management.base import BaseCommand, CommandError
from finance.models import ImportProfile, ImportProfileMapping, Transaction, BusinessEntity, Currency, TransactionCategory, TransactionPattern
from core.models import CustomUser, FamilyUser, Family
import datetime
import random
from core.utils import ImportProfileMappingDestinationColumns


class Command(BaseCommand):
    help = 'Generate test data for the application'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, default=10, help='The username for which to create the data.')

    def handle(self, *args, **options):
        #fake = Faker()
        total_record_count: int = 0
        username = options['user']

        # Get user from username:
        try:
            user = CustomUser.objects.get(username=username)
            print(f"Generating test data for user '{user.username}")
        except CustomUser.DoesNotExist:
            raise CommandError('User with username {} does not exist'.format(username))

        try:
            new_family, created = Family.objects.get_or_create()

            FamilyUser.objects.get_or_create(custom_user_id=user.id).first().family_id
        except FamilyUser.DoesNotExist:
            raise CommandError("User '{}' isn't part of a family.".format(username))

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total_record_count} test records')
        )