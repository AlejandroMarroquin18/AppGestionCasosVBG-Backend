from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Queja, CambioEstado

@receiver(pre_save, sender=Queja)
def detectar_cambio_estado(sender, instance, **kwargs):
    """Guarda el estado anterior antes de actualizar la queja."""
    if instance.pk:
        try:
            old_instance = Queja.objects.get(pk=instance.pk)
            instance._estado_anterior = old_instance.estado
        except Queja.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=Queja)
def crear_cambio_estado(sender, instance, created, **kwargs):
    """Crea un CambioEstado si el estado cambió."""
    if not created:
        estado_anterior = getattr(instance, "_estado_anterior", None)
        nuevo_estado = instance.estado
        if estado_anterior and estado_anterior != nuevo_estado:
            CambioEstado.objects.create(
                queja_id=instance,
                estado_anterior=estado_anterior,
                nuevo_estado=nuevo_estado,
                usuario=getattr(instance, "_user", None),  # 👈 se asignará desde la vista
            )
