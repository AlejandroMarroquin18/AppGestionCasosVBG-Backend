
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list_create, name='event-list-create'),     # GET (lista) y POST (crear)
    path('<int:pk>/', views.event_detail, name='event-detail'),      # GET, PUT, DELETE por ID


]