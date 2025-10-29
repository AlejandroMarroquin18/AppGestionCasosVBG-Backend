from rest_framework import serializers
from .models import Queja, HistorialQueja, CambioEstado, PersonaReporta, PersonaAfectada, PersonaAcusada

class PersonaReportaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaReporta
        fields = '__all__'

class PersonaAfectadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaAfectada
        fields = '__all__'

class PersonaAcusadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaAcusada
        fields = '__all__'

class QuejaSerializer(serializers.ModelSerializer):
    persona_reporta = PersonaReportaSerializer()
    persona_afectada = PersonaAfectadaSerializer(required=False, allow_null=True)
    persona_acusada = PersonaAcusadaSerializer(required=False, allow_null=True)

    class Meta:
        model = Queja
        fields = '__all__'

    def create(self, validated_data):
        # Extraer datos de las relaciones
        persona_reporta_data = validated_data.pop('persona_reporta')
        persona_afectada_data = validated_data.pop('persona_afectada', None)
        persona_acusada_data = validated_data.pop('persona_acusada', None)
        
        # Crear persona_reporta (obligatoria)
        persona_reporta = PersonaReporta.objects.create(**persona_reporta_data)
        
        # Crear persona_afectada solo si existe data y no es None
        persona_afectada = None
        if persona_afectada_data is not None:  # Verificar explícitamente que no sea None
            persona_afectada = PersonaAfectada.objects.create(**persona_afectada_data)
        
        # Crear persona_acusada solo si existe data y no es None
        persona_acusada = None
        if persona_acusada_data is not None:  # Verificar explícitamente que no sea None
            persona_acusada = PersonaAcusada.objects.create(**persona_acusada_data)
        
        # Crear la queja con las relaciones
        queja = Queja.objects.create(
            persona_reporta=persona_reporta,
            persona_afectada=persona_afectada,  # Puede ser None
            persona_acusada=persona_acusada,    # Puede ser None
            **validated_data
        )
        
        return queja

    def update(self, instance, validated_data):
        # Manejar actualización de relaciones anidadas
        persona_reporta_data = validated_data.pop('persona_reporta', None)
        persona_afectada_data = validated_data.pop('persona_afectada', None)
        persona_acusada_data = validated_data.pop('persona_acusada', None)
        
        # Actualizar la queja principal
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar las entidades relacionadas si se proporcionan
        if persona_reporta_data:
            for attr, value in persona_reporta_data.items():
                setattr(instance.persona_reporta, attr, value)
            instance.persona_reporta.save()
            
        if persona_afectada_data and instance.persona_afectada:
            for attr, value in persona_afectada_data.items():
                setattr(instance.persona_afectada, attr, value)
            instance.persona_afectada.save()
            
        if persona_acusada_data and instance.persona_acusada:
            for attr, value in persona_acusada_data.items():
                setattr(instance.persona_acusada, attr, value)
            instance.persona_acusada.save()
        
        return instance

class HistorialQuejaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialQueja
        fields = '__all__'

class CambioEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CambioEstado
        fields = '__all__'