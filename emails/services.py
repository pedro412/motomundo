from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Invitation, EmailLog
from clubs.models import Member


class InvitationService:
    """Servicio de invitaciones para clubes motociclistas - optimizado para Railway"""
    
    @staticmethod
    def send_invitation(email, first_name, last_name, club, chapter, invited_by, 
                       role='rider', personal_message=''):
        """Enviar invitación a un prospecto"""
        
        # Verificar si ya existe una invitación pendiente
        existing = Invitation.objects.filter(
            email=email, 
            club=club, 
            status='pending'
        ).first()
        
        if existing:
            return {
                'success': False,
                'message': f"{first_name} ya tiene una invitación pendiente a {club.name}",
                'existing_invitation': existing
            }
        
        # Crear la invitación
        invitation = Invitation.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            club=club,
            chapter=chapter,
            invited_by=invited_by,
            intended_role=role,
            personal_message=personal_message
        )
        
        # Crear registro de miembro (placeholder hasta que acepte)
        member = Member.objects.create(
            first_name=first_name,
            last_name=last_name,
            chapter=chapter,
            role=role,
            nickname=f"{first_name} {last_name}",
            user=None  # Se enlazará cuando acepte la invitación
        )
        invitation.member = member
        invitation.save()
        
        # Enviar email inmediatamente (bajo volumen)
        email_sent = InvitationService._send_email(invitation)
        
        # Registrar el intento de envío
        EmailLog.objects.create(
            invitation=invitation,
            success=email_sent,
            error_message="" if email_sent else "Error al enviar email"
        )
        
        return {
            'success': email_sent,
            'invitation': invitation,
            'message': f"Invitación enviada a {email}" if email_sent else "Error al enviar invitación"
        }
    
    @staticmethod
    def create_invitation_link(email, first_name, last_name, club, chapter, invited_by, 
                              role='rider', personal_message=''):
        """Crear invitación sin enviar email (solo generar link para compartir)"""
        
        # Verificar si ya existe una invitación pendiente
        existing = Invitation.objects.filter(
            email=email, 
            club=club, 
            status='pending'
        ).first()
        
        if existing:
            return {
                'success': False,
                'message': f"{first_name} ya tiene una invitación pendiente a {club.name}",
                'existing_invitation': existing
            }
        
        # Crear la invitación
        invitation = Invitation.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            club=club,
            chapter=chapter,
            invited_by=invited_by,
            intended_role=role,
            personal_message=personal_message
        )
        
        # Crear registro de miembro (placeholder hasta que acepte)
        member = Member.objects.create(
            first_name=first_name,
            last_name=last_name,
            chapter=chapter,
            role=role,
            nickname=f"{first_name} {last_name}",
            user=None  # Se enlazará cuando acepte la invitación
        )
        invitation.member = member
        invitation.save()
        
        # NO enviar email, solo crear registro para tracking
        EmailLog.objects.create(
            invitation=invitation,
            success=True,
            error_message="Link creado - email no enviado"
        )
        
        return {
            'success': True,
            'invitation': invitation,
            'message': f"Link de invitación creado para {first_name} {last_name}"
        }
    
    @staticmethod
    def _send_email(invitation):
        """Enviar email de invitación en español"""
        try:
            context = {
                'nombre_prospecto': invitation.first_name,
                'apellido_prospecto': invitation.last_name,
                'nombre_club': invitation.club.name,
                'nombre_chapter': invitation.chapter.name,
                'nombre_padrino': invitation.invited_by.get_full_name() or invitation.invited_by.username,
                'rol': invitation.get_intended_role_display(),
                'mensaje_personal': invitation.personal_message,
                'url_aceptar': invitation.get_accept_url(),
                'url_rechazar': invitation.get_decline_url(),
                'fecha_expira': invitation.expires_at.strftime('%d de %B de %Y'),
                'ubicacion_chapter': getattr(invitation.chapter, 'description', 'Área local'),
            }
            
            # Templates en español
            subject = f"🏍️ Invitación para unirte a {invitation.club.name}"
            message = render_to_string('emails/invitacion.txt', context)
            html_message = render_to_string('emails/invitacion.html', context)
            
            # Enviar usando Railway + SendGrid
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.email],
                html_message=html_message,
                fail_silently=False
            )
            
            return True
            
        except Exception as e:
            print(f"Error enviando invitación MC: {e}")
            return False
    
    @staticmethod
    def accept_invitation(token, user_data=None):
        """Aceptar una invitación"""
        try:
            invitation = Invitation.objects.get(token=token, status='pending')
            
            if invitation.is_expired:
                invitation.status = 'expired'
                invitation.save()
                raise ValueError("La invitación ha expirado")
            
            # Crear cuenta de usuario si se proporcionan datos
            if user_data:
                from django.contrib.auth.models import User
                user = User.objects.create_user(
                    username=user_data.get('username'),
                    email=invitation.email,
                    password=user_data.get('password'),
                    first_name=invitation.first_name,
                    last_name=invitation.last_name
                )
                
                # Enlazar miembro a usuario
                invitation.member.user = user
                invitation.member.save()
            
            # Marcar invitación como aceptada
            invitation.status = 'accepted'
            invitation.accepted_at = timezone.now()
            invitation.save()
            
            return invitation
            
        except Invitation.DoesNotExist:
            raise ValueError("Token de invitación inválido")
    
    @staticmethod
    def decline_invitation(token):
        """Rechazar una invitación"""
        try:
            invitation = Invitation.objects.get(token=token, status='pending')
            invitation.status = 'declined'
            invitation.save()
            
            # Eliminar el registro de miembro placeholder
            if invitation.member and not invitation.member.user:
                invitation.member.delete()
            
            return invitation
            
        except Invitation.DoesNotExist:
            raise ValueError("Token de invitación inválido")
    
    @staticmethod
    def get_club_stats(club):
        """Estadísticas de invitaciones para un club"""
        from django.db.models import Count, Q
        
        stats = Invitation.objects.filter(club=club).aggregate(
            total_enviadas=Count('id'),
            pendientes=Count('id', filter=Q(status='pending')),
            aceptadas=Count('id', filter=Q(status='accepted')),
            rechazadas=Count('id', filter=Q(status='declined')),
            expiradas=Count('id', filter=Q(status='expired'))
        )
        
        return stats
