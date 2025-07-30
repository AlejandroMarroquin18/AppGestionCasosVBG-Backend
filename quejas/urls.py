# quejas/urls.py
from django.urls import path
from .views import lista_quejas, QuejaViewSet,statistics
from . import views

urlpatterns = [
    path('', QuejaViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='quejas-list'),
    path('<int:pk>/', QuejaViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='quejas-detail'),
    path('statistics', views.statistics, name="Estadisticas talleres")


    
]