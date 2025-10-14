from rest_framework import serializers
from .models import Queja, HistorialQueja, CambioEstado

class QuejaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queja
        fields = '__all__'

class HistorialQuejaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialQueja
        fields = '__all__'

class CambioEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CambioEstado
        fields = '__all__'
