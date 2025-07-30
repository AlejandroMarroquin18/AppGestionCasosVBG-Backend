from django.db import models

class Queja(models.Model):
    

    
    tipo_de_acompanamiento = models.CharField(max_length=30, blank=True)
    estado = models.CharField(max_length=30, blank=True)
    unidad = models.CharField(max_length=100, null=True, blank=True)





    ##Datos de la persona que Reporta
    fecha_recepcion= models.CharField(max_length=30, blank=True)
    reporta_nombre= models.CharField(max_length=30, blank=True)
    reporta_Sexo= models.CharField(max_length=30, blank=True)
    reporta_edad= models.CharField(max_length=30, blank=True)
    reporta_estamento= models.CharField(max_length=30, blank=True)
    reporta_vicerrectoria_adscrito= models.CharField(max_length=30, blank=True)
    reporta_dependencia= models.CharField(max_length=30, blank=True)
    reporta_programa_academico= models.CharField(max_length=30, blank=True)
    reporta_facultad= models.CharField(max_length=30, blank=True)
    reporta_sede= models.CharField(max_length=30, blank=True)
    reporta_celular= models.CharField(max_length=30, blank=True)
    reporta_correo= models.CharField(max_length=30, blank=True)
    #Datos de la persona afectada
    afectado_nombre= models.CharField(max_length=30, blank=True)
    afectado_sexo= models.CharField(max_length=30, blank=True)
    afectado_edad= models.CharField(max_length=30, blank=True)
    afectado_codigo = models.CharField(max_length=30, blank=True)
    afectado_comuna= models.CharField(max_length=30, blank=True)
    afectado_estrato_socioeconomico= models.CharField(max_length=30, blank=True)
    afectado_condicion_etnico_racial= models.CharField(max_length=30, blank=True)
    afectado_tiene_discapacidad= models.CharField(max_length=30, blank=True)
    afectado_tipo_discapacidad= models.CharField(max_length=30, blank=True)
    afectado_identidad_genero= models.CharField(max_length=30, blank=True)
    afectado_orientacion_sexual= models.CharField(max_length=30, blank=True)
    afectado_estamento= models.CharField(max_length=30, blank=True)
    afectado_vicerrectoria_adscrito= models.CharField(max_length=30, blank=True)
    afectado_dependencia= models.CharField(max_length=30, blank=True)
    afectado_programa_academico= models.CharField(max_length=30, blank=True)
    afectado_facultad= models.CharField(max_length=30, blank=True)
    afectado_sede= models.CharField(max_length=30, blank=True)
    afectado_celular= models.CharField(max_length=30, blank=True)
    afectado_correo= models.CharField(max_length=30, blank=True)
    afectado_tipo_vbg_os= models.CharField(max_length=30, blank=True)
    afectado_detalles_caso= models.CharField(max_length=30, blank=True)
    #datos de la persona agresora
    agresor_nombre= models.CharField(max_length=30, blank=True)
    agresor_sexo= models.CharField(max_length=30, blank=True)
    agresor_edad= models.CharField(max_length=30, blank=True)
    agresor_condicion_etnico_racial= models.CharField(max_length=30, blank=True)
    agresor_tiene_discapacidad= models.CharField(max_length=30, blank=True)
    agresor_tipo_discapacidad= models.CharField(max_length=30, blank=True)
    agresor_identidad_genero= models.CharField(max_length=30, blank=True)
    agresor_orientacion_sexual= models.CharField(max_length=30, blank=True)
    agresor_estamento= models.CharField(max_length=30, blank=True)
    agresor_vicerrectoria_adscrito= models.CharField(max_length=30, blank=True)
    agresor_dependencia= models.CharField(max_length=30, blank=True)
    agresor_programa_academico= models.CharField(max_length=30, blank=True)
    agresor_facultad= models.CharField(max_length=30, blank=True)
    agresor_sede= models.CharField(max_length=30, blank=True)
    #Datos adicionales para el asesoramiento
    desea_activar_ruta_atencion_integral= models.CharField(max_length=30, blank=True)
    recibir_asesoria_orientacion_sociopedagogica= models.CharField(max_length=30, blank=True)
    orientacion_psicologica= models.CharField(max_length=30, blank=True)
    asistencia_juridica= models.CharField(max_length=30, blank=True)
    acompañamiento_solicitud_medidas_proteccion_inicial= models.CharField(max_length=30, blank=True)
    acompañamiento_ante_instancias_gubernamentales= models.CharField(max_length=30, blank=True)
    interponer_queja_al_comite_asusntos_internos_disciplinarios= models.CharField(max_length=30, blank=True)
    observaciones= models.CharField(max_length=700,default='hola')


    def __str__(self):
        return f"{self.nombre} - {self.sede} - {self.estado}"