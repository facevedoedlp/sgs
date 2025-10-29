from django.contrib import admin
from .models import SociosEstado, CategoriaSocio, Filial, SociosHistoriaAccion

@admin.register(SociosEstado)
class SociosEstadoAdmin(admin.ModelAdmin):
    list_display = ['socioestadoid', 'descripcion', 'vigente', 'indica_socio_activo']
    list_filter = ['vigente', 'indica_socio_activo']
    search_fields = ['descripcion']


@admin.register(CategoriaSocio)
class CategoriaSocioAdmin(admin.ModelAdmin):
    list_display = ['categoriasocioid', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['descripcion']


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['filialid', 'descripcion', 'domicilio', 'vigente']
    list_filter = ['vigente']
    search_fields = ['descripcion', 'domicilio']


@admin.register(SociosHistoriaAccion)
class SociosHistoriaAccionAdmin(admin.ModelAdmin):
    list_display = ['accionid', 'descripcion']
    search_fields = ['descripcion']