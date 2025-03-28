# talleres/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.workshop_list, name='workshop_list'),
    path('<int:pk>/', views.workshop_detail, name='workshop_detail'),
]