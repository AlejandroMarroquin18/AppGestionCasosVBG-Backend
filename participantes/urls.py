from django.urls import include, path

urlpatterns = [
    path('api/talleres/', include('talleres.urls')),
    path('api/participantes/', include('participantes.urls')),
]