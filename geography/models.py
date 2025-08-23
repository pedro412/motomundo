from django.contrib.gis.db import models as gis_models
from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True, help_text="ISO 3166-1 alpha-2 code")
    
    # Geographic data
    location = gis_models.PointField(null=True, blank=True, help_text="Central point of country")
    boundary = gis_models.MultiPolygonField(null=True, blank=True, help_text="Country boundaries")
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    code = models.CharField(max_length=10, blank=True, help_text="State/province code")
    
    # Geographic data
    location = gis_models.PointField(null=True, blank=True, help_text="Central point of state")
    boundary = gis_models.MultiPolygonField(null=True, blank=True, help_text="State boundaries")
    
    class Meta:
        unique_together = ['name', 'country']
        ordering = ['country__name', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"
