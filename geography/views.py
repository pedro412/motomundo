from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from .models import Country, State
from .serializers import CountrySerializer, StateSerializer

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]  # Allow public access for geographic data
    
    @action(detail=True, methods=['get'])
    def states(self, request, pk=None):
        """Get all states for a country"""
        country = self.get_object()
        states = country.states.all()
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def states_with_coordinates(self, request, pk=None):
        """Get all states with geographic coordinates"""
        country = self.get_object()
        states = country.states.filter(location__isnull=False)
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.select_related('country')
    serializer_class = StateSerializer
    permission_classes = [AllowAny]  # Allow public access for geographic data
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find states near a given point"""
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            distance_km = float(request.query_params.get('distance', 100))  # Default 100km
            
            point = Point(lng, lat)  # PostGIS uses (longitude, latitude)
            
            # Find states within distance
            nearby_states = State.objects.filter(
                location__isnull=False,
                location__distance_lte=(point, D(km=distance_km))
            ).annotate(
                distance=Distance('location', point)
            ).order_by('distance')
            
            serializer = StateSerializer(nearby_states, many=True)
            return Response({
                'query_point': {'lat': lat, 'lng': lng},
                'distance_km': distance_km,
                'results': serializer.data
            })
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinates. Provide lat, lng, and optionally distance.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def with_coordinates(self, request):
        """Get all states that have coordinates"""
        states = State.objects.filter(location__isnull=False).select_related('country')
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)
