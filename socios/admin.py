from django.contrib import admin
from .models import (
    Socio,
    SocioGrupoFamiliar,
    SocioGrupoFamiliarMiembro,
    SocioDiscapacidad,
    SocioDiscapacidadAcompanante,
    SocioDomicilioPagoSas
)


# Inline para mostrar historial dentro de Socio (opcional)
class GrupoFamiliarMiembroInline(admin.TabularInline):
    model = SocioGrupoFamiliarMiembro
    extra = 0
    fields = ['grupo_familiar', 'es_titular', 'fecha_alta', 'fecha_baja']
    raw_id_fields = ['grupo_familiar']
    verbose_name = 'Grupo Familiar'
    verbose_name_plural = 'Grupos Familiares del Socio'


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = [
        'numero_socio',
        'get_nombre_completo',
        'get_documento',
        'estado',
        'categoria',
        'filial',
        'fecha_alta'
    ]
    list_filter = ['estado', 'categoria', 'filial', 'fecha_alta']
    search_fields = [
        'numero_socio',
        'persona__apellido',
        'persona__nombre',
        'persona__documento'
    ]
    date_hierarchy = 'fecha_alta'
    raw_id_fields = ['persona']

    # Mostrar grupos familiares del socio
    inlines = [GrupoFamiliarMiembroInline]

    fieldsets = (
        ('Información del Socio', {
            'fields': ('persona', 'numero_socio')
        }),
        ('Estado Actual', {
            'fields': ('estado', 'categoria', 'filial')
        }),
        ('Fechas', {
            'fields': ('fecha_alta',)
        }),
    )

    def get_nombre_completo(self, obj):
        return obj.persona.nombre_completo if obj.persona else '-'

    get_nombre_completo.short_description = 'Nombre Completo'
    get_nombre_completo.admin_order_field = 'persona__apellido'

    def get_documento(self, obj):
        return obj.persona.documento if obj.persona else '-'

    get_documento.short_description = 'Documento'
    get_documento.admin_order_field = 'persona__documento'


# Inline para acompañantes dentro de Discapacidad
class AcompananteInline(admin.TabularInline):
    model = SocioDiscapacidadAcompanante
    extra = 1
    fields = ['apellido', 'nombre', 'documento', 'vinculo', 'fecha_desde', 'fecha_hasta']


@admin.register(SocioDiscapacidad)
class SocioDiscapacidadAdmin(admin.ModelAdmin):
    list_display = [
        'get_socio_numero',
        'get_socio_nombre',
        'numero_certificado',
        'tipo_discapacidad',
        'fecha_desde',
        'fecha_hasta',
        'esta_vigente'
    ]
    list_filter = ['fecha_desde', 'fecha_hasta', 'tipo_discapacidad']
    search_fields = [
        'socio__numero_socio',
        'socio__persona__apellido',
        'socio__persona__nombre',
        'numero_certificado'
    ]
    raw_id_fields = ['socio']
    inlines = [AcompananteInline]

    fieldsets = (
        ('Socio', {
            'fields': ('socio',)
        }),
        ('Certificado', {
            'fields': ('numero_certificado', 'tipo_discapacidad', 'fecha_desde', 'fecha_hasta')
        }),
        ('Información Adicional', {
            'fields': ('auditor_responsable', 'observaciones'),
            'classes': ('collapse',)
        }),
    )

    def get_socio_numero(self, obj):
        return obj.socio.numero_socio

    get_socio_numero.short_description = 'Nº Socio'
    get_socio_numero.admin_order_field = 'socio__numero_socio'

    def get_socio_nombre(self, obj):
        return obj.socio.persona.nombre_completo

    get_socio_nombre.short_description = 'Socio'
    get_socio_nombre.admin_order_field = 'socio__persona__apellido'

    def esta_vigente(self, obj):
        return "✓ Vigente" if obj.esta_vigente else "✗ Vencido"

    esta_vigente.short_description = 'Estado'


@admin.register(SocioDomicilioPagoSas)
class SocioDomicilioPagoSasAdmin(admin.ModelAdmin):
    list_display = [
        'get_socio_numero',
        'get_socio_nombre',
        'calle',
        'numero',
        'localidad',
        'provincia'
    ]
    search_fields = [
        'socio__numero_socio',
        'socio__persona__apellido',
        'socio__persona__nombre',
        'calle',
        'localidad'
    ]
    raw_id_fields = ['socio']

    fieldsets = (
        ('Socio', {
            'fields': ('socio',)
        }),
        ('Domicilio', {
            'fields': ('calle', 'numero', 'piso', 'departamento')
        }),
        ('Ubicación', {
            'fields': ('codigo_postal', 'localidad', 'provincia', 'pais')
        }),
    )

    def get_socio_numero(self, obj):
        return obj.socio.numero_socio

    get_socio_numero.short_description = 'Nº Socio'
    get_socio_numero.admin_order_field = 'socio__numero_socio'

    def get_socio_nombre(self, obj):
        return obj.socio.persona.nombre_completo

    get_socio_nombre.short_description = 'Socio'
    get_socio_nombre.admin_order_field = 'socio__persona__apellido'


# Inline para miembros dentro de Grupo Familiar
class GrupoFamiliarMiembroInlineParaGrupo(admin.TabularInline):
    model = SocioGrupoFamiliarMiembro
    extra = 1
    fields = ['socio', 'es_titular', 'fecha_alta', 'fecha_baja']
    raw_id_fields = ['socio']


@admin.register(SocioGrupoFamiliar)
class SocioGrupoFamiliarAdmin(admin.ModelAdmin):
    list_display = ['grupofamiliarid', 'get_titular', 'cantidad_miembros', 'fecha_desde', 'fecha_hasta', 'activo']
    list_filter = ['activo', 'fecha_desde']
    date_hierarchy = 'fecha_desde'
    inlines = [GrupoFamiliarMiembroInlineParaGrupo]

    fieldsets = (
        ('Información del Grupo', {
            'fields': ('fecha_desde', 'fecha_hasta', 'activo')
        }),
    )

    def get_titular(self, obj):
        titular = obj.socio_titular
        if titular:
            return f"{titular.numero_socio} - {titular.persona.nombre_completo}"
        return "⚠️ Sin titular"

    get_titular.short_description = 'Socio Titular'

    def cantidad_miembros(self, obj):
        return obj.cantidad_miembros

    cantidad_miembros.short_description = 'Miembros'


@admin.register(SocioGrupoFamiliarMiembro)
class SocioGrupoFamiliarMiembroAdmin(admin.ModelAdmin):
    list_display = [
        'grupofamiliarmiembroid',
        'grupo_familiar',
        'get_socio_numero',
        'get_socio_nombre',
        'es_titular',
        'fecha_alta',
        'fecha_baja'
    ]
    list_filter = ['es_titular', 'fecha_alta']
    search_fields = [
        'socio__numero_socio',
        'socio__persona__apellido',
        'socio__persona__nombre'
    ]
    raw_id_fields = ['grupo_familiar', 'socio']

    def get_socio_numero(self, obj):
        return obj.socio.numero_socio

    get_socio_numero.short_description = 'Nº Socio'
    get_socio_numero.admin_order_field = 'socio__numero_socio'

    def get_socio_nombre(self, obj):
        return obj.socio.persona.nombre_completo

    get_socio_nombre.short_description = 'Socio'
    get_socio_nombre.admin_order_field = 'socio__persona__apellido'