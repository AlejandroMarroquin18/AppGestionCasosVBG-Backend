import os
import qrcode
from django.db import models
from io import BytesIO
from django.core.files.base import ContentFile
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
    sede = models.CharField(max_length=100, blank=True, null=True)
    facilitators = models.ManyToManyField(Facilitator)  # Relación muchos a muchos
    qr_code_url = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        """Genera el QR con la URL de inscripción que incluye el ID del taller"""
        # Ahora que el taller ya tiene un ID, creamos la URL con el ID
        qr_url = f"http://localhost:3000/inscripcion/{self.id}"

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
        img.save(buffer)
        buffer.seek(0)

        # Guardar el archivo QR en el directorio media
        file_name = f"qrcode_{self.id}.png"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Guardamos el archivo en el sistema de archivos
        with open(file_path, 'wb') as f:
            f.write(buffer.read())

        return file_name

    def save(self, *args, **kwargs):
        if not self.pk:  # Solo guardamos el taller si no tiene un ID (es un nuevo taller)
            super().save(*args, **kwargs)  # Guarda el taller y asigna un ID

        # Generamos el código QR solo después de que el taller haya sido guardado y tenga un ID
        if not self.qr_code_url:  # Si no se ha asignado un QR
            file_name = self.generate_qr_code()  # Generar el archivo QR
            self.qr_code_url = f"{settings.MEDIA_URL}{file_name}"  # Asignar la URL del archivo QR

            # Actualizamos solo la URL del QR sin crear un nuevo taller
            super().save(update_fields=["qr_code_url"])  # Solo actualizamos el campo QR