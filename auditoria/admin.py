from django.contrib import admin
from .models import SocioHistoria

@admin.register(SocioHistoria)
class SocioHistoriaAdmin(admin.ModelAdmin):
    list_display = ['sociohistoriaid', 'socio', 'accion', 'estado', 'fecha_accion', 'usuario']
    list_filter = ['accion', 'estado', 'fecha_accion']
    search_fields = ['socio__numero_socio', 'observaciones']
    readonly_fields = ['fecha_accion']