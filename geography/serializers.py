from rest_framework import serializers
from .models import Country, State

class CountrySerializer(serializers.ModelSerializer):
    states_count = serializers.SerializerMethodField()
    location_coordinates = serializers.SerializerMethodField()
    has_location = serializers.SerializerMethodField()
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'states_count', 'location_coordinates', 'has_location']
    
    def get_states_count(self, obj):
        return obj.states.count()
    
    def get_location_coordinates(self, obj):
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None
    
    def get_has_location(self, obj):
        return bool(obj.location)

class StateSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    location_coordinates = serializers.SerializerMethodField()
    has_location = serializers.SerializerMethodField()
    
    class Meta:
        model = State
        fields = [
            'id', 'name', 'code', 'country', 'country_name', 'country_code',
            'location_coordinates', 'has_location'
        ]
    
    def get_location_coordinates(self, obj):
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None
    
    def get_has_location(self, obj):
        return bool(obj.location)
