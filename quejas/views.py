# quejas/views.py
import re
from django.http import JsonResponse
from .serializers import (
    QuejaSerializer, 
    HistorialQuejaSerializer,  # Añadir esta importación
    CambioEstadoSerializer,    # Añadir esta también por si acaso
    PersonaReportaSerializer, 
    PersonaAfectadaSerializer, 
    PersonaAcusadaSerializer
)
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from datetime import datetime
from rest_framework import viewsets, permissions
from datetime import timedelta
from .models import Queja, CambioEstado, HistorialQueja, PersonaReporta, PersonaAfectada, PersonaAcusada
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from django.core.mail import EmailMultiAlternatives
from appvbgbackend import settings
from rest_framework.exceptions import PermissionDenied
from utils.decorators import rol_required
from collections import Counter
import pandas as pd

@api_view(['GET'])
@rol_required('admin', 'staff', 'developer')
def lista_quejas(request):
    if request.method == 'GET':
        quejas = Queja.objects.all()
        serializer = QuejaSerializer(quejas, many=True)
        return Response(serializer.data)

class QuejaViewSet(viewsets.ModelViewSet):
    queryset = Queja.objects.all()
    serializer_class = QuejaSerializer
    
    def get_queryset(self):
        user = self.request.user
        if not user:
            return Queja.objects.none()

        queryset = Queja.objects.all()

        if user.rol == "visitor":
            queryset = queryset.filter(
                Q(persona_afectada__correo=user.email) | 
                Q(persona_reporta__correo=user.email)
            )

        query_params = self.request.query_params
        filters = {}
        for param, value in query_params.items():
            if param in [f.name for f in Queja._meta.fields]:
                filters[param] = value
        
        return queryset.filter(**filters)
    
    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if user.rol == "visitor":
            raise PermissionDenied("No tienes permiso para modificar esta queja.")

        instance._user = self.request.user
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.rol == "visitor":
            raise PermissionDenied("No tienes permiso para eliminar esta queja.")

        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        
        if user.rol == "visitor":
            if (instance.persona_afectada.correo != user.email and 
                instance.persona_reporta.correo != user.email):
                raise PermissionDenied("No tienes permiso para ver esta queja.")

        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['estado'] = 'Pendiente'

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Enviar correo de notificación al área
        subject = "Nueva Queja Registrada"
        queja_data = serializer.data
        
        # Obtener nombres de las personas relacionadas - CON MANEJO DE NULL
        reporta_nombre = queja_data.get('persona_reporta', {}).get('nombre', 'N/A')
        fecha_recepcion = queja_data.get('persona_reporta', {}).get('fecha_recepcion', 'N/A')
        
        # Obtener datos de persona_afectada si existe
        persona_afectada = queja_data.get('persona_afectada')
        afectado_nombre = persona_afectada.get('nombre', 'N/A') if persona_afectada else 'No especificado'
        afectado_correo = persona_afectada.get('correo') if persona_afectada else None
        
        # Obtener datos de persona_reporta
        persona_reporta = queja_data.get('persona_reporta', {})
        reporta_correo = persona_reporta.get('correo')
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color:#444;">📢 Nueva queja registrada</h2>
            <p>Se ha registrado una nueva queja en la plataforma.</p>
            <p><strong>Detalles de la queja:</strong></p>
            <ul>
                <li><strong>ID:</strong> {queja_data['id']}</li>
                <li><strong>Fecha de recepción:</strong> {fecha_recepcion}</li>
                <li><strong>Estado actual:</strong> {queja_data['estado']}</li>
                <li><strong>Registrada por:</strong> {reporta_nombre}</li>
                <li><strong>Persona afectada:</strong> {afectado_nombre}</li>
            </ul>
            <p>Le recomendamos ingresar al panel administrativo para revisar los detalles y asignar seguimiento.</p>
            <p>
                <a href="{getattr(settings, 'BACKEND_URL', '#')}" 
                style="background-color:#007bff;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">
                Ir al panel
                </a>
            </p>
            <br>
            <p>Atentamente,<br>
            <strong>Plataforma para la gestión de atención de violencias basadas en género</strong><br>
            </p>
        </body>
        </html>
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=getattr(settings, "CORREO_AREA_VBG", settings.DEFAULT_FROM_EMAIL),
            to=[settings.CORREO_AREA_VBG],
        )
        email.attach_alternative(html_content, "text/html")

        try:
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Error al enviar correo: {e}")

        # Enviar correo de confirmación a los usuarios
        subject_user = "Confirmación de registro de queja"
        
        html_content_user = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color:#444;">📢 Su queja ha sido registrada exitosamente</h2>
            <p>Su queja ha sido recibida por la plataforma y será atendida por el equipo correspondiente.</p>
            <p><strong>Detalles de la queja registrada:</strong></p>
            <ul>
                <li><strong>ID:</strong> {queja_data['id']}</li>
                <li><strong>Fecha de recepción:</strong> {fecha_recepcion}</li>
                <li><strong>Estado actual:</strong> {queja_data['estado']}</li>
                <li><strong>Registrada por:</strong> {reporta_nombre}</li>
            </ul>
            <p>Nos comunicaremos con usted si se requiere información adicional o para informarle sobre el avance del caso.</p>
            <br>
            <p>Atentamente,<br>
            <strong>Plataforma para la gestión de atención de violencias basadas en género</strong><br>
            </p>
        </body>
        </html>
        """

        # Determinar destinatarios (evitando errores si los campos no existen)
        destinatarios = []

        # Solo agregar afectado_correo si existe y no es None
        if afectado_correo:
            destinatarios.append(afectado_correo)
        
        # Solo agregar reporta_correo si existe y no es None
        if reporta_correo:
            destinatarios.append(reporta_correo)

        # Asegurar que haya destinatarios válidos
        if destinatarios:
            email_user = EmailMultiAlternatives(
                subject=subject_user,
                body=html_content_user,
                from_email=getattr(settings, "CORREO_AREA_VBG", settings.DEFAULT_FROM_EMAIL),
                to=destinatarios,
            )
            email_user.attach_alternative(html_content_user, "text/html")

            try:
                email_user.send(fail_silently=False)
                print(f"Correo enviado correctamente a: {', '.join(destinatarios)}")
            except Exception as e:
                print(f"Error al enviar correo a usuario(s): {e}")
        else:
            print("No se encontraron correos válidos en los datos proporcionados.")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def validar_case_id(request, case_id):
    existe = Queja.objects.filter(id=case_id).exists()
    return Response({"exists": existe}, status=status.HTTP_200_OK)

@api_view(['GET'])
@rol_required('admin', 'staff', 'developer')
def statistics(request):
    conteo_por_anio = {}
    conteo_por_mes = {}

    # Soporta fechas tipo 1/1/2024, 01/01/2024, etc.
    patron_fecha = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})')

    quejas = Queja.objects.all()

    for q in quejas:
        fecha_recepcion = q.persona_reporta.fecha_recepcion
        if fecha_recepcion:
            match = patron_fecha.match(fecha_recepcion.strip())
            if match:
                dia = int(match.group(1))
                mes = int(match.group(2))
                año = int(match.group(3))

                conteo_por_anio[año] = conteo_por_anio.get(año, 0) + 1
                conteo_por_mes[mes] = conteo_por_mes.get(mes, 0) + 1

    # Conteo por estamento del afectado
    estudiantes = Queja.objects.filter(persona_afectada__estamento__iexact='Estudiante').count()
    profesores = Queja.objects.filter(persona_afectada__estamento__iexact='Docente').count()
    funcionarios = Queja.objects.filter(persona_afectada__estamento__iexact='Funcionario').count()
    
    # Remitidos
    remitidosEstudiantes = Queja.objects.filter(
        persona_afectada__estamento__iexact='Estudiante', 
        estado__iexact='Remitido'
    ).count()
    remitidosProfesores = Queja.objects.filter(
        persona_afectada__estamento__iexact='Docente', 
        estado__iexact='Remitido'
    ).count()
    remitidosFuncionarios = Queja.objects.filter(
        persona_afectada__estamento__iexact='Funcionario', 
        estado__iexact='Remitido'
    ).count()

    # Conteo por facultades del afectado
    facultades = (
        Queja.objects
        .values('persona_afectada__facultad')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Conteo por sedes del afectado
    sedes = (
        Queja.objects
        .values('persona_afectada__sede')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Conteo por vicerrectoría adscrita del afectado
    vicerrectorias = (
        Queja.objects
        .values('persona_afectada__vicerrectoria_adscrito')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Conteo por identidad de género del afectado
    generos = (
        Queja.objects
        .values('persona_afectada__identidad_genero')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    edades = (
        Queja.objects
        .values('persona_afectada__edad')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    comunas = (
        Queja.objects
        .values('persona_afectada__comuna')  
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    conteoTipoVBG = Counter()

    for q in Queja.objects.values_list("persona_afectada__tipo_vbg_os", flat=True):
        if q:
            tipos = [t.strip().lower() for t in q.split(",") if t.strip()]
            conteoTipoVBG.update(tipos)

    conteoFactoresRiesgo = Counter()
    for q in Queja.objects.values_list("persona_acusada__factores_riesgo", flat=True):
        if q:
            tipos = [t.strip().lower() for t in q.split(",") if t.strip()]
            conteoFactoresRiesgo.update(tipos)

    # Tiempo promedio de respuesta a denuncias
    estados_finales = ['Atendida', 'Cerrada', 'Resuelta']
        
    total_tiempo = timedelta()
    contador = 0

    for queja in Queja.objects.all():
        fecha_recepcion_str = queja.persona_reporta.fecha_recepcion
        if not fecha_recepcion_str:
            continue

        try:
            # Intentar parsear diferentes formatos de fecha
            for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    fecha_recepcion = datetime.strptime(fecha_recepcion_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                continue
        except:
            continue

        primer_cambio = (
            CambioEstado.objects
            .filter(queja_id=queja, nuevo_estado__in=estados_finales)
            .order_by('fecha')
            .first()
        )

        if primer_cambio:
            diferencia = primer_cambio.fecha - fecha_recepcion.replace(tzinfo=primer_cambio.fecha.tzinfo)
            total_tiempo += diferencia
            contador += 1

    if contador == 0:
        contador = 1

    promedio = total_tiempo / contador

    avgResponseTime = {
        "tiempo_promedio_dias": promedio.days,
        "tiempo_promedio_horas": round(promedio.total_seconds() / 3600, 2),
        "detalle": str(promedio)
    }

    # Número de víctimas que reciben acompañamiento
    acompanamientos = HistorialQueja.objects.filter(tipo__in=['Psicológico', 'Jurídico'])

    victimas_psicologico = set()
    victimas_juridico = set()

    for hist in acompanamientos:
        if hist.tipo == 'Psicológico' and hist.queja_id and hist.queja_id.persona_afectada:
            victimas_psicologico.add(hist.queja_id.id)
        if hist.tipo == 'Jurídico' and hist.queja_id and hist.queja_id.persona_afectada:
            victimas_juridico.add(hist.queja_id.id)

    total_acompanamientos = {
        "total_victimas_psicologico": len(victimas_psicologico),
        "total_victimas_juridico": len(victimas_juridico),
        "total_victimas_ambos": len(victimas_psicologico.union(victimas_juridico))
    }

    # Tasa de reincidencia de agresores
    agresores = (
        Queja.objects
        .exclude(persona_acusada__nombre__isnull=True)
        .exclude(persona_acusada__nombre__exact="")
        .values('persona_acusada__nombre')
        .annotate(num_quejas=Count('id'))
    )

    total_agresores = agresores.count()
    agresores_reincidentes = agresores.filter(num_quejas__gt=1).count()

    tasa_reincidencia = 0
    if total_agresores > 0:
        tasa_reincidencia = (agresores_reincidentes / total_agresores) * 100

    tasa_reincidencia_data = {
        "total_agresores_unicos": total_agresores,
        "agresores_reincidentes": agresores_reincidentes,
        "tasa_reincidencia_porcentaje": round(tasa_reincidencia, 2),
    }    

    # Variación de denuncias resueltas
    variacion_denuncias_resueltas_mensual = variacion_denuncias_resueltas('mensual')
    variacion_denuncias_resueltas_semestral = variacion_denuncias_resueltas('semestral')
    variacion_denuncias_resueltas_anual = variacion_denuncias_resueltas('anual')

    return Response({
        'edades': list(edades),
        'comunas': list(comunas),
        'tipo_vbg': dict(conteoTipoVBG),
        'factores_riesgo': dict(conteoFactoresRiesgo),

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
        'tiempo_promedio_respuesta': avgResponseTime,
        'total_acompanamientos': total_acompanamientos,
        'tasa_reincidencia': tasa_reincidencia_data,
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

    # Convertir las fechas (usando el campo fecha_recepcion de PersonaReporta)
    quejas = Queja.objects.filter(estado__iexact="Resuelta").exclude(persona_reporta__fecha_recepcion__exact='')
    data = []
    
    for q in quejas:
        fecha_recepcion = q.persona_reporta.fecha_recepcion
        if fecha_recepcion:
            try:
                # Intentar diferentes formatos de fecha
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']:
                    try:
                        fecha = datetime.strptime(fecha_recepcion, fmt)
                        data.append({'fecha': fecha})
                        break
                    except ValueError:
                        continue
            except:
                continue

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

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class HistorialQuejaViewSet(viewsets.ModelViewSet):
    queryset = HistorialQueja.objects.all()
    serializer_class = HistorialQuejaSerializer

    def list(self, request, *args, **kwargs):
        # Bloqueamos la lista general
        return Response({"detail": "Método no permitido."}, status=405)

    @action(detail=False, methods=['get'], url_path='caso/(?P<caso_id>[^/.]+)')
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
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=False)
        try:
            serializer.save()
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

# Views para las nuevas entidades
class PersonaReportaViewSet(viewsets.ModelViewSet):
    queryset = PersonaReporta.objects.all()
    serializer_class = PersonaReportaSerializer
    permission_classes = [IsAuthenticated]

class PersonaAfectadaViewSet(viewsets.ModelViewSet):
    queryset = PersonaAfectada.objects.all()
    serializer_class = PersonaAfectadaSerializer
    permission_classes = [IsAuthenticated]

class PersonaAcusadaViewSet(viewsets.ModelViewSet):
    queryset = PersonaAcusada.objects.all()
    serializer_class = PersonaAcusadaSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_personas(request):
    """
    Búsqueda unificada de personas en todas las entidades
    """
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', 'todas')  # todas, reporta, afectada, acusada
    
    resultados = {
        'personas_reporta': [],
        'personas_afectadas': [],
        'personas_acusadas': []
    }
    
    if tipo in ['todas', 'reporta']:
        personas_reporta = PersonaReporta.objects.filter(
            Q(nombre__icontains=query) | 
            Q(correo__icontains=query) |
            Q(documento_identidad__icontains=query)
        )[:10]
        resultados['personas_reporta'] = PersonaReportaSerializer(personas_reporta, many=True).data
    
    if tipo in ['todas', 'afectada']:
        personas_afectadas = PersonaAfectada.objects.filter(
            Q(nombre__icontains=query) | 
            Q(correo__icontains=query) |
            Q(documento_identidad__icontains=query)
        )[:10]
        resultados['personas_afectadas'] = PersonaAfectadaSerializer(personas_afectadas, many=True).data
    
    if tipo in ['todas', 'acusada']:
        personas_acusadas = PersonaAcusada.objects.filter(
            Q(nombre__icontains=query) | 
            Q(documento_identidad__icontains=query)
        )[:10]
        resultados['personas_acusadas'] = PersonaAcusadaSerializer(personas_acusadas, many=True).data
    
    return Response(resultados)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@rol_required('admin', 'staff', 'developer')
def crear_queja_completa(request):
    """
    Endpoint alternativo para crear queja con datos separados
    """
    try:
        # Extraer datos de cada entidad
        persona_reporta_data = request.data.get('persona_reporta', {})
        persona_afectada_data = request.data.get('persona_afectada', {})
        persona_acusada_data = request.data.get('persona_acusada', {})
        queja_data = request.data.get('queja', {})
        
        # Validar datos requeridos
        if not persona_reporta_data.get('nombre') or not persona_afectada_data.get('nombre'):
            return Response(
                {"error": "Nombre de persona reporta y afectada son requeridos"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear las entidades
        persona_reporta = PersonaReporta.objects.create(**persona_reporta_data)
        persona_afectada = PersonaAfectada.objects.create(**persona_afectada_data)
        persona_acusada = PersonaAcusada.objects.create(**persona_acusada_data)
        
        # Crear la queja
        queja = Queja.objects.create(
            persona_reporta=persona_reporta,
            persona_afectada=persona_afectada,
            persona_acusada=persona_acusada,
            estado='Pendiente',
            **queja_data
        )
        
        serializer = QuejaSerializer(queja)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": f"Error al crear queja: {str(e)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_avanzadas(request):
    """
    Estadísticas avanzadas usando las nuevas relaciones
    """
    user = request.user
    if user.rol not in ['admin', 'staff', 'developer']:
        raise PermissionDenied("No tienes permiso para acceder a estas estadísticas")
    
    # Conteo por tipo de discapacidad
    discapacidades_afectados = (
        Queja.objects
        .values('persona_afectada__tipo_discapacidad')
        .annotate(total=Count('id'))
        .exclude(persona_afectada__tipo_discapacidad__exact='')
        .order_by('-total')
    )
    
    discapacidades_acusados = (
        Queja.objects
        .values('persona_acusada__tipo_discapacidad')
        .annotate(total=Count('id'))
        .exclude(persona_acusada__tipo_discapacidad__exact='')
        .order_by('-total')
    )
    
    # Conteo por condición étnico-racial
    etnias_afectados = (
        Queja.objects
        .values('persona_afectada__condicion_etnico_racial')
        .annotate(total=Count('id'))
        .exclude(persona_afectada__condicion_etnico_racial__exact='')
        .order_by('-total')
    )
    
    etnias_acusados = (
        Queja.objects
        .values('persona_acusada__condicion_etnico_racial')
        .annotate(total=Count('id'))
        .exclude(persona_acusada__condicion_etnico_racial__exact='')
        .order_by('-total')
    )
    
    # Distribución por edad
    distribucion_edad_afectados = (
        Queja.objects
        .values('persona_afectada__edad')
        .annotate(total=Count('id'))
        .exclude(persona_afectada__edad__exact='')
        .order_by('persona_afectada__edad')
    )
    
    distribucion_edad_acusados = (
        Queja.objects
        .values('persona_acusada__edad')
        .annotate(total=Count('id'))
        .exclude(persona_acusada__edad__exact='')
        .order_by('persona_acusada__edad')
    )
    
    # Tipos de acompañamiento solicitados
    acompanamiento_ruta = Queja.objects.filter(desea_activar_ruta_atencion_integral='Sí').count()
    acompanamiento_sociopedagogico = Queja.objects.filter(recibir_asesoria_orientacion_sociopedagogica='Sí').count()
    acompanamiento_psicologico = Queja.objects.filter(orientacion_psicologica='Sí').count()
    acompanamiento_juridico = Queja.objects.filter(asistencia_juridica='Sí').count()
    
    return Response({
        'discapacidades_afectados': list(discapacidades_afectados),
        'discapacidades_acusados': list(discapacidades_acusados),
        'etnias_afectados': list(etnias_afectados),
        'etnias_acusados': list(etnias_acusados),
        'distribucion_edad_afectados': list(distribucion_edad_afectados),
        'distribucion_edad_acusados': list(distribucion_edad_acusados),
        'acompanamientos_solicitados': {
            'ruta_atencion_integral': acompanamiento_ruta,
            'sociopedagogico': acompanamiento_sociopedagogico,
            'psicologico': acompanamiento_psicologico,
            'juridico': acompanamiento_juridico
        }
    })