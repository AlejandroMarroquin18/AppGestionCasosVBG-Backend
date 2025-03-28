from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Usuarios,Restore_Password_Token

class UserSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True)
    class Meta:
        model = Usuarios
        fields=[ 'id','nombre', 'email','rol','telefono','password']

class RestorePasswordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=Restore_Password_Token
        fields=['id','codigo','email','creado_en']
        read_only_fields = ['codigo','email', 'creado_en']

'''class QuejaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quejas
        fields=fields = '__all__'''