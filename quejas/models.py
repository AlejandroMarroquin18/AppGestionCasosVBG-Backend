from django.db import models

class Queja(models.Model):
    nombre = models.CharField(max_length=100)
    sede = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    facultad = models.CharField(max_length=100, null=True)
    unidad = models.CharField(max_length=100, null=True)
    tipo_de_acompanamiento = models.CharField(max_length=100)
    fecha = models.DateField()
    estado = models.CharField(max_length=100)
    detalles = models.TextField()

    def __str__(self):
        return f"{self.nombre} - {self.sede} - {self.estado}"