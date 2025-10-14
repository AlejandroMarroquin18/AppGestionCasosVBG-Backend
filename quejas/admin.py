from django.contrib import admin
from .models import Queja, CambioEstado

##admin.site.register(Queja) Poner esta linea y quitar la de abajo si da error


class CambioEstadoInline(admin.StackedInline):
    model = CambioEstado
    extra = 0
    readonly_fields = ('fecha', 'estado_anterior', 'nuevo_estado', 'usuario')
    can_delete = False

@admin.register(Queja)
class QuejaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'tipo_de_acompanamiento', 'unidad')
    search_fields = ('id', 'estado', 'unidad', 'reporta_nombre', 'afectado_nombre')
    inlines = [CambioEstadoInline]  # 👈 muestra el historial dentro del detalle

@admin.register(CambioEstado)
class CambioEstadoAdmin(admin.ModelAdmin):
    list_display = ('queja_id', 'fecha', 'estado_anterior', 'nuevo_estado', 'usuario')
    list_filter = ('nuevo_estado', 'usuario')
