from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import HistorialQueja
from .serializers import HistorialQuejaSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class HistorialQuejaViewSet(viewsets.ModelViewSet):
    queryset = HistorialQueja.objects.all()
    serializer_class = HistorialQuejaSerializer

    def list(self, request, *args, **kwargs):
        # Bloqueamos la lista general
        return Response({"detail": "Método no permitido."}, status=405)

    def retrieve_by_caso(self, request, caso_id=None):
        queryset = HistorialQueja.objects.filter(queja_id=caso_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        try:
            serializer.save()
        except ValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=False)
        try:
            serializer.save()
        except ValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)