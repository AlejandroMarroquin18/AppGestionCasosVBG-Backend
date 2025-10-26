from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from talleres.models import Workshop
from .models import Participant
from .serializers import ParticipantSerializer
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

@api_view(['POST'])
def register_participant(request, workshop_id):
    print("=== DATOS RECIBIDOS EN BACKEND ===")
    print("Workshop ID:", workshop_id)
    print("Datos recibidos:", request.data)
    print("Headers:", request.headers)
    try:
        workshop = get_object_or_404(Workshop, pk=workshop_id)
        
        # Verificar si hay cupos disponibles
        current_participants = Participant.objects.filter(workshop=workshop).count()
        if current_participants >= workshop.slots:
            return Response(
                {"error": "No hay cupos disponibles para este taller"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si el documento ya está registrado en este taller
        document_number = request.data.get('document_number')
        if Participant.objects.filter(workshop=workshop, document_number=document_number).exists():
            return Response(
                {"error": "Ya estás inscrito en este taller"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ParticipantSerializer(data=request.data)
        
        if serializer.is_valid():
            participant = serializer.save(workshop=workshop)
            
            # Enviar correo de confirmación
            try:
                send_mail(
                    subject=f'Confirmación de inscripción - {workshop.name}',
                    message=f'''Hola {participant.full_name},

¡Gracias por inscribirte en nuestro taller "{workshop.name}"!

Detalles del taller:
📅 Fecha: {workshop.date}
🕒 Hora: {workshop.start_time} - {workshop.end_time}
📍 Lugar: {workshop.location}
📝 Modalidad: {workshop.get_modality_display()}

Te esperamos!

Equipo de Talleres''',
                    from_email='noreply@tusistema.com',
                    recipient_list=[participant.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Error enviando correo: {e}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response(
            {"error": "Error en el servidor: " + str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )