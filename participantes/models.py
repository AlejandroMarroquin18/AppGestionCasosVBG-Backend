from django.db import models
from talleres.models import Workshop  # Importamos Workshop

class Participant(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="participants")
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100)
    document_number = models.CharField(max_length=100, unique=True)  # Aseguramos que sea único
    age = models.IntegerField()
    disability = models.CharField(max_length=100, null=True, blank=True)
    program = models.CharField(max_length=255, null=True, blank=True)  # Nuevo campo para el programa académico / dependencia
    gender_identity = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo para la identidad de género
    self_recognition = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo para el auto-reconocimiento
    terms_accepted = models.BooleanField(default=False, null=True, blank=True)  # Aceptación de los términos y condiciones
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.full_name
