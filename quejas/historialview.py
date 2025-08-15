from rest_framework import viewsets
from rest_framework.response import Response
from .models import HistorialQueja
from .serializers import HistorialQuejaSerializer

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