from django.db import models
from login.models import Usuarios
from django.conf import settings
from django.core.exceptions import ValidationError


class Queja(models.Model):
    
    
    tipo_de_acompanamiento = models.CharField(max_length=30, blank=True)
    estado = models.CharField(max_length=30, blank=True, default='Recepción')
    unidad = models.CharField(max_length=100, null=True, blank=True)
    prioridad = models.CharField(max_length=30, blank=True, default='Pendiente')

    ##Datos de la persona que Reporta
    fecha_recepcion= models.CharField(max_length=30, blank=True)
    reporta_nombre= models.CharField(max_length=30, blank=True)
    reporta_Sexo= models.CharField(max_length=30, blank=True)
    reporta_edad= models.CharField(max_length=30, blank=True)
    reporta_estamento= models.CharField(max_length=30, blank=True)
    reporta_vicerrectoria_adscrito= models.CharField(max_length=52, blank=True)
    reporta_dependencia= models.CharField(max_length=30, blank=True)
    reporta_programa_academico= models.CharField(max_length=30, blank=True)
    reporta_facultad= models.CharField(max_length=30, blank=True)
    reporta_sede= models.CharField(max_length=30, blank=True)
    reporta_celular= models.CharField(max_length=30, blank=True)
    reporta_correo= models.EmailField( blank=True)
    #Datos de la persona afectada
    afectado_nombre= models.CharField(max_length=30, blank=True)
    afectado_sexo= models.CharField(max_length=30, blank=True)
    afectado_edad= models.CharField(max_length=30, blank=True)
    afectado_tipo_documento_identidad= models.CharField(max_length=30, blank=True)
    afectado_documento_identidad= models.CharField(max_length=30, blank=True)
    afectado_redes_apoyo= models.TextField( blank=True)
    afectado_codigo = models.CharField(max_length=30, blank=True)
    afectado_semestre= models.IntegerField(blank=True,null=True)  
    afectado_comuna= models.CharField(max_length=30, blank=True)
    afectado_direccion= models.CharField(max_length=100, blank=True,null=True)
    afectado_barrio= models.CharField(max_length=30, blank=True)
    afectado_ciudad_origen= models.CharField(max_length=30, blank=True,null=True)
    afectado_estrato_socioeconomico= models.CharField(max_length=30, blank=True)
    afectado_condicion_etnico_racial= models.CharField(max_length=30, blank=True)
    afectado_tiene_discapacidad= models.CharField(max_length=30, blank=True)
    afectado_tipo_discapacidad= models.CharField(max_length=30, blank=True)
    afectado_identidad_genero= models.CharField(max_length=30, blank=True)
    afectado_orientacion_sexual= models.CharField(max_length=30, blank=True)
    afectado_estamento= models.CharField(max_length=30, blank=True)
    afectado_vicerrectoria_adscrito= models.CharField(max_length=52, blank=True)
    afectado_dependencia= models.CharField(max_length=30, blank=True)
    afectado_programa_academico= models.CharField(max_length=30, blank=True)
    afectado_facultad= models.CharField(max_length=30, blank=True)
    afectado_sede= models.CharField(max_length=30, blank=True)
    afectado_celular= models.CharField(max_length=30, blank=True)
    afectado_correo= models.EmailField(blank=True)
    afectado_tipo_vbg_os= models.TextField( blank=True)
    afectado_detalles_caso= models.TextField( blank=True)
    afectado_ha_hecho_denuncia= models.CharField(max_length=3, blank=True)
    afectado_denuncias_previas= models.TextField(null=True, blank=True)
    #datos de la persona agresora
    agresor_nombre= models.CharField(max_length=30, blank=True)
    agresor_sexo= models.CharField(max_length=30, blank=True)
    agresor_edad= models.CharField(max_length=30, blank=True)
    agresor_semestre= models.IntegerField(blank=True, null=True)
    agresor_barrio= models.CharField(max_length=30, blank=True)
    agresor_ciudad_origen= models.CharField(max_length=30, blank=True,null=True)
    agresor_condicion_etnico_racial= models.CharField(max_length=30, blank=True)
    agresor_tiene_discapacidad= models.CharField(max_length=30, blank=True)
    agresor_tipo_discapacidad= models.CharField(max_length=30, blank=True)
    agresor_identidad_genero= models.CharField(max_length=30, blank=True)
    agresor_orientacion_sexual= models.CharField(max_length=30, blank=True)
    agresor_estamento= models.CharField(max_length=30, blank=True)
    agresor_vicerrectoria_adscrito= models.CharField(max_length=52, blank=True)
    agresor_dependencia= models.CharField(max_length=30, blank=True)
    agresor_programa_academico= models.CharField(max_length=30, blank=True)
    agresor_facultad= models.CharField(max_length=30, blank=True)
    agresor_sede= models.CharField(max_length=30, blank=True)
    agresor_factores_riesgo= models.TextField( blank=True,null=True)
    agresor_tiene_denuncias= models.CharField(max_length=3, blank=True)
    agresor_detalles_denuncias= models.TextField( blank=True,null=True)
    #Datos adicionales para el asesoramiento
    desea_activar_ruta_atencion_integral= models.CharField(max_length=3, blank=True)
    recibir_asesoria_orientacion_sociopedagogica= models.CharField(max_length=3, blank=True)
    orientacion_psicologica= models.CharField(max_length=3, blank=True)
    asistencia_juridica= models.CharField(max_length=3, blank=True)
    acompañamiento_solicitud_medidas_proteccion_inicial= models.CharField(max_length=3, blank=True)
    acompañamiento_ante_instancias_gubernamentales= models.CharField(max_length=3, blank=True)
    interponer_queja_al_comite_asusntos_internos_disciplinarios= models.CharField(max_length=3, blank=True)
    observaciones= models.TextField(blank=True)
    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            value = getattr(self, field.name)
            # Solo reemplaza si es cadena vacía
            if isinstance(value, str) and value.strip() == "":
                setattr(self, field.name, "N/A")
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.nombre} - {self.sede} - {self.estado}"
   
