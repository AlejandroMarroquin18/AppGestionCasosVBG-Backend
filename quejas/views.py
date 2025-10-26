# quejas/views.py
import re
from django.http import JsonResponse
from .serializers import QuejaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from datetime import datetime
from rest_framework import viewsets, permissions
from .serializers import QuejaSerializer
from datetime import timedelta
from .models import Queja, CambioEstado, HistorialQueja
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from django.core.mail import EmailMultiAlternatives
from appvbgbackend import settings
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from utils.decorators import rol_required
from collections import Counter




import pandas as pd



@api_view(['GET'])
@rol_required('admin', 'staff', 'developer')
def lista_quejas(request):
    print("jsjsjsj")
    if request.method == 'GET':
        quejas = Queja.objects.all()
        serializer = QuejaSerializer(quejas, many=True)
        return Response(serializer.data)
    


class QuejaViewSet(viewsets.ModelViewSet):
    queryset = Queja.objects.all()  # Recupera todas las quejas
    serializer_class = QuejaSerializer  # Usa el serializer para validar datos
    def get_queryset(self):

        user = self.request.user
        print("user making request:", user)
        if not user:
            return Queja.objects.none()  # Si no hay usuario, no devolver nada
        

        queryset = Queja.objects.all()

        # Si el usuario es "visitor", solo puede ver sus propias quejas
        print("user role:", user.rol)
        if user.rol == "visitor":
            queryset = queryset.filter(
                Q(afectado_correo=user) | Q(reporta_correo=user.email)
            )

        query_params = self.request.query_params

        # Recorrer todos los parámetros y aplicarlos como filtros dinámicos
        filters = {}
        for param, value in query_params.items():
            if param in [f.name for f in Queja._meta.fields]:  # Verificar si el campo existe en el modelo
                filters[param] = value
        
        return queryset.filter(**filters)
    
    def perform_update(self, serializer):
        instance = self.get_object()
        user= self.request.user
        if user.rol == "visitor":
            raise PermissionDenied("No tienes permiso para modificar esta queja.")

        instance._user = self.request.user  # 👈 pasa el usuario a la señal
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        # Evitar que un visitor borre quejas que no le pertenecen
        if user.rol == "visitor":
            
            raise PermissionDenied("No tienes permiso para eliminar esta queja.")

        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        # Evitar que un visitor consulte una queja que no le pertenece
        if user.rol == "visitor":
            if instance.afectado_correo != user.email and instance.reporta_correo != user.email:
                raise PermissionDenied("No tienes permiso para ver esta queja.")

        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        # Si la acción es 'create' (POST), permitir acceso sin autenticación
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


    ####Essto se añade para que al crear una queja, el estado se establezca en 'pendiente' por defecto, ye
    def create(self, request, *args, **kwargs):
         # Copia mutable de los datos recibidos
        data = request.data.copy()
        
        # Modificar el campo que necesitas antes de validar
        data['estado'] = 'Pendiente'  

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Enviar correo de notificación
        subject = "Nueva Queja Registrada"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color:#444;">📢 Nueva queja registrada</h2>

            <p>Se ha registrado una nueva queja en la plataforma.</p>

            <p><strong>Detalles de la queja:</strong></p>
            <ul>
                <li><strong>ID:</strong> {serializer.data['id']}</li>
                <li><strong>Fecha de recepción:</strong> {serializer.data['fecha_recepcion']}</li>
                <li><strong>Estado actual:</strong> {serializer.data['estado']}</li>
                <li><strong>Registrada por:</strong> {serializer.data['reporta_nombre']}</li>
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
            to=[settings.CORREO_AREA_VBG],  # Cambia esto por el correo del área de VBG
        )
        email.attach_alternative(html_content, "text/html")

        try:
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Error al enviar correo: {e}")
        #send_mail(asunto, mensaje,remitente,destinatario)

        # Enviar correo de notificación al afectado y al reportante (si aplica)
        subject = "Confirmación de registro de queja"

        # Construcción del contenido del correo
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color:#444;">📢 Su queja ha sido registrada exitosamente</h2>

            <p>Su queja ha sido recibida por la plataforma y será atendida por el equipo correspondiente.</p>

            <p><strong>Detalles de la queja registrada:</strong></p>
            <ul>
                <li><strong>ID:</strong> {serializer.data['id']}</li>
                <li><strong>Fecha de recepción:</strong> {data.get('fecha_recepcion', 'No especificada')}</li>
                <li><strong>Estado actual:</strong> {data.get('estado', 'No especificado')}</li>
                <li><strong>Registrada por:</strong> {data.get('reporta_nombre', 'No especificado')}</li>
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

        afectado_correo = data.get('afectado_correo')
        reporta_correo = data.get('reporta_correo')

        if afectado_correo:
            destinatarios.append(afectado_correo)
        if reporta_correo:
            destinatarios.append(reporta_correo)

        # Asegurar que haya destinatarios válidos
        if destinatarios:
            email = EmailMultiAlternatives(
                subject=subject,
                body=html_content,
                from_email=getattr(settings, "CORREO_AREA_VBG", settings.DEFAULT_FROM_EMAIL),
                to=destinatarios,  # Se envía a ambos si existen
            )
            email.attach_alternative(html_content, "text/html")

            try:
                email.send(fail_silently=False)
                print(f"Correo enviado correctamente a: {', '.join(destinatarios)}")
            except Exception as e:
                print(f"Error al enviar correo a usuario(s): {e}")
        else:
            print("No se encontraron correos en afectado_correo o reporta_correo.")

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

    edades = (
        Queja.objects
        .values('afectado_edad')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    comunas = (
        Queja.objects
        .values('afectado_comuna')  
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    conteoTipoVBG = Counter()

    for q in Queja.objects.values_list("afectado_tipo_vbg_os", flat=True):
        if q:
            tipos = [t.strip().lower() for t in q.split(",") if t.strip()]
            conteoTipoVBG.update(tipos)

    '''tipo_vbg = (
        Queja.objects
        .values('afectado_tipo_vbg_os')  
        .annotate(total=Count('id'))
        .order_by('-total')
    )'''

    conteoFactoresRiesgo = Counter()
    for q in Queja.objects.values_list("agresor_factores_riesgo", flat=True):
        if q:
            tipos = [t.strip().lower() for t in q.split(",") if t.strip()]
            conteoFactoresRiesgo.update(tipos)

    '''factores_riesgo = (
        Queja.objects
        .values('agresor_factores_riesgo')
        .annotate(total=Count('id'))
        .order_by('-total')
    )'''



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
    print (dict(conteoTipoVBG))
    print (dict(conteoFactoresRiesgo))

    '''
    Vicerrectoría Académica
    Vicerrectoría Administrativa
    Vicerrectoría de Bienestar Universitario
    Vicerrectoría de Investigaciones
    Vicerrectoría de Regionalización
    Vicerrectoría de Extensión y Proyección Social '''
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