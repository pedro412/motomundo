from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clubs.models import Club, Chapter, ClubAdmin, ChapterManager


class Command(BaseCommand):
    help = 'Create club admin and chapter manager roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-club-admin',
            action='store_true',
            help='Create a club admin role',
        )
        parser.add_argument(
            '--create-chapter-manager',
            action='store_true',
            help='Create a chapter manager role',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the user to assign the role to',
        )
        parser.add_argument(
            '--club-id',
            type=int,
            help='ID of the club (for club admin role)',
        )
        parser.add_argument(
            '--chapter-id',
            type=int,
            help='ID of the chapter (for chapter manager role)',
        )

    def handle(self, *args, **options):
        if options['create_club_admin']:
            self.create_club_admin(options)
        elif options['create_chapter_manager']:
            self.create_chapter_manager(options)
        else:
            self.stdout.write(
                self.style.ERROR('Please specify either --create-club-admin or --create-chapter-manager')
            )

    def create_club_admin(self, options):
        username = options.get('username')
        club_id = options.get('club_id')

        if not username or not club_id:
            self.stdout.write(
                self.style.ERROR('Both --username and --club-id are required for creating club admin')
            )
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return

        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Club with ID {club_id} does not exist')
            )
            return

        club_admin, created = ClubAdmin.objects.get_or_create(
            user=user,
            club=club,
            defaults={'created_by': None}
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created club admin role for {user.username} at {club.name}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Club admin role already exists for {user.username} at {club.name}'
                )
            )

    def create_chapter_manager(self, options):
        username = options.get('username')
        chapter_id = options.get('chapter_id')

        if not username or not chapter_id:
            self.stdout.write(
                self.style.ERROR('Both --username and --chapter-id are required for creating chapter manager')
            )
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return

        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Chapter with ID {chapter_id} does not exist')
            )
            return

        chapter_manager, created = ChapterManager.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={'created_by': None}
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created chapter manager role for {user.username} at {chapter.name}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Chapter manager role already exists for {user.username} at {chapter.name}'
                )
            )
