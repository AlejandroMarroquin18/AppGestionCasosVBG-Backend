from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer
from quejas.models import Queja
from django.db.models import Count, Max
from django.http import JsonResponse
from django.db.models.functions import ExtractYear, ExtractMonth
from utils.decorators import rol_required


# Listar todos los eventos o crear uno nuevo
@api_view(['GET', 'POST'])
@rol_required('admin', 'staff', 'developer')
def event_list_create(request):
    if request.method == 'GET':
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':

        dataCopy = request.data.copy()
        
        # Modificar el campo que necesitas antes de validar
        dataCopy['status'] = 'Pendiente'
        
        
        serializer = EventSerializer(data=dataCopy)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Obtener, actualizar o eliminar un evento por ID
@api_view(['GET', 'PUT', 'DELETE'])
def event_detail(request, pk):
    try:
        event = Event.objects.get(google_event_id=pk)
    except Event.DoesNotExist:
        return Response({'error': 'Evento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EventSerializer(event)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@rol_required('admin', 'staff', 'developer')
def eventos_stats(request):
    # Totales por status
    total_creados = Event.objects.filter(status="Creado").count()
    total_realizados = Event.objects.filter(status="Realizada").count()

    # Relación Event -> Queja por case_id
    eventos_con_queja = Event.objects.filter(case_id__isnull=False)

    # Filtrar y contar por estamento
    total_estudiantes = eventos_con_queja.filter(
        case_id__in=Queja.objects.filter(afectado_estamento="Estudiante").values_list('id', flat=True)
    ).count()

    total_funcionarios = eventos_con_queja.filter(
        case_id__in=Queja.objects.filter(afectado_estamento="Funcionario").values_list('id', flat=True)
    ).count()

    total_profesores = eventos_con_queja.filter(
        case_id__in=Queja.objects.filter(afectado_estamento="Docente").values_list('id', flat=True)
    ).count()

    # Clasificación por facultad
    facultades =  Event.objects.values("case_id__afectado_facultad").annotate(
        total_eventos=Count("id")
    ).order_by("case_id__afectado_facultad")

    generos = Event.objects.values("case_id__afectado_identidad_genero").annotate(
        total=Count("id")
    ).order_by("case_id__afectado_identidad_genero")
    tipo = (
        Event.objects
        .values('type')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    # 1. Conteo por AÑOS
    anios = (
        Event.objects
        .annotate(year=ExtractYear("startdatehour"))
        .values("year")
        .annotate(total=Count("id"))
        .order_by("year")
    )

    # 2. Último año disponible
    last_year = Event.objects.annotate(year=ExtractYear("startdatehour")).aggregate(
        max_year=Max("year")
    )["max_year"]

    # 3. Conteo por MESES del último año
    meses = (
        Event.objects
        .filter(startdatehour__year=last_year)
        .annotate(month=ExtractMonth("startdatehour"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    return JsonResponse({
        "total_eventos_creados": total_creados,
        "total_eventos_realizados": total_realizados,
        "total_estudiantes": total_estudiantes,
        "total_funcionarios": total_funcionarios,
        "total_profesores": total_profesores,
        "conteo_por_facultad_afectado": list(facultades),
        "conteo_por_genero_afectado": list(generos),
        "conteo_por_tipo": list(tipo),
        "conteo_por_anio": list(anios),
        "conteo_por_mes": list(meses)

    }) 