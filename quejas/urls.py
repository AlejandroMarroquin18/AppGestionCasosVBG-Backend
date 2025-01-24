# quejas/urls.py
from django.urls import path
from .views import lista_quejas, QuejaViewSet

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
]