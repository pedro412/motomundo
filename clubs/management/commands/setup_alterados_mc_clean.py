from django.core.management.base import BaseCommand
from clubs.models import Club, Chapter


class Command(BaseCommand):
    help = 'Sets up Alterados MC club and initial chapters'

    def handle(self, *args, **options):
        # Create or get Alterados MC club
        club, created = Club.objects.get_or_create(
            name="Alterados MC",
            defaults={
                'description': 'Alterados Motorcycle Club - Una hermandad de motociclistas unidos por la pasión y el respeto.',
                'website': '',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created club: {club.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Club already exists: {club.name}')
            )
        
        # Create all 13 Alterados MC chapters
        chapters_to_create = [
            {
                'name': 'Nacional',
                'description': 'Capítulo Nacional - Sede principal de Alterados MC'
            },
            {
                'name': 'Ciudad del Carmen',
                'description': 'Capítulo de Ciudad del Carmen, Campeche'
            },
            {
                'name': 'Cancún',
                'description': 'Capítulo de Cancún, Quintana Roo'
            },
            {
                'name': 'Mérida',
                'description': 'Capítulo de Mérida, Yucatán'
            },
            {
                'name': 'Chetumal',
                'description': 'Capítulo de Chetumal, Quintana Roo'
            },
            {
                'name': 'Campeche',
                'description': 'Capítulo de Campeche, Campeche'
            },
            {
                'name': 'Playa del Carmen',
                'description': 'Capítulo de Playa del Carmen, Quintana Roo'
            },
            {
                'name': 'Cozumel',
                'description': 'Capítulo de Cozumel, Quintana Roo'
            },
            {
                'name': 'Valladolid',
                'description': 'Capítulo de Valladolid, Yucatán'
            },
            {
                'name': 'Tulum',
                'description': 'Capítulo de Tulum, Quintana Roo'
            },
            {
                'name': 'Escárcega',
                'description': 'Capítulo de Escárcega, Campeche'
            },
            {
                'name': 'Progreso',
                'description': 'Capítulo de Progreso, Yucatán'
            },
            {
                'name': 'Akumal',
                'description': 'Capítulo de Akumal, Quintana Roo'
            }
        ]
        
        for chapter_data in chapters_to_create:
            chapter, created = Chapter.objects.get_or_create(
                club=club,
                name=chapter_data['name'],
                defaults={
                    'description': chapter_data['description']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created chapter: {chapter.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Chapter already exists: {chapter.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Alterados MC setup completed successfully!')
        )
