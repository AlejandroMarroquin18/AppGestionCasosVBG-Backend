


from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuarios(AbstractUser):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=30)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    username = models.CharField(max_length=150, unique=False, default='')
    USERNAME_FIELD = 'email'  # Ahora el email es el campo principal de autenticación
    REQUIRED_FIELDS = [ 'password','nombre', 'rol', 'telefono']

