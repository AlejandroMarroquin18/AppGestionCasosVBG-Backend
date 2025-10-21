from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Usuarios,Restore_Password_Token

class UserSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True)
    class Meta:
        model = Usuarios
        fields=[ 'id','nombre', 'email','rol','telefono','password']
    def create(self, validated_data):
        # Cambiar el valor del campo 'rol' antes de crear
        validated_data['rol'] = 'visitor'  # ejemplo: forzar a un valor específico

        # O si quieres hacerlo condicionalmente:
        # if validated_data['rol'] == 'developer':
        #     validated_data['rol'] = 'administrador'

class RestorePasswordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=Restore_Password_Token
        fields=['id','codigo','email','creado_en']
        read_only_fields = ['codigo','email', 'creado_en']

