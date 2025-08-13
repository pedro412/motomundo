from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clubs.models import Club, Chapter
from emails.services import InvitationService


class Command(BaseCommand):
    help = 'Prueba el sistema de invitaciones enviando un email de prueba'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email destino para la prueba')
        parser.add_argument('--club-id', type=int, required=True, help='ID del club')
        parser.add_argument('--chapter-id', type=int, required=True, help='ID del chapter')
        parser.add_argument('--admin-username', type=str, required=True, help='Username del admin que invita')

    def handle(self, *args, **options):
        email = options['email']
        club_id = options['club_id']
        chapter_id = options['chapter_id']
        admin_username = options['admin_username']

        try:
            # Obtener entidades necesarias
            club = Club.objects.get(id=club_id)
            chapter = Chapter.objects.get(id=chapter_id)
            admin_user = User.objects.get(username=admin_username)

            self.stdout.write(f"🏍️ Enviando invitación de prueba...")
            self.stdout.write(f"   Club: {club.name}")
            self.stdout.write(f"   Chapter: {chapter.name}")
            self.stdout.write(f"   Admin: {admin_user.username}")
            self.stdout.write(f"   Email destino: {email}")

            # Enviar invitación de prueba
            result = InvitationService.send_invitation(
                email=email,
                first_name="Carlos",
                last_name="Motociclista",
                club=club,
                chapter=chapter,
                invited_by=admin_user,
                role='rider',
                personal_message="¡Bienvenido hermano! Te esperamos para rodar juntos en nuestras aventuras por las carreteras."
            )

            if result['success']:
                invitation = result['invitation']
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Invitación enviada exitosamente!")
                )
                self.stdout.write(f"   ID de invitación: {invitation.id}")
                self.stdout.write(f"   Token: {invitation.token}")
                self.stdout.write(f"   Expira: {invitation.expires_at.strftime('%d/%m/%Y')}")
                self.stdout.write(f"   URL de aceptación: {invitation.get_accept_url()}")
                
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error: {result['message']}")
                )

        except Club.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Club con ID {club_id} no existe"))
        except Chapter.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Chapter con ID {chapter_id} no existe"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Usuario {admin_username} no existe"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error inesperado: {str(e)}"))
