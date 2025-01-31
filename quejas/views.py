# quejas/views.py

from django.http import JsonResponse
from .models import Queja
from .serializers import QuejaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets
from .models import Queja
from .serializers import QuejaSerializer



@api_view(['GET'])
def lista_quejas(request):
    if request.method == 'GET':
        quejas = Queja.objects.all()
        serializer = QuejaSerializer(quejas, many=True)
        return Response(serializer.data)
    


class QuejaViewSet(viewsets.ModelViewSet):
    queryset = Queja.objects.all()  # Recupera todas las quejas
    serializer_class = QuejaSerializer  # Usa el serializer para validar datos
    def get_queryset(self):
        queryset = Queja.objects.all()
        query_params = self.request.query_params

        # Recorrer todos los parámetros y aplicarlos como filtros dinámicos
        filters = {}
        for param, value in query_params.items():
            if param in [f.name for f in Queja._meta.fields]:  # Verificar si el campo existe en el modelo
                filters[param] = value
        
        return queryset.filter(**filters)

