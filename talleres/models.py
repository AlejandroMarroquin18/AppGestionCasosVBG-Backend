from django.db import models

class Workshop(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    details = models.TextField()
    location = models.CharField(max_length=255)
    modality = models.CharField(max_length=10, choices=(('presencial', 'Presencial'), ('virtual', 'Virtual')))
    slots = models.IntegerField()
    facilitator = models.CharField(max_length=255)  # Asumiendo que este es el "Tallerista"

    def __str__(self):
        return self.name
