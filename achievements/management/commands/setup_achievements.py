"""
Management command to create initial achievements
"""

from django.core.management.base import BaseCommand
from achievements.models import Achievement


class Command(BaseCommand):
    help = 'Create initial achievements for the motomundo system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing achievements',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        achievements_data = [
            # Leadership Achievements
            {
                'code': 'president_badge',
                'name': 'Club President',
                'description': 'Earned by becoming a President of a motorcycle club',
                'category': 'leadership',
                'points': 100,
                'difficulty': 'hard',
                'icon': '👑',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'vice_president_badge',
                'name': 'Vice President',
                'description': 'Earned by becoming a Vice President of a motorcycle club',
                'category': 'leadership',
                'points': 75,
                'difficulty': 'medium',
                'icon': '🥈',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'secretary_badge',
                'name': 'Club Secretary',
                'description': 'Earned by becoming a Secretary of a motorcycle club',
                'category': 'leadership',
                'points': 50,
                'difficulty': 'medium',
                'icon': '📝',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'treasurer_badge',
                'name': 'Club Treasurer',
                'description': 'Earned by becoming a Treasurer of a motorcycle club',
                'category': 'leadership',
                'points': 50,
                'difficulty': 'medium',
                'icon': '💰',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'club_founder_badge',
                'name': 'Club Founder',
                'description': 'Earned by founding and creating a motorcycle club',
                'category': 'leadership',
                'points': 200,
                'difficulty': 'expert',
                'icon': '🏗️',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'multi_club_leader_badge',
                'name': 'Multi-Club Leader',
                'description': 'Earned by holding leadership positions in 2 or more clubs',
                'category': 'leadership',
                'points': 150,
                'difficulty': 'hard',
                'icon': '🌟',
                'is_repeatable': False,
                'requires_verification': False,
            },
            
            # Membership Achievements
            {
                'code': 'first_timer_badge',
                'name': 'First Timer',
                'description': 'Welcome to the community! Earned by joining your first motorcycle club',
                'category': 'membership',
                'points': 25,
                'difficulty': 'easy',
                'icon': '🎉',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'multi_club_member_badge',
                'name': 'Multi-Club Member',
                'description': 'Earned by becoming a member of 2 different motorcycle clubs',
                'category': 'membership',
                'points': 50,
                'difficulty': 'medium',
                'icon': '🤝',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'veteran_rider_badge',
                'name': 'Veteran Rider',
                'description': 'Earned by being a club member for over 1 year',
                'category': 'membership',
                'points': 75,
                'difficulty': 'medium',
                'icon': '🏍️',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'social_butterfly_badge',
                'name': 'Social Butterfly',
                'description': 'Earned by joining 3 or more different motorcycle clubs',
                'category': 'membership',
                'points': 100,
                'difficulty': 'hard',
                'icon': '🦋',
                'is_repeatable': False,
                'requires_verification': False,
            },
            
            # Activity Achievements
            {
                'code': 'chapter_creator_badge',
                'name': 'Chapter Creator',
                'description': 'Earned by creating or managing multiple chapters',
                'category': 'activity',
                'points': 75,
                'difficulty': 'medium',
                'icon': '🏛️',
                'is_repeatable': False,
                'requires_verification': False,
            },
            
            # Milestone Achievements
            {
                'code': 'centurion_badge',
                'name': 'Centurion',
                'description': 'Earned by accumulating 100 achievement points',
                'category': 'milestone',
                'points': 50,
                'difficulty': 'medium',
                'icon': '💯',
                'is_repeatable': False,
                'requires_verification': False,
            },
            {
                'code': 'legend_badge',
                'name': 'Legend',
                'description': 'Earned by accumulating 500 achievement points',
                'category': 'milestone',
                'points': 100,
                'difficulty': 'expert',
                'icon': '🏆',
                'is_repeatable': False,
                'requires_verification': False,
            },
        ]

        created_count = 0
        updated_count = 0

        for data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created achievement: {achievement.name}')
                )
            elif force:
                # Update existing achievement
                for key, value in data.items():
                    if key != 'code':  # Don't update the code
                        setattr(achievement, key, value)
                achievement.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Updated achievement: {achievement.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⏩ Skipped existing achievement: {achievement.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 Achievement setup complete!\n'
                f'Created: {created_count} achievements\n'
                f'Updated: {updated_count} achievements\n'
                f'Total active achievements: {Achievement.objects.filter(is_active=True).count()}'
            )
        )
