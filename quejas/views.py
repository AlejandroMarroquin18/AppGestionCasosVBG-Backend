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

class QuejaViewSet(viewsets.ModelViewSet):
    queryset = Queja.objects.all()
    serializer_class = QuejaSerializer


@api_view(['GET'])
def lista_quejas(request):
    if request.method == 'GET':
        quejas = Queja.objects.all()
        serializer = QuejaSerializer(quejas, many=True)
        return Response(serializer.data)
