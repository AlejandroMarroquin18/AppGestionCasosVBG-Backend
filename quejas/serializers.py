from rest_framework import serializers
from .models import Queja, HistorialQueja

class QuejaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queja
        fields = '__all__'

class HistorialQuejaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialQueja
        fields = '__all__'
