from rest_framework import serializers
from django.contrib.auth.models import User
from clubs.models import Club, Chapter
from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    """Serializer para invitaciones"""
    club = serializers.PrimaryKeyRelatedField(queryset=Club.objects.all())
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all())
    invited_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    club_name = serializers.CharField(source='club.name', read_only=True)
    chapter_name = serializers.CharField(source='chapter.name', read_only=True)
    
    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'first_name', 'last_name', 'club', 'chapter',
            'intended_role', 'personal_message', 'status', 'status_display',
            'expires_at', 'created_at', 'accepted_at', 'invited_by_name',
            'club_name', 'chapter_name', 'token'
        ]
        read_only_fields = ['token', 'status', 'expires_at', 'created_at', 'accepted_at']
    
    def get_invited_by_name(self, obj):
        return obj.invited_by.get_full_name() or obj.invited_by.username
    
    def validate(self, data):
        """Validaciones para la invitación"""
        club = data.get('club')
        chapter = data.get('chapter')
        
        # Verificar que el chapter pertenezca al club
        if chapter and club and chapter.club != club:
            raise serializers.ValidationError("El chapter debe pertenecer al club seleccionado")
        
        # Verificar email único por club
        email = data.get('email')
        if club and email:
            existing = Invitation.objects.filter(
                email=email, 
                club=club, 
                status='pending'
            ).exists()
            if existing:
                raise serializers.ValidationError(f"Ya existe una invitación pendiente para {email} en {club.name}")
        
        return data


class InvitationCreateSerializer(InvitationSerializer):
    """Serializer simplificado para crear invitaciones"""
    
    class Meta:
        model = Invitation
        fields = [
            'email', 'first_name', 'last_name', 'club', 'chapter',
            'intended_role', 'personal_message'
        ]
    
    def validate_email(self, value):
        """Validar formato de email"""
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Formato de email inválido")
        
        return value.lower()


class InvitationAcceptSerializer(serializers.Serializer):
    """Serializer para aceptar invitaciones"""
    username = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(min_length=8, required=False)
    password_confirm = serializers.CharField(min_length=8, required=False)
    
    def validate(self, data):
        """Validar datos de usuario al aceptar"""
        username = data.get('username')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # Si se proporciona username, se requieren las contraseñas
        if username:
            if not password:
                raise serializers.ValidationError("Se requiere contraseña")
            if not password_confirm:
                raise serializers.ValidationError("Se requiere confirmación de contraseña")
            if password != password_confirm:
                raise serializers.ValidationError("Las contraseñas no coinciden")
            
            # Verificar que el username esté disponible
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError("Este nombre de usuario ya está en uso")
        
        return data


class InvitationStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de invitaciones"""
    total_enviadas = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    aceptadas = serializers.IntegerField()
    rechazadas = serializers.IntegerField()
    expiradas = serializers.IntegerField()
