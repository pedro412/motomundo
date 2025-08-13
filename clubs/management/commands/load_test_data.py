from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from clubs.models import Club, Chapter, Member, ClubAdmin, ChapterManager


class Command(BaseCommand):
    help = 'Load test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset database before loading test data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting database...')
            # Clear existing data
            ChapterManager.objects.all().delete()
            ClubAdmin.objects.all().delete()
            Member.objects.all().delete()
            Chapter.objects.all().delete()
            Club.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            
            self.stdout.write(self.style.SUCCESS('Database cleared'))

        # Load fixture data
        self.stdout.write('Loading test data...')
        call_command('loaddata', 'test_data.json')
        
        # Set proper passwords for test users
        try:
            harley_admin = User.objects.get(username='harley_admin')
            harley_admin.set_password('testpass123')
            harley_admin.save()

            sf_manager = User.objects.get(username='sf_manager')
            sf_manager.set_password('testpass123')
            sf_manager.save()

            bmw_admin = User.objects.get(username='bmw_admin')
            bmw_admin.set_password('testpass123')
            bmw_admin.save()

            admin = User.objects.get(username='admin')
            admin.set_password('admin123')
            admin.save()

            self.stdout.write(self.style.SUCCESS('User passwords set'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('Some users not found, passwords not updated'))

        # Display summary
        self.stdout.write('\n=== TEST DATA SUMMARY ===')
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'Clubs: {Club.objects.count()}')
        self.stdout.write(f'Chapters: {Chapter.objects.count()}')
        self.stdout.write(f'Members: {Member.objects.count()}')
        self.stdout.write(f'Club Admins: {ClubAdmin.objects.count()}')
        self.stdout.write(f'Chapter Managers: {ChapterManager.objects.count()}')

        self.stdout.write('\n=== TEST USER CREDENTIALS ===')
        self.stdout.write('Superuser: admin / admin123')
        self.stdout.write('Harley Admin: harley_admin / testpass123')
        self.stdout.write('SF Manager: sf_manager / testpass123')
        self.stdout.write('BMW Admin: bmw_admin / testpass123')

        self.stdout.write(self.style.SUCCESS('\n✅ Test data loaded successfully!'))
