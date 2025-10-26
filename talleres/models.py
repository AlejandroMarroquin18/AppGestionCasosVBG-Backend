import base64
import qrcode
from django.db import models
from io import BytesIO
from django.conf import settings

class Facilitator(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Workshop(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    details = models.TextField()
    location = models.CharField(max_length=255)
    modality = models.CharField(max_length=10, choices=(('presencial', 'Presencial'), ('virtual', 'Virtual')))
    slots = models.IntegerField()
    facilitators = models.ManyToManyField(Facilitator)
    qr_imagen = models.TextField(null=True, blank=True)  # Para guardar base64
    qr_link = models.URLField(max_length=500, null=True, blank=True)  # Enlace de inscripción
    sede = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        """Genera el QR en base64 sin guardar archivo físico"""
        # URL de inscripción pública (sin autenticación)
        qr_url = f"http://localhost:3000/inscripcion/{self.id}"
        self.qr_link = qr_url
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Convertir a base64
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        self.qr_imagen = qr_base64
        
        return qr_base64

    def save(self, *args, **kwargs):
        is_new = not self.pk
        
        if is_new:
            super().save(*args, **kwargs)  # Guarda primero para obtener ID
            
        # Generar QR si es nuevo o si no tiene QR
        if not self.qr_imagen:
            self.generate_qr_code()
            # Guardar solo los campos del QR
            super().save(update_fields=['qr_imagen', 'qr_link'])
        else:
            super().save(*args, **kwargs)

    @property
    def available_slots(self):
        """Calcula los cupos disponibles"""
        from participantes.models import Participant
        registered_count = Participant.objects.filter(workshop=self).count()
        return self.slots - registered_count