class HistorialQueja(models.Model):
    fecha= models.DateTimeField(auto_now_add=True)
    queja_id = models.ForeignKey(Queja, related_name='historial_estados', on_delete=models.SET_NULL,null=True)
    descripcion= models.TextField(blank=True)
    tipo= models.CharField(max_length=80, blank=True)
    numero= models.IntegerField(editable=False, null=True, blank=True)
    def save(self, *args, **kwargs):
        TIPO_LIMITADO = "Apoyo psicológico"  # reemplaza con tu tipo
        MAXIMO = 3

        if self.tipo == TIPO_LIMITADO:
            # Excluye este registro si ya existe (para edición)
            queryset = HistorialQueja.objects.filter(
                queja_id=self.queja_id,
                tipo=TIPO_LIMITADO
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            if queryset.count() >= MAXIMO:
                raise ValidationError(
                    f"No se pueden tener más de {MAXIMO} registros del tipo '{TIPO_LIMITADO}' para esta queja."
                )
        if self.numero is None:  # solo al crear
            ultimo = HistorialQueja.objects.filter(queja_id=self.queja_id).order_by("-numero").first()
            if ultimo and ultimo.numero:
                self.numero = ultimo.numero + 1
            else:
                self.numero = 1
        super().save(*args, **kwargs)
    def __str__(self):
        return f"ID: {self.id} - Fecha: {self.fecha}"
    
class CambioEstado(models.Model):
    queja_id = models.ForeignKey(Queja, related_name='cambios_estado', on_delete=models.SET_NULL,null=True)
    fecha= models.DateTimeField(auto_now_add=True)
    estado_anterior= models.CharField(max_length=30, blank=False)
    nuevo_estado= models.CharField(max_length=30, blank=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return f"De {self.estado_anterior} a {self.nuevo_estado}"