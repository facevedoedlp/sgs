from django.contrib import admin
from .models import Socio, SocioEstado, CategoriaSocio


@admin.register(SocioEstado)
class SocioEstadoAdmin(admin.ModelAdmin):
    list_display = ['socioestadoid', 'nombre', 'habilitado', 'visible']
    list_filter = ['habilitado', 'visible']
    search_fields = ['nombre']


@admin.register(CategoriaSocio)
class CategoriaSocioAdmin(admin.ModelAdmin):
    list_display = ['categoriasocioid', 'nombre', 'alias', 'grupo', 'orden']
    list_filter = ['grupo', 'habilita_grupo_familiar']
    search_fields = ['nombre', 'alias']
    ordering = ['orden']


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ['personaid', 'nrosocio', 'legajo', 'get_nombre', 'get_estado', 'get_categoria', 'fecha_alta']
    list_filter = ['socioestadoid', 'categoriasocioid', 'socio_minuto']
    search_fields = ['nrosocio', 'legajo', 'personaid__nombre', 'personaid__apellido', 'personaid__documento']
    raw_id_fields = ['personaid']

    def get_nombre(self, obj):
        return obj.personaid.nombre_completo() if obj.personaid else '-'

    get_nombre.short_description = 'Nombre'

    def get_estado(self, obj):
        return obj.socioestadoid.nombre if obj.socioestadoid else '-'

    get_estado.short_description = 'Estado'

    def get_categoria(self, obj):
        return obj.categoriasocioid.nombre if obj.categoriasocioid else '-'

    get_categoria.short_description = 'Categoría'