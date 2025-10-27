from django.core.management.base import BaseCommand, CommandError
from finance.models import ImportProfile, ImportProfileMapping, Transaction, BusinessEntity, Currency, TransactionCategory, TransactionPattern
from core.models import CustomUser, FamilyUser
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

        # Get first family of user:
        try:
            family_id = FamilyUser.objects.filter(custom_user_id=user.id).first().family_id
        except FamilyUser.DoesNotExist:
            raise CommandError("User '{}' isn't part of a family.".format(username))

        # Create 1 Import Profile
        profile, created = ImportProfile.objects.get_or_create(
                name="Sparkasse MT940",
                family_id=family_id,
                defaults={"description": "Import profile for Sparkasse MT940 files."}
        )
        if created:
            total_record_count += 1

        # Create 10 Business Entities for the family
        business_entity_names = ["KFZ Workshop", "Telekom Deutschland GmbH", "ARAL AG", "FitX Deutschland GmbH", "Penny Nurnberg", "ALDI GmbH + Co. KG Berlin", "Stadt Recklinghausen", "Zoo Dortmund", "AMAZON PAYMENTS EUROPE S.C.A.", "PayPal Europe S.a.r.l. et Cie S.C.A"]
        business_entities = []
        for name in business_entity_names:
            entity, created = BusinessEntity.objects.get_or_create(
                name=name,
                family_id=family_id,
                defaults={"description": f"Description of '{name}' is pending..."}
            )
            business_entities.append(entity)
            if created:
                total_record_count += 1

        # Create an Import Profile Mappings for each option in ImportProfileMappingDestinationColumns:
        mapping, created = ImportProfileMapping.objects.get_or_create(
            import_profile_id=profile,
            from_file_header="Beguenstigter/Zahlungspflichtiger",
            to_transaction_header=ImportProfileMappingDestinationColumns.NAME.value,
        )
        if created:
            total_record_count += 1
        mapping, created = ImportProfileMapping.objects.get_or_create(
            import_profile_id=profile,
            from_file_header="Buchungstext",
            to_transaction_header=ImportProfileMappingDestinationColumns.DESCRIPTION.value,
        )
        if created:
            total_record_count += 1
        mapping, created = ImportProfileMapping.objects.get_or_create(
            import_profile_id=profile,
            from_file_header="Valutadatum",
            to_transaction_header=ImportProfileMappingDestinationColumns.TRANSACTION_DATE.value,
        )
        if created:
            total_record_count += 1
        mapping, created = ImportProfileMapping.objects.get_or_create(
            import_profile_id=profile,
            from_file_header="Verwendungszweck",
            to_transaction_header=ImportProfileMappingDestinationColumns.REFERENCE.value,
        )
        if created:
            total_record_count += 1
        mapping, created = ImportProfileMapping.objects.get_or_create(
            import_profile_id=profile,
            from_file_header="Beguenstigter/Zahlungspflichtiger",
            to_transaction_header=ImportProfileMappingDestinationColumns.BUSINESS_ENTITY_NAME.value,
        )
        if created:
            total_record_count += 1
        mapping, created = ImportProfileMapping.objects.get_or_create(
            import_profile_id=profile,
            from_file_header="Betrag",
            to_transaction_header=ImportProfileMappingDestinationColumns.AMOUNT.value,
        )
        if created:
            total_record_count += 1
        mapping, created = ImportProfileMapping.objects.get_or_create(
            import_profile_id=profile,
            from_file_header="Waehrung",
            to_transaction_header=ImportProfileMappingDestinationColumns.CURRENCY.value,
        )
        if created:
            total_record_count += 1

        # Create EUR currency, if it doesn't already exist
        try:
            Currency.objects.get(code="EUR")
        except Currency.DoesNotExist:
            Currency.objects.create(
                code="EUR",
                description="Euro",
                symbol="€"
            )
            total_record_count += 1

        # Create 7 different Transaction Categories
        categories = [
            {"name": "Food", "description": "Category for food expenses"},
            {"name": "Transportation", "description": "Category for transportation expenses"},
            {"name": "Entertainment", "description": "Category for entertainment expenses"},
            {"name": "Education", "description": "Category for education expenses"},
            {"name": "Healthcare", "description": "Category for healthcare expenses"},
            {"name": "Telecommunications", "description": "Category for telephones, internet, etc."},
            {"name": "Home", "description": "Expenses related to home maintenance and utilities."},
            {"name": "Salary", "description": "Income from employment."},
            {"name": "Social Benefits", "description": "Benefits such as social security payments."},
            {"name": "Charity", "description": "Donations to charity organizations."},
            {"name": "Family", "description": "Money to or from family members."},
            {"name": "Other", "description": "Miscellaneous category for unclassified expenses"}
        ]
        category_objs = []
        for category in categories:
            category_obj, created = TransactionCategory.objects.get_or_create(
                name=category["name"],
                family_id=family_id,
                defaults={
                    "description": category["description"]
                }
            )
            category_objs.append(category_obj)
            if created:
                total_record_count += 1

        # Create 10 Transactions for the family
        for i in range(10):
            Transaction.objects.create(
                import_history_id=None,
                name="Transaction {}".format(i),
                description="Description of '{}' is pending...".format(i),
                transaction_date=datetime.date.today() - datetime.timedelta(days=i*7),
                reference="Reference {}".format(i),
                business_entity_id=business_entities[random.randint(0, 9)],
                amount=random.randint(-1000, 1000),
                currency=Currency.objects.get(code="EUR"),
                created_by=user,
                transaction_category_id=category_objs[random.randint(0, 6)]
            )
            total_record_count += 1

        # Create 5 specific Transaction Patterns to test the transaction imports later
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "01664 MCDONALDS",
            transaction_category_id=TransactionCategory.objects.get(name="Food"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "KFZ Workshop",
            transaction_category_id=TransactionCategory.objects.get(name="Transportation"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "Telekom Deutschland GmbH",
            transaction_category_id=TransactionCategory.objects.get(name="Telecommunications"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "DIE NEUE APOTHEKE",
            transaction_category_id=TransactionCategory.objects.get(name="Healthcare"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "AMAZON PAYMENTS EUROPE S.C.A.",
            transaction_category_id=TransactionCategory.objects.get(name="Other"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "My Best Employer",
            transaction_category_id=TransactionCategory.objects.get(name="Salary"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "Bundesagentur fur Arbeit -Kindergeldt",
            transaction_category_id=TransactionCategory.objects.get(name="Social Benefits"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "E.ON Deutschland GmbH",
            transaction_category_id=TransactionCategory.objects.get(name="Home"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "Stadt Recklinghausen",
            transaction_category_id=TransactionCategory.objects.get(name="Home"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "Die Kirche",
            transaction_category_id=TransactionCategory.objects.get(name="Charity"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "Zahnartz Dr. Utker",
            transaction_category_id=TransactionCategory.objects.get(name="Healthcare"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "Johnny Smith R",
            transaction_category_id=TransactionCategory.objects.get(name="Family"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "ARAL AG",
            transaction_category_id=TransactionCategory.objects.get(name="Transportation"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "PayPal Europe S.a.r.l. et Cie S.C.A",
            transaction_category_id=TransactionCategory.objects.get(name="Other"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1
        (record, iscreated) = TransactionPattern.objects.get_or_create(
            business_entity_name = "Netto Marken-Discoun",
            transaction_category_id=TransactionCategory.objects.get(name="Food"),
            family_id=family_id
        )
        if iscreated:
            total_record_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total_record_count} test records')
        )