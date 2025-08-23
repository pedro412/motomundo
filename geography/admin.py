from django.contrib import admin
from .models import Country, State


from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Country, State

@admin.register(Country)
class CountryAdmin(GISModelAdmin):
    list_display = ['name', 'code', 'states_count', 'has_location', 'has_boundary']
    list_filter = ['name']
    search_fields = ['name', 'code']
    readonly_fields = ['states_count']
    
    # Map widget for geographic fields
    gis_widget_kwargs = {
        'attrs': {'default_zoom': 4},
    }
    
    def states_count(self, obj):
        return obj.states.count()
    states_count.short_description = 'Number of States'
    
    def has_location(self, obj):
        return bool(obj.location)
    has_location.boolean = True
    has_location.short_description = 'Has Coordinates'
    
    def has_boundary(self, obj):
        return bool(obj.boundary)
    has_boundary.boolean = True
    has_boundary.short_description = 'Has Boundaries'

@admin.register(State)
class StateAdmin(GISModelAdmin):
    list_display = ['name', 'country', 'code', 'has_location', 'has_boundary']
    list_filter = ['country', 'country__name']
    search_fields = ['name', 'code', 'country__name']
    list_select_related = ['country']
    
    # Map widget for geographic fields
    gis_widget_kwargs = {
        'attrs': {'default_zoom': 6},
    }
    
    def has_location(self, obj):
        return bool(obj.location)
    has_location.boolean = True
    has_location.short_description = 'Has Coordinates'
    
    def has_boundary(self, obj):
        return bool(obj.boundary)
    has_boundary.boolean = True
    has_boundary.short_description = 'Has Boundaries'
