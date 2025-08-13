from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clubs.models import Club, Chapter
from emails.services import InvitationService


class Command(BaseCommand):
    help = 'Probar creación de links de invitación'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email del prospecto')
        parser.add_argument('--first-name', type=str, required=True, help='Nombre del prospecto')
        parser.add_argument('--last-name', type=str, required=True, help='Apellido del prospecto')
        parser.add_argument('--club-id', type=int, required=True, help='ID del club')
        parser.add_argument('--chapter-id', type=int, required=True, help='ID del chapter')
        parser.add_argument('--admin-username', type=str, required=True, help='Username del admin')
        parser.add_argument('--role', type=str, default='rider', help='Rol del miembro')
        parser.add_argument('--message', type=str, default='', help='Mensaje personal')

    def handle(self, *args, **options):
        try:
            # Obtener datos necesarios
            admin_user = User.objects.get(username=options['admin_username'])
            club = Club.objects.get(id=options['club_id'])
            chapter = Chapter.objects.get(id=options['chapter_id'])
            
            self.stdout.write(f"🏍️  Creando link de invitación...")
            self.stdout.write(f"   👤 Prospecto: {options['first_name']} {options['last_name']}")
            self.stdout.write(f"   📧 Email: {options['email']}")
            self.stdout.write(f"   🏆 Club: {club.name}")
            self.stdout.write(f"   📍 Chapter: {chapter.name}")
            self.stdout.write(f"   👨‍💼 Admin: {admin_user.username}")
            self.stdout.write(f"   🎯 Rol: {options['role']}")
            
            # Crear link de invitación
            result = InvitationService.create_invitation_link(
                email=options['email'],
                first_name=options['first_name'],
                last_name=options['last_name'],
                club=club,
                chapter=chapter,
                invited_by=admin_user,
                role=options['role'],
                personal_message=options['message']
            )
            
            if result['success']:
                invitation = result['invitation']
                
                self.stdout.write(self.style.SUCCESS("✅ Link de invitación creado exitosamente!"))
                self.stdout.write("")
                self.stdout.write("📋 INFORMACIÓN DE LA INVITACIÓN:")
                self.stdout.write(f"   🔗 Token: {invitation.token}")
                self.stdout.write(f"   ⏰ Expira: {invitation.expires_at.strftime('%d de %B de %Y a las %H:%M')}")
                self.stdout.write("")
                self.stdout.write("🔗 LINKS GENERADOS:")
                self.stdout.write(f"   ✅ Aceptar: {invitation.get_accept_url()}")
                self.stdout.write(f"   ❌ Rechazar: {invitation.get_decline_url()}")
                self.stdout.write("")
                
                # Generar texto para compartir
                sponsor_name = admin_user.get_full_name() or admin_user.username
                share_text = (
                    f"🏍️ Te invito a unirte a {invitation.club.name} - {invitation.chapter.name}\n\n"
                    f"👤 Invitado por: {sponsor_name}\n"
                    f"🎯 Rol: {invitation.intended_role}\n"
                    f"⏰ Expira: {invitation.expires_at.strftime('%d de %B de %Y')}\n\n"
                )
                
                if invitation.personal_message:
                    share_text += f"💬 Mensaje: {invitation.personal_message}\n\n"
                
                share_text += (
                    f"Para ver y responder a la invitación:\n"
                    f"{invitation.get_accept_url()}\n\n"
                    f"¡Únete a nuestra hermandad de motociclistas! 🏍️"
                )
                
                self.stdout.write("📱 TEXTO PARA COMPARTIR:")
                self.stdout.write("=" * 60)
                self.stdout.write(share_text)
                self.stdout.write("=" * 60)
                self.stdout.write("")
                
                # URLs de API para frontend
                self.stdout.write("🔧 API ENDPOINTS:")
                self.stdout.write(f"   📋 Info: /api/invitations/{invitation.token}/info/")
                self.stdout.write(f"   ✅ Aceptar: /api/invitations/{invitation.token}/aceptar/")
                self.stdout.write(f"   ❌ Rechazar: /api/invitations/{invitation.token}/rechazar/")
                
                self.stdout.write(self.style.SUCCESS("\n🎉 ¡Link listo para compartir por WhatsApp, Telegram, etc!"))
                
            else:
                self.stdout.write(self.style.ERROR(f"❌ Error: {result['message']}"))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Usuario admin '{options['admin_username']}' no encontrado"))
        except Club.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Club con ID {options['club_id']} no encontrado"))
        except Chapter.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Chapter con ID {options['chapter_id']} no encontrado"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error inesperado: {str(e)}"))
