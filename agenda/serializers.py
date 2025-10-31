from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = Event
        fields = '__all__'
    
    def validate_google_event_id(self, value):
        if value == "":
            return None
        return value

