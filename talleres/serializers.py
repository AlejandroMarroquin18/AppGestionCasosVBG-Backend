from rest_framework import serializers
from .models import Workshop, Facilitator
from participantes.models import Participant

class FacilitatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facilitator
        fields = ['id', 'name']

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            'id', 'full_name', 'email', 'document_type', 'document_number', 
            'age', 'disability', 'program', 'gender_identity', 
            'self_recognition', 'institutional_email', 'terms_accepted', 'created_at'
        ]

class WorkshopSerializer(serializers.ModelSerializer):
    facilitators = FacilitatorSerializer(many=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    qr_imagen = serializers.CharField(read_only=True)
    qr_link = serializers.CharField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workshop
        fields = [
            'id', 'name', 'date', 'start_time', 'end_time', 'details', 
            'location', 'modality', 'slots', 'available_slots', 'facilitators', 
            'participants', 'qr_imagen', 'qr_link'
        ]

    def create(self, validated_data):
        facilitators_data = validated_data.pop('facilitators', [])
        
        # Crea el taller (esto activará el save() que genera el QR automáticamente)
        workshop = Workshop.objects.create(**validated_data)
        
        # Maneja los facilitadores de forma segura
        for facilitator_data in facilitators_data:
            # Buscar si ya existe un facilitador con ese nombre
            existing_facilitators = Facilitator.objects.filter(name=facilitator_data['name'])
            
            if existing_facilitators.exists():
                # Si hay múltiples, tomar el primero
                facilitator = existing_facilitators.first()
            else:
                # Si no existe, crear uno nuevo
                facilitator = Facilitator.objects.create(**facilitator_data)
            
            workshop.facilitators.add(facilitator)
            
        return workshop

    def update(self, instance, validated_data):
        facilitators_data = validated_data.pop('facilitators', None)

        # Actualiza los campos del taller
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualiza los facilitadores
        if facilitators_data is not None:
            instance.facilitators.clear()
            for facilitator_data in facilitators_data:
                # Buscar si ya existe un facilitador con ese nombre
                existing_facilitators = Facilitator.objects.filter(name=facilitator_data['name'])
                
                if existing_facilitators.exists():
                    facilitator = existing_facilitators.first()
                else:
                    facilitator = Facilitator.objects.create(**facilitator_data)
                
                instance.facilitators.add(facilitator)

        return instance