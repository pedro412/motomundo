from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('register/alteradosmc/', views.member_registration, name='member_registration'),
    path('register/alteradosmc/success/', views.member_registration_success, name='member_registration_success'),
]
