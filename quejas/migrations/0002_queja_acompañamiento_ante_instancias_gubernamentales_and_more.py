# Generated by Django 5.1.3 on 2025-01-31 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quejas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='queja',
            name='acompañamiento_ante_instancias_gubernamentales',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='acompañamiento_solicitud_medidas_proteccion_inicial',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_celular',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_comuna',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_condicion_etnico_racial',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_correo',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_dependencia',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_detalles_caso',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_edad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_estamento',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_estrato_socioeconomico',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_facultad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_identidad_genero',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_nombre',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_orientacion_sexual',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_programa_academico',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_sede',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_sexo',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_tiene_discapacidad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_tipo_discapacidad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_tipo_vbg_os',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='afectado_vicerrectoria_adscrito',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_condicion_etnico_racial',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_dependencia',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_edad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_estamento',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_facultad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_identidad_genero',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_nombre',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_orientacion_sexual',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_programa_academico',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_sede',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_sexo',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_tiene_discapacidad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_tipo_discapacidad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='agresor_vicerrectoria_adscrito',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='asistencia_juridica',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='desea_activar_ruta_atencion_integral',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='fecha_recepcion',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='interponer_queja_al_comite_asusntos_internos_disciplinarios',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='observaciones',
            field=models.CharField(default='hola', max_length=500),
        ),
        migrations.AddField(
            model_name='queja',
            name='orientacion_psicologica',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='recibir_asesoria_orientacion_sociopedagogica',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_Sexo',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_celular',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_correo',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_dependencia',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_edad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_estamento',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_facultad',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_nombre',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_programa_academico',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_sede',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='queja',
            name='reporta_vicerrectoria_adscrito',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
