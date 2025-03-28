from rest_framework import serializers
from .models import Participant

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            'id', 'workshop', 'email', 'full_name', 'document_type', 
            'document_number', 'age', 'disability', 
            'program', 'gender_identity', 'self_recognition', 
            'institutional_email', 'terms_accepted'
        ]