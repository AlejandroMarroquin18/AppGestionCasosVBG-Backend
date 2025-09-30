# quejas/urls.py
from django.urls import path
from .views import lista_quejas, QuejaViewSet,statistics
from . import views
from . import historialview





urlpatterns = [
    path('', QuejaViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='quejas-list'),
    path('statistics/', views.statistics, name="Estadisticas talleres"),
    path('validarquejaid/<int:case_id>/', views.validar_case_id, name='validar id queja'),
    path('<int:pk>/', QuejaViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy',
        'patch': 'partial_update'
    }), name='quejas-detail'),



    # Lista completa y creación
    path('historial-quejas/', historialview.HistorialQuejaViewSet.as_view({
        'post': 'create'
    }), name='historialqueja-list'),
    # GET filtrado por caso_id y POST para crear
    path('historial-quejas/<int:caso_id>/', historialview.HistorialQuejaViewSet.as_view({
    'get': 'retrieve_by_caso',
    
    }), name='historialqueja-by-caso'),

    # CRUD para un historial específico
    path('historial-queja/<int:pk>/', historialview.HistorialQuejaViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
    }), name='historialqueja-detail'),
    


    
]