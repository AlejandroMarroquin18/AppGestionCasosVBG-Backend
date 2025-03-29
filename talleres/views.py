# talleres/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import WorkshopSerializer, ParticipantSerializer
from .models import Workshop
from participantes.models import Participant  # Importamos el modelo Participant
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Workshop
from django.db.models import Count, Avg, F
from django.core.mail import send_mail

@api_view(['GET', 'POST'])
def workshop_list(request):
    if request.method == 'GET':
        # Obtener todos los talleres
        workshops = Workshop.objects.all()
        serializer = WorkshopSerializer(workshops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Verifica los datos recibidos para el taller
        print("Datos recibidos para el taller:", request.data)
        
        serializer = WorkshopSerializer(data=request.data)
        
        if serializer.is_valid():
            # Guardar el taller
            workshop = serializer.save()
            return Response(WorkshopSerializer(workshop).data, status=status.HTTP_201_CREATED)
        else:
            print("Error de validación:", serializer.errors)  # Mostrar errores de validación en el backend
            return Response({"message": "Datos inválidos", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PATCH'])  # Agregado PATCH
def workshop_detail(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    if request.method == 'GET':
        serializer = WorkshopSerializer(workshop)
        return Response(serializer.data)
    elif request.method == 'DELETE':

        
        ###Enviar correo a los participantes
        participants = Participant.objects.filter(workshop=workshop)
        
        destinatarios  = [participant.email for participant in participants]
        
        if destinatarios:  # Verificar que haya destinatarios
            remitente = 'dawntest90@gmail.com'
            asunto = f'Cancelacion del taller {workshop.name}'
            mensaje = f'El taller de {workshop.name}, ha sido cancelado, gracias por inscribirte '
            
            send_mail(asunto, mensaje,remitente,destinatarios)
            
            
            

            
        
        workshop.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PATCH':
        serializer = WorkshopSerializer(workshop, data=request.data, partial=True)  # partial=True permite actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_participant(request, workshop_id):
    # Verificamos que el taller exista
    workshop = get_object_or_404(Workshop, pk=workshop_id)

    # Usamos el serializer de Participant para validar los datos
    serializer = ParticipantSerializer(data=request.data)
    
    if serializer.is_valid():
        participant = serializer.save(workshop=workshop)  # Guardamos el participante y lo asociamos al taller
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Respondemos con los datos del participante
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def statistics(request):
    # Número total de talleres
    total_workshops = Workshop.objects.count()

    # Talleres virtuales y presenciales
    virtual_workshops = Workshop.objects.filter(modality='virtual').count()
    in_person_workshops = total_workshops - virtual_workshops

    # Participantes totales
    total_participants = Participant.objects.count()

    # Participantes promedio por taller
    average_participants = Participant.objects.values('workshop').annotate(count=Count('id')).aggregate(Avg('count'))

    # Porcentaje de participantes por género
    gender_stats = Participant.objects.values('gender_identity').annotate(count=Count('id'))

    # Participantes por programa
    program_stats = Participant.objects.values('program').annotate(count=Count('id'))

    data = {
        'total_workshops': total_workshops,
        'virtual_workshops': virtual_workshops,
        'in_person_workshops': in_person_workshops,
        'total_participants': total_participants,
        'average_participants': average_participants.get('count__avg', 0),
        'gender_stats': gender_stats,
        'program_stats': program_stats  # Agregar estadísticas de programa
    }

    return Response(data)