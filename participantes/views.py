from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from talleres.models import Workshop
from .models import Participant
from .serializers import ParticipantSerializer

@api_view(['POST'])
def register_participant(request, workshop_id):
    # Verificamos que el taller exista
    workshop = get_object_or_404(Workshop, pk=workshop_id)

    # Usamos el serializer de Participant para validar los datos
    serializer = ParticipantSerializer(data=request.data)
    
    if serializer.is_valid():
        # Guardamos el participante y lo asociamos con el taller
        participant = serializer.save(workshop=workshop)  # Asociamos el taller
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Respondemos con los datos del participante
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
