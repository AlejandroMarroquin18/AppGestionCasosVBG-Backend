from django.db import models
from django.contrib.auth.models import AbstractUser
import string
import secrets
#Create your models here.
#Usuarios
class Usuarios(AbstractUser):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=30)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    username = models.CharField(max_length=150, unique=False, default='')
    refresh_token = models.TextField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'  # Ahora el email es el campo principal de autenticación
    REQUIRED_FIELDS = [ 'nombre', 'rol', 'telefono']


#Tokens de recuperacion de contraseña
def generar_codigo():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(6))

class Restore_Password_Token(models.Model):
    codigo=models.CharField(max_length=6, unique=True,default=generar_codigo)
    email=models.EmailField(unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)



class GoogleOAuth(models.Model):
    user = models.OneToOneField(Usuarios, on_delete=models.CASCADE, related_name='google_oauth')
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_type = models.CharField(max_length=20, default='Bearer')
    scope = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField()  # UTC
    raw = models.JSONField(default=dict, blank=True)  # respuesta completa opcional
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GoogleOAuth({self.user.email})"