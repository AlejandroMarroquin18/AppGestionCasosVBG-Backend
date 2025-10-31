from django.db import models
from quejas.models import Queja
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class Event(models.Model):
    title=models.CharField(max_length=255,blank=True)#Titulo
    description=models.CharField(blank=True)#Descripcion
    status=models.CharField(default='Creado', blank=True)#Cancelado, aplazado y tales
    location=models.CharField(max_length=255, blank=True)#lugar
    attendes = ArrayField(models.EmailField(), blank=True, default=list, null=True)#asistentes, correos electronicos preferiblemente
    color= models.CharField(max_length=8,blank=True,null=True)#Colores
    organizer=models.CharField(max_length=255, blank=True, null=True)#organizador de la reunion, quien lo hace


    startdatehour=models.DateTimeField()#hora de inicio, en formato yyyy-mm-ddThh:mm o algo así
    enddatehour=models.DateTimeField()#Hora de finalizacion
    timezone=models.CharField(max_length=100, default='America/Bogota')#Zona horaria

    type= models.CharField(max_length=100, blank=True)##Tipo de reunion/orientacion/asesoría
    ##case_id=models.CharField(max_length=100)##id de la queja relacionada
    case_id = models.ForeignKey('quejas.Queja',on_delete=models.SET_NULL,null=True,blank=True)


    ##Descartar si no se van a usar más
    create_meet = models.BooleanField(default=False,blank=True, null=True)
    meet_link = models.URLField(null=True, blank=True)
    google_event_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        return self.title


    
    


