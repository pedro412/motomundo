from django.db import models
from django.contrib.auth.models import User
from clubs.models import Member, Club, Chapter
import uuid
from datetime import timedelta
from django.utils import timezone


class Invitation(models.Model):
    """Sistema de invitaciones para clubes de motociclistas"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'), 
        ('declined', 'Rechazada'),
        ('expired', 'Expirada'),
    ]
    
    # Información básica del invitado
    email = models.EmailField(verbose_name="Email")
    first_name = models.CharField(max_length=50, verbose_name="Nombre")
    last_name = models.CharField(max_length=50, verbose_name="Apellido")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='invitations')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations', verbose_name="Invitado por")
    
    # Rol que tendrá al aceptar
    intended_role = models.CharField(max_length=20, default='rider', verbose_name="Rol previsto")
    personal_message = models.TextField(blank=True, verbose_name="Mensaje personal", help_text="Mensaje del padrino")
    
    # Control de invitación
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    expires_at = models.DateTimeField(verbose_name="Expira el")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creada el")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Aceptada el")
    
    # Enlace al registro de miembro
    member = models.OneToOneField(Member, on_delete=models.CASCADE, null=True, related_name='invitation')
    
    class Meta:
        unique_together = ['email', 'club', 'status']
        verbose_name = "Invitación"
        verbose_name_plural = "Invitaciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} → {self.club.name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # 30 días para responder (generoso para la comunidad MC)
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def get_accept_url(self):
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/invitaciones/{self.token}/aceptar/"
    
    def get_decline_url(self):
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/invitaciones/{self.token}/rechazar/"


class EmailLog(models.Model):
    """Log simple para seguimiento de emails enviados"""
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name='email_logs')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado el")
    success = models.BooleanField(default=True, verbose_name="Exitoso")
    error_message = models.TextField(blank=True, verbose_name="Mensaje de error")
    
    class Meta:
        verbose_name = "Log de Email"
        verbose_name_plural = "Logs de Emails"
        ordering = ['-sent_at']
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} Email a {self.invitation.email} - {self.sent_at.strftime('%d/%m/%Y %H:%M')}"
