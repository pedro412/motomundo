from django.contrib import admin
from .models import Invitation, EmailLog


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Admin para gestión de invitaciones"""
    list_display = ['full_name', 'email', 'club', 'chapter', 'status', 'invited_by', 'created_at', 'expires_at']
    list_filter = ['status', 'club', 'chapter', 'intended_role', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'club__name', 'chapter__name']
    readonly_fields = ['token', 'created_at', 'accepted_at']
    raw_id_fields = ['invited_by', 'member']
    
    fieldsets = (
        ('Información del Prospecto', {
            'fields': ('first_name', 'last_name', 'email', 'intended_role')
        }),
        ('Club y Chapter', {
            'fields': ('club', 'chapter')
        }),
        ('Invitación', {
            'fields': ('invited_by', 'personal_message', 'status')
        }),
        ('Control de Tiempo', {
            'fields': ('token', 'expires_at', 'created_at', 'accepted_at'),
            'classes': ('collapse',)
        }),
        ('Miembro Asociado', {
            'fields': ('member',),
            'classes': ('collapse',)
        })
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Nombre completo'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('club', 'chapter', 'invited_by')
    
    def has_delete_permission(self, request, obj=None):
        # Solo permitir eliminar invitaciones pendientes o expiradas
        if obj and obj.status in ['accepted']:
            return False
        return True


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin para logs de emails"""
    list_display = ['invitation_email', 'invitation_club', 'success', 'sent_at']
    list_filter = ['success', 'sent_at', 'invitation__club']
    search_fields = ['invitation__email', 'invitation__first_name', 'invitation__last_name']
    readonly_fields = ['invitation', 'sent_at', 'success', 'error_message']
    
    def invitation_email(self, obj):
        return obj.invitation.email
    invitation_email.short_description = 'Email'
    
    def invitation_club(self, obj):
        return obj.invitation.club.name
    invitation_club.short_description = 'Club'
    
    def has_add_permission(self, request):
        return False  # No permitir crear logs manualmente
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar logs
