from django.db import models
from login.models import Usuarios
from django.conf import settings
from django.core.exceptions import ValidationError

class PersonaReporta(models.Model):
    fecha_recepcion = models.CharField(max_length=30, blank=True)
    nombre = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=30, blank=True)
    edad = models.CharField(max_length=30, blank=True)
    estamento = models.CharField(max_length=30, blank=True)
    vicerrectoria_adscrito = models.CharField(max_length=52, blank=True)
    dependencia = models.CharField(max_length=30, blank=True)
    programa_academico = models.CharField(max_length=30, blank=True)
    facultad = models.CharField(max_length=30, blank=True)
    sede = models.CharField(max_length=30, blank=True)
    celular = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, str) and value.strip() == "":
                setattr(self, field.name, "N/A")
        super().save(*args, **kwargs)

    def __str__(self):
        nombre_afectado = self.persona_afectada.nombre if self.persona_afectada else "Sin afectado"
        return f"{self.nombre} - {self.correo}"

class PersonaAfectada(models.Model):
    nombre = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=30, blank=True)
    edad = models.CharField(max_length=30, blank=True)
    tipo_documento_identidad = models.CharField(max_length=30, blank=True)
    documento_identidad = models.CharField(max_length=30, blank=True)
    redes_apoyo = models.TextField(blank=True)
    codigo = models.CharField(max_length=30, blank=True)
    semestre = models.IntegerField(blank=True, null=True)  
    comuna = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    barrio = models.CharField(max_length=50, blank=True)
    ciudad_origen = models.CharField(max_length=50, blank=True, null=True)
    estrato_socioeconomico = models.CharField(max_length=3, blank=True)
    condicion_etnico_racial = models.CharField(max_length=40, blank=True)
    tiene_discapacidad = models.CharField(max_length=3, blank=True)
    tipo_discapacidad = models.CharField(max_length=40, blank=True)
    identidad_genero = models.CharField(max_length=60, blank=True)
    orientacion_sexual = models.CharField(max_length=60, blank=True)
    estamento = models.CharField(max_length=100, blank=True)
    vicerrectoria_adscrito = models.CharField(max_length=100, blank=True)
    dependencia = models.CharField(max_length=40, blank=True)
    programa_academico = models.CharField(max_length=200, blank=True)
    facultad = models.CharField(max_length=100, blank=True)
    sede = models.CharField(max_length=50, blank=True)
    celular = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    tipo_vbg_os = models.TextField(blank=True)
    detalles_caso = models.TextField(blank=True)
    ha_hecho_denuncia = models.CharField(max_length=3, blank=True)
    denuncias_previas = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, str) and value.strip() == "":
                setattr(self, field.name, "N/A")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.correo}"

class PersonaAcusada(models.Model):
    nombre = models.CharField(max_length=30, blank=True)
    sexo = models.CharField(max_length=30, blank=True)
    edad = models.CharField(max_length=30, blank=True)
    semestre = models.IntegerField(blank=True, null=True)
    barrio = models.CharField(max_length=30, blank=True)
    ciudad_origen = models.CharField(max_length=30, blank=True, null=True)
    condicion_etnico_racial = models.CharField(max_length=30, blank=True)
    tiene_discapacidad = models.CharField(max_length=30, blank=True)
    tipo_discapacidad = models.CharField(max_length=30, blank=True)
    identidad_genero = models.CharField(max_length=30, blank=True)
    orientacion_sexual = models.CharField(max_length=30, blank=True)
    estamento = models.CharField(max_length=30, blank=True)
    vicerrectoria_adscrito = models.CharField(max_length=52, blank=True)
    dependencia = models.CharField(max_length=30, blank=True)
    programa_academico = models.CharField(max_length=30, blank=True)
    facultad = models.CharField(max_length=30, blank=True)
    sede = models.CharField(max_length=30, blank=True)
    factores_riesgo = models.TextField(blank=True, null=True)
    tiene_denuncias = models.CharField(max_length=3, blank=True)
    detalles_denuncias = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, str) and value.strip() == "":
                setattr(self, field.name, "N/A")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre}"

class Queja(models.Model):
    tipo_de_acompanamiento = models.CharField(max_length=30, blank=True)
    estado = models.CharField(max_length=30, blank=True, default='Recepción')
    unidad = models.CharField(max_length=100, null=True, blank=True)
    prioridad = models.CharField(max_length=30, blank=True, default='Pendiente')
    
    # Relaciones con las nuevas entidades
    persona_reporta = models.ForeignKey(PersonaReporta, on_delete=models.CASCADE, related_name='quejas_reportadas')
    persona_afectada = models.ForeignKey(PersonaAfectada, on_delete=models.CASCADE, related_name='quejas_afectadas', null=True, blank=True)
    persona_acusada = models.ForeignKey(PersonaAcusada, on_delete=models.CASCADE, related_name='quejas_acusadas', null=True, blank=True)
    
    # Datos adicionales para el asesoramiento
    desea_activar_ruta_atencion_integral = models.CharField(max_length=3, blank=True)
    recibir_asesoria_orientacion_sociopedagogica = models.CharField(max_length=3, blank=True)
    orientacion_psicologica = models.CharField(max_length=3, blank=True)
    asistencia_juridica = models.CharField(max_length=3, blank=True)
    acompañamiento_solicitud_medidas_proteccion_inicial = models.CharField(max_length=3, blank=True)
    acompañamiento_ante_instancias_gubernamentales = models.CharField(max_length=3, blank=True)
    
    #interponer_queja_al_comite_asusntos_internos_disciplinarios = models.CharField(max_length=3, blank=True)
    
    interponer_queja_al_cade = models.CharField(max_length=3, blank=True)
    interponer_queja_oficina_control_interno = models.CharField(max_length=3, blank=True)
    interponer_queja_a_rectoria=models.CharField(max_length=3, blank=True)
    
    observaciones = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, str) and value.strip() == "":
                setattr(self, field.name, "N/A")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Queja {self.id} - {self.persona_afectada.nombre} - {self.estado}"

class HistorialQueja(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    queja_id = models.ForeignKey(Queja, related_name='historial_estados', on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=80, blank=True)
    numero = models.IntegerField(editable=False, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        TIPO_LIMITADO = "Apoyo psicológico"
        MAXIMO = 3

        if self.tipo == TIPO_LIMITADO:
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
        
        if self.numero is None:
            ultimo = HistorialQueja.objects.filter(queja_id=self.queja_id).order_by("-numero").first()
            if ultimo and ultimo.numero:
                self.numero = ultimo.numero + 1
            else:
                self.numero = 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"ID: {self.id} - Fecha: {self.fecha}"

class CambioEstado(models.Model):
    queja_id = models.ForeignKey(Queja, related_name='cambios_estado', on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado_anterior = models.CharField(max_length=30, blank=False)
    nuevo_estado = models.CharField(max_length=30, blank=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"De {self.estado_anterior} a {self.nuevo_estado}"