# quejas/views.py
import re
from django.http import JsonResponse
from .models import Queja
from .serializers import QuejaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from datetime import datetime
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
    
    ####Essto se añade para que al crear una queja, el estado se establezca en 'pendiente' por defecto, ye
    def create(self, request, *args, **kwargs):
         # Copia mutable de los datos recibidos
        data = request.data.copy()
        
        # Modificar el campo que necesitas antes de validar
        data['estado'] = 'Pendiente'  

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def validar_case_id(request, case_id):
    existe = Queja.objects.filter(id=case_id).exists()
    return Response({"exists": existe}, status=status.HTTP_200_OK)

@api_view(['GET'])
def statistics(request):
    conteo_por_anio = {}
    conteo_por_mes = {}

    # Soporta fechas tipo 1/1/2024, 01/01/2024, etc.
    patron_fecha = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})')

    quejas = Queja.objects.all()

    for q in quejas:
        match = patron_fecha.match(q.fecha_recepcion.strip())
        if match:
            dia = int(match.group(1))
            mes = int(match.group(2))
            año = int(match.group(3))

            conteo_por_anio[año] = conteo_por_anio.get(año, 0) + 1
            conteo_por_mes[mes] = conteo_por_mes.get(mes, 0) + 1


    # Total recibido en el año actual (usando campo 'fecha' que debe tener el año)
    ##total_actual = Queja.objects.filter(fecha_recepcion__icontains=str(año_actual)).count()

    # Conteo por estamento del afectado
    estudiantes = Queja.objects.filter(afectado_estamento__iexact='Estudiante').count()
    profesores = Queja.objects.filter(afectado_estamento__iexact='Docente').count()
    funcionarios = Queja.objects.filter(afectado_estamento__iexact='Funcionario').count()
    ##remitidos
    remitidosEstudiantes = Queja.objects.filter(
    afectado_estamento__iexact='Estudiante', estado__iexact='Remitido'
    ).count()
    remitidosProfesores = Queja.objects.filter(
        afectado_estamento__iexact='Docente', estado__iexact='Remitido'
    ).count()
    remitidosFuncionarios = Queja.objects.filter(
        afectado_estamento__iexact='Funcionario', estado__iexact='Remitido'
    ).count()


    # Conteo por facultades del afectado
    facultades = (
        Queja.objects
        .values('afectado_facultad')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Conteo por sedes del afectado
    sedes = (
        Queja.objects
        .values('afectado_sede')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    

    # Conteo por vicerrectoría adscrita del afectado
    vicerrectorias = (
        Queja.objects
        .values('afectado_vicerrectoria_adscrito')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Conteo por identidad de género del afectado
    generos = (
        Queja.objects
        .values('afectado_identidad_genero')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    '''
    Vicerrectoría Académica
    Vicerrectoría Administrativa
    Vicerrectoría de Bienestar Universitario
    Vicerrectoría de Investigaciones
    Vicerrectoría de Regionalización
    Vicerrectoría de Extensión y Proyección Social '''
    return Response({
        'conteo_por_anio': conteo_por_anio,
        'conteo_por_mes': conteo_por_mes,


        'afectado_estudiantes': estudiantes,
        'afectado_profesores': profesores,
        'afectado_funcionarios': funcionarios,
        
        'remitidos_estudiantes': remitidosEstudiantes,
        'remitidos_profesores': remitidosProfesores,
        'remitidos_funcionarios': remitidosFuncionarios,

        
        'conteo_por_facultad_afectado': list(facultades),
        'conteo_por_sede_afectado': list(sedes),
        
        'conteo_por_vicerrectoria_adscrita_afectado': list(vicerrectorias),
        'conteo_por_genero_afectado': list(generos),
    })





