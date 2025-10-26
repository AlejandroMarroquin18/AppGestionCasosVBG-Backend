from django.urls import path
from . import views

urlpatterns = [
    path('talleres/inscripcion/<int:workshop_id>/', views.register_participant, name='register_participant'),
]