from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from clubs.permissions import IsClubAdminOrChapterAdmin
from .models import Invitation
from .services import InvitationService
from .serializers import (
    InvitationSerializer, 
    InvitationCreateSerializer, 
    InvitationAcceptSerializer,
    InvitationStatsSerializer
)


class InvitationViewSet(viewsets.ReadOnlyModelViewSet):
    """API para gestión de invitaciones MC"""
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Mostrar solo invitaciones que el usuario puede gestionar"""
        user = self.request.user
        
        if user.is_superuser:
            return Invitation.objects.all().select_related('club', 'chapter', 'invited_by')
        
        # Obtener clubs y chapters que el usuario puede gestionar
        managed_clubs = user.club_admins.all()
        managed_chapters = user.chapter_admins.all()
        
        return Invitation.objects.filter(
            Q(club__in=managed_clubs) | 
            Q(chapter__in=managed_chapters)
        ).select_related('club', 'chapter', 'invited_by').order_by('-created_at')
    
    @action(detail=False, methods=['post'], 
            permission_classes=[IsAuthenticated, IsClubAdminOrChapterAdmin],
            serializer_class=InvitationCreateSerializer)
    def enviar_invitacion(self, request):
        """Enviar invitación a un prospecto"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                result = InvitationService.send_invitation(
                    email=serializer.validated_data['email'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    club=serializer.validated_data['club'],
                    chapter=serializer.validated_data['chapter'],
                    invited_by=request.user,
                    role=serializer.validated_data.get('intended_role', 'rider'),
                    personal_message=serializer.validated_data.get('personal_message', '')
                )
                
                if result['success']:
                    invitation_data = InvitationSerializer(result['invitation']).data
                    return Response({
                        'success': True,
                        'message': result['message'],
                        'invitation': invitation_data,
                        'expires_at': result['invitation'].expires_at,
                        'accept_url': result['invitation'].get_accept_url()
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': False,
                        'message': result['message']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f"Error interno: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], 
            permission_classes=[IsAuthenticated, IsClubAdminOrChapterAdmin],
            serializer_class=InvitationCreateSerializer)
    def crear_link(self, request):
        """Crear link de invitación para compartir (sin enviar email)"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                result = InvitationService.create_invitation_link(
                    email=serializer.validated_data['email'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    club=serializer.validated_data['club'],
                    chapter=serializer.validated_data['chapter'],
                    invited_by=request.user,
                    role=serializer.validated_data.get('intended_role', 'rider'),
                    personal_message=serializer.validated_data.get('personal_message', '')
                )
                
                if result['success']:
                    invitation = result['invitation']
                    invitation_data = InvitationSerializer(invitation).data
                    
                    # Generar texto para compartir
                    sponsor_name = request.user.get_full_name() or request.user.username
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
                    
                    return Response({
                        'success': True,
                        'message': 'Link de invitación creado exitosamente',
                        'invitation': invitation_data,
                        'links': {
                            'accept_url': invitation.get_accept_url(),
                            'decline_url': invitation.get_decline_url(),
                            'info_url': f"/api/invitations/{invitation.token}/info/"
                        },
                        'share_text': share_text,
                        'expires_at': invitation.expires_at
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': False,
                        'message': result['message']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f"Error interno: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[],
            serializer_class=InvitationAcceptSerializer)
    def aceptar(self, request, pk=None):
        """Aceptar invitación (endpoint público)"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user_data = None
                if serializer.validated_data.get('username'):
                    user_data = {
                        'username': serializer.validated_data['username'],
                        'password': serializer.validated_data['password']
                    }
                
                invitation = InvitationService.accept_invitation(
                    token=pk,  # Usando token como pk
                    user_data=user_data
                )
                
                return Response({
                    'success': True,
                    'message': f'¡Bienvenido a {invitation.club.name}!',
                    'club': invitation.club.name,
                    'chapter': invitation.chapter.name,
                    'role': invitation.intended_role
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f"Error interno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[])
    def rechazar(self, request, pk=None):
        """Rechazar invitación (endpoint público)"""
        try:
            invitation = InvitationService.decline_invitation(token=pk)
            
            return Response({
                'success': True,
                'message': f'Invitación a {invitation.club.name} rechazada'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f"Error interno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def estadisticas(self, request):
        """Obtener estadísticas de invitaciones para clubs gestionados"""
        user = request.user
        stats = {}
        
        # Estadísticas para cada club que el usuario gestiona
        for club in user.club_admins.all():
            club_stats = InvitationService.get_club_stats(club)
            stats[club.name] = club_stats
        
        return Response({
            'success': True,
            'stats': stats
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], permission_classes=[])
    def info(self, request, pk=None):
        """Obtener información básica de una invitación (endpoint público)"""
        try:
            invitation = Invitation.objects.get(token=pk)
            
            # Información básica sin datos sensibles
            info = {
                'club_name': invitation.club.name,
                'chapter_name': invitation.chapter.name,
                'invited_name': f"{invitation.first_name} {invitation.last_name}",
                'role': invitation.intended_role,
                'sponsor_name': invitation.invited_by.get_full_name() or invitation.invited_by.username,
                'status': invitation.status,
                'is_expired': invitation.is_expired,
                'expires_at': invitation.expires_at.strftime('%d de %B de %Y'),
                'created_at': invitation.created_at.strftime('%d de %B de %Y')
            }
            
            return Response({
                'success': True,
                'invitation_info': info
            }, status=status.HTTP_200_OK)
            
        except Invitation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invitación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
