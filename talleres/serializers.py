from rest_framework import serializers
from .models import Workshop, Facilitator
from participantes.models import Participant  # Importa el modelo Participant

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
            'self_recognition', 'institutional_email', 'terms_accepted'
        ]

class WorkshopSerializer(serializers.ModelSerializer):
    facilitators = FacilitatorSerializer(many=True)  # Lista de facilitadores
    participants = ParticipantSerializer(many=True)  # Lista de participantes

    class Meta:
        model = Workshop
        fields = [
            'id', 'name', 'date', 'start_time', 'end_time', 'details', 
            'location', 'modality', 'slots', 'facilitators', 'participants', 'qr_code_url'
        ]

    def create(self, validated_data):
        facilitators_data = validated_data.pop('facilitators', [])  # Extrae los facilitadores
        participants_data = validated_data.pop('participants', [])  # Extrae los participantes

        # Crea el taller
        workshop = Workshop.objects.create(**validated_data)
        workshop.generate_qr_code() 

        # Crea los facilitadores y los asocia al taller
        for facilitator_data in facilitators_data:
            facilitator = Facilitator.objects.create(**facilitator_data)
            workshop.facilitators.add(facilitator)

        # Crea los participantes y los asocia al taller
        for participant_data in participants_data:
            participant_data['workshop'] = workshop  # Asocia el taller al participante
            Participant.objects.create(**participant_data)

        return workshop

    def update(self, instance, validated_data):
        facilitators_data = validated_data.pop('facilitators', None)  # Extrae los facilitadores
        participants_data = validated_data.pop('participants', None)  # Extrae los participantes

        # Actualiza los campos del taller
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualiza los facilitadores
        if facilitators_data is not None:
            instance.facilitators.clear()
            for facilitator_data in facilitators_data:
                if 'id' in facilitator_data:
                    facilitator = Facilitator.objects.get(id=facilitator_data['id'])
                else:
                    facilitator = Facilitator.objects.create(**facilitator_data)
                instance.facilitators.add(facilitator)

        # Actualiza los participantes
        if participants_data is not None:
            for participant_data in participants_data:
                if 'id' in participant_data:
                    participant = Participant.objects.get(id=participant_data['id'])
                    for attr, value in participant_data.items():
                        setattr(participant, attr, value)
                    participant.save()
                else:
                    participant_data['workshop'] = instance  # Asocia el taller al participante
                    Participant.objects.create(**participant_data)

        return instance