# quejas/views.py
import re
from django.http import JsonResponse
from .serializers import QuejaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from datetime import datetime
from rest_framework import viewsets
from .serializers import QuejaSerializer
from datetime import timedelta
from .models import Queja, CambioEstado, HistorialQueja

import pandas as pd



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
    def perform_update(self, serializer):
        instance = self.get_object()
        instance._user = self.request.user  # 👈 pasa el usuario a la señal
        serializer.save()
    
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



    ####Tiempo promedio de respuesta a denuncias por parte de las autoridades de la IES.
    estados_finales = ['Atendida', 'Cerrada', 'Resuelta']  # puedes ajustar esto
        
    total_tiempo = timedelta()
    contador = 0

    for queja in Queja.objects.all():
        if not queja.fecha_recepcion:
            continue

        primer_cambio = (
            CambioEstado.objects
            .filter(queja_id=queja, nuevo_estado__in=estados_finales)
            .order_by('fecha')
            .first()
        )

        if primer_cambio:
            diferencia = primer_cambio.fecha - queja.fecha_recepcion
            total_tiempo += diferencia
            contador += 1

    if contador == 0:
        contador = 1  # para evitar división por cero

    promedio = total_tiempo / contador

    avgResponseTime = {
        "tiempo_promedio_dias": promedio.days,
        "tiempo_promedio_horas": round(promedio.total_seconds() / 3600, 2),
        "detalle": str(promedio)
    }


    ####Número de víctimas que reciben acompañamiento psicológico y/o jurídico tras una denuncia de DyVBG.

    # Filtramos todos los registros de acompañamiento
    acompanamientos = HistorialQueja.objects.filter(tipo__in=['Psicológico', 'Jurídico'])

    # Usamos un set para contar víctimas únicas por queja
    victimas_psicologico = set()
    victimas_juridico = set()

    for hist in acompanamientos:
        if hist.tipo == 'Psicológico' and hist.queja_id and hist.queja_id.afectado_nombre:
            victimas_psicologico.add(hist.queja_id.id)
        if hist.tipo == 'Jurídico' and hist.queja_id and hist.queja_id.afectado_nombre:
            victimas_juridico.add(hist.queja_id.id)

    total_acompanamientos = {
        "total_victimas_psicologico": len(victimas_psicologico),
        "total_victimas_juridico": len(victimas_juridico),
        "total_victimas_ambos": len(victimas_psicologico.union(victimas_juridico))
    }


    ###Tasa de reincidencia de agresores dentro de la institución.

    # Excluir registros sin nombre de agresor
    agresores = (
        Queja.objects
        .exclude(agresor_nombre__isnull=True)
        .exclude(agresor_nombre__exact="")
        .values('agresor_nombre')
        .annotate(num_quejas=Count('id'))
    )

    total_agresores = agresores.count()
    agresores_reincidentes = agresores.filter(num_quejas__gt=1).count()

    tasa_reincidencia = 0
    if total_agresores > 0:
        tasa_reincidencia = (agresores_reincidentes / total_agresores) * 100

    tasa_reincidencia = {
        "total_agresores_unicos": total_agresores,
        "agresores_reincidentes": agresores_reincidentes,
        "tasa_reincidencia_porcentaje": round(tasa_reincidencia, 2),
    }    

    
    variacion_denuncias_resueltas_mensual = variacion_denuncias_resueltas('mensual')
    variacion_denuncias_resueltas_semestral = variacion_denuncias_resueltas('semestral')
    variacion_denuncias_resueltas_anual = variacion_denuncias_resueltas('anual')


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
        'tiempo_promedio_respuessta': avgResponseTime,
        'total_acompanamientos': total_acompanamientos,
        'tasa_reincidencia':tasa_reincidencia,
        'variacion_denuncias_resueltas_mensual': variacion_denuncias_resueltas_mensual,
        'variacion_denuncias_resueltas_semestral': variacion_denuncias_resueltas_semestral,
        'variacion_denuncias_resueltas_anual': variacion_denuncias_resueltas_anual
    })





def variacion_denuncias_resueltas(periodo='mensual'):
    """
    Retorna la variación en la cantidad de denuncias resueltas
    por periodo (mensual, semestral o anual).
    """
    
    if periodo not in ['mensual', 'semestral', 'anual']:
        return {"error": "Periodo inválido. Usa mensual, semestral o anual."}

    # Convertir las fechas (porque es un CharField)
    quejas = Queja.objects.filter(estado__iexact="Resuelta").exclude(fecha_recepcion__exact='')
    data = []
    for q in quejas:
        try:
            fecha = datetime.strptime(q.fecha_recepcion, "%Y-%m-%d")
            data.append({'fecha': fecha})
        except ValueError:
            continue  # ignorar si no tiene formato correcto

    if not data:
        return {"detalle": "No hay denuncias resueltas con fecha válida."}

    df = pd.DataFrame(data)

    # Agrupar según el periodo
    if periodo == "mensual":
        df['periodo'] = df['fecha'].dt.to_period('M').astype(str)
    elif periodo == "anual":
        df['periodo'] = df['fecha'].dt.year
    elif periodo == "semestral":
        df['periodo'] = df['fecha'].apply(lambda f: f"{f.year}-S{1 if f.month <= 6 else 2}")

    # Contar cuántas hay por periodo
    conteo = df.groupby('periodo').size().reset_index(name='cantidad').sort_values('periodo')

    # Calcular variación porcentual entre periodos consecutivos
    conteo['variacion_%'] = conteo['cantidad'].pct_change() * 100
    conteo['variacion_%'] = conteo['variacion_%'].fillna(0).round(2)

    resultado = conteo.to_dict(orient='records')

    return resultado