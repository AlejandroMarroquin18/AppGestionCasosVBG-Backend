# talleres/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.workshop_list, name='workshop_list'),  # Lista de talleres
    path('<int:pk>/', views.workshop_detail, name='workshop_detail'),  # Detalles del taller
    path('inscripcion/<int:workshop_id>/', views.register_participant, name='register_participant'),  # Inscripción de participantes
]