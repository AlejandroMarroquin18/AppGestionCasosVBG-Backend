

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Usuarios

class UserSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True)
    class Meta:
        model = Usuarios
        fields=[ 'id','nombre', 'email','rol','telefono','password']