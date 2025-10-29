"""
Django Admin para el módulo de Deportes
Sistema de Gestión de Socios - Club Estudiantes de La Plata
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Lugar, Frecuencia, TipoBeca, Disciplina, Categoria,
    GrupoHorario, Inscripcion, InscripcionHistorial, PagoActividad
)


# ============================================
# INLINE ADMINS
# ============================================

class CategoriaInline(admin.TabularInline):
    model = Categoria
    extra = 0
    fields = ['nombre', 'nivel', 'edad_desde', 'edad_hasta', 'activa', 'orden']


class GrupoHorarioInline(admin.TabularInline):
    model = GrupoHorario
    extra = 0
    fields = ['nombre', 'frecuencia', 'lugar', 'horario_inicio', 'horario_fin',
              'arancel_socio', 'arancel_no_socio', 'cupo_maximo', 'activo']
    readonly_fields = []


class InscripcionHistorialInline(admin.TabularInline):
    model = InscripcionHistorial
    extra = 0
    can_delete = False
    fields = ['fecha', 'accion', 'descripcion', 'usuario']
    readonly_fields = ['fecha', 'accion', 'descripcion', 'usuario']

    def has_add_permission(self, request, obj=None):
        return False


# ============================================
# ADMIN CLASSES - CATÁLOGOS
# ============================================

@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'capacidad_maxima', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'direccion']
    list_editable = ['activo']
    ordering = ['nombre']

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'direccion', 'capacidad_maxima', 'activo')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Frecuencia)
class FrecuenciaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'dias_display', 'activa', 'created_at']
    list_filter = ['activa', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    search_fields = ['nombre']
    list_editable = ['activa']
    ordering = ['nombre']

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'activa')
        }),
        ('Días de la Semana', {
            'fields': (('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'),)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def dias_display(self, obj):
        dias = obj.get_dias_semana()
        return ', '.join(dias) if dias else 'Ninguno'

    dias_display.short_description = 'Días'


@admin.register(TipoBeca)
class TipoBecaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'porcentaje_descuento', 'requiere_autorizacion',
                    'requiere_documentacion', 'activa']
    list_filter = ['activa', 'requiere_autorizacion', 'requiere_documentacion']
    search_fields = ['nombre', 'codigo', 'descripcion']
    list_editable = ['activa']
    ordering = ['nombre']

    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'nombre', 'descripcion', 'activa')
        }),
        ('Descuento', {
            'fields': ('porcentaje_descuento',)
        }),
        ('Requisitos', {
            'fields': ('requiere_autorizacion', 'requiere_documentacion', 'documentacion_requerida')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


# ============================================
# ADMIN CLASSES - DISCIPLINAS Y CATEGORÍAS
# ============================================

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_actividad', 'requiere_apto_medico', 'es_temporada',
                    'temporada_display', 'activa', 'orden']
    list_filter = ['activa', 'tipo_actividad', 'es_temporada', 'requiere_apto_medico']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activa', 'orden']
    ordering = ['orden', 'nombre']
    inlines = [CategoriaInline]

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'tipo_actividad', 'descripcion', 'activa', 'orden')
        }),
        ('Requisitos', {
            'fields': ('requiere_apto_medico', 'edad_minima', 'edad_maxima')
        }),
        ('Temporada', {
            'fields': ('es_temporada', 'fecha_inicio_temporada', 'fecha_fin_temporada'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def temporada_display(self, obj):
        if not obj.es_temporada:
            return '-'
        if obj.fecha_inicio_temporada and obj.fecha_fin_temporada:
            return f"{obj.fecha_inicio_temporada.strftime('%d/%m/%Y')} - {obj.fecha_fin_temporada.strftime('%d/%m/%Y')}"
        return 'Sin fechas'

    temporada_display.short_description = 'Temporada'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'disciplina', 'nivel', 'edad_rango', 'activa', 'orden']
    list_filter = ['activa', 'nivel', 'disciplina']
    search_fields = ['nombre', 'disciplina__nombre']
    list_editable = ['activa', 'orden']
    ordering = ['disciplina', 'orden', 'nombre']
    inlines = [GrupoHorarioInline]

    fieldsets = (
        ('Información General', {
            'fields': ('disciplina', 'nombre', 'nivel', 'descripcion', 'activa', 'orden')
        }),
        ('Rango de Edad', {
            'fields': ('edad_desde', 'edad_hasta')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def edad_rango(self, obj):
        if obj.edad_desde and obj.edad_hasta:
            return f"{obj.edad_desde} - {obj.edad_hasta} años"
        elif obj.edad_desde:
            return f"{obj.edad_desde}+ años"
        elif obj.edad_hasta:
            return f"Hasta {obj.edad_hasta} años"
        return 'Sin límite'

    edad_rango.short_description = 'Edad'


# ============================================
# ADMIN CLASSES - GRUPOS Y HORARIOS
# ============================================

@admin.register(GrupoHorario)
class GrupoHorarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'lugar', 'frecuencia', 'horario_display',
                    'arancel_socio', 'arancel_no_socio', 'inscriptos_display',
                    'instructor', 'activo']
    list_filter = ['activo', 'categoria__disciplina', 'categoria', 'lugar', 'frecuencia']
    search_fields = ['nombre', 'categoria__nombre', 'categoria__disciplina__nombre']
    list_editable = ['activo']
    ordering = ['categoria', 'nombre']
    autocomplete_fields = ['categoria', 'lugar', 'frecuencia', 'instructor']

    fieldsets = (
        ('Información General', {
            'fields': ('categoria', 'nombre', 'activo')
        }),
        ('Horario y Lugar', {
            'fields': ('frecuencia', 'horario_inicio', 'horario_fin', 'lugar')
        }),
        ('Aranceles', {
            'fields': ('arancel_socio', 'arancel_no_socio')
        }),
        ('Cupos e Instructor', {
            'fields': ('cupo_maximo', 'instructor')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def horario_display(self, obj):
        if obj.horario_inicio and obj.horario_fin:
            return f"{obj.horario_inicio.strftime('%H:%M')} - {obj.horario_fin.strftime('%H:%M')}"
        return '-'

    horario_display.short_description = 'Horario'

    def inscriptos_display(self, obj):
        count = obj.get_inscriptos_count()
        if obj.cupo_maximo:
            porcentaje = (count / obj.cupo_maximo) * 100
            color = 'green' if porcentaje < 70 else ('orange' if porcentaje < 90 else 'red')
            return format_html(
                '<span style="color: {};">{}/{}</span>',
                color, count, obj.cupo_maximo
            )
        return f"{count} inscriptos"

    inscriptos_display.short_description = 'Inscriptos'


# ============================================
# ADMIN CLASSES - INSCRIPCIONES
# ============================================

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ['persona', 'grupo_horario', 'estado', 'fecha_inscripcion',
                    'arancel_display', 'beca_display', 'apto_display']
    list_filter = ['estado', 'beca_aprobada', 'apto_medico_presentado',
                   'grupo_horario__categoria__disciplina', 'fecha_inscripcion']
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__documento',
                     'grupo_horario__nombre']
    date_hierarchy = 'fecha_inscripcion'
    ordering = ['-fecha_inscripcion']
    autocomplete_fields = ['persona', 'grupo_horario', 'beca']
    inlines = [InscripcionHistorialInline]

    fieldsets = (
        ('Información General', {
            'fields': ('persona', 'grupo_horario', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inscripcion', 'fecha_inicio', 'fecha_baja')
        }),
        ('Beca/Descuento', {
            'fields': ('beca', 'beca_aprobada', 'beca_aprobada_por', 'beca_aprobada_fecha',
                       'porcentaje_descuento_adicional'),
            'classes': ('collapse',)
        }),
        ('Apto Médico', {
            'fields': ('apto_medico_presentado', 'apto_medico_vencimiento'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones', 'observaciones_internas'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'beca_aprobada_por', 'beca_aprobada_fecha']

    def arancel_display(self, obj):
        base = obj.get_arancel_base()
        final = obj.get_arancel_con_descuento()
        if base != final:
            return format_html(
                '<span style="text-decoration: line-through;">${}</span> <span style="color: green; font-weight: bold;">${}</span>',
                base, final
            )
        return f"${final}"

    arancel_display.short_description = 'Arancel'

    def beca_display(self, obj):
        if not obj.beca:
            return '-'
        if obj.beca_aprobada:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.beca.nombre
            )
        return format_html(
            '<span style="color: orange;">⏳ {}</span>',
            obj.beca.nombre
        )

    beca_display.short_description = 'Beca'

    def apto_display(self, obj):
        if not obj.grupo_horario.categoria.disciplina.requiere_apto_medico:
            return '-'

        if obj.necesita_renovar_apto_medico():
            return format_html('<span style="color: red;">✗ Vencido/Faltante</span>')

        return format_html('<span style="color: green;">✓ Vigente</span>')

    apto_display.short_description = 'Apto Médico'

    actions = ['aprobar_inscripciones', 'aprobar_becas', 'dar_de_baja']

    def aprobar_inscripciones(self, request, queryset):
        count = 0
        for inscripcion in queryset.filter(estado='PENDIENTE'):
            inscripcion.aprobar(usuario=request.user)
            count += 1
        self.message_user(request, f"{count} inscripciones aprobadas correctamente")

    aprobar_inscripciones.short_description = "Aprobar inscripciones seleccionadas"

    def aprobar_becas(self, request, queryset):
        count = 0
        for inscripcion in queryset.filter(beca__isnull=False, beca_aprobada=False):
            inscripcion.aprobar_beca(usuario=request.user)
            count += 1
        self.message_user(request, f"{count} becas aprobadas correctamente")

    aprobar_becas.short_description = "Aprobar becas seleccionadas"

    def dar_de_baja(self, request, queryset):
        count = queryset.filter(estado__in=['ACTIVA', 'PENDIENTE']).update(
            estado='BAJA'
        )
        self.message_user(request, f"{count} inscripciones dadas de baja")

    dar_de_baja.short_description = "Dar de baja inscripciones seleccionadas"


# ============================================
# ADMIN CLASSES - PAGOS
# ============================================

@admin.register(PagoActividad)
class PagoActividadAdmin(admin.ModelAdmin):
    list_display = ['inscripcion', 'periodo_display', 'monto_final', 'estado',
                    'fecha_vencimiento', 'vencido_display']
    list_filter = ['estado', 'mes', 'anio', 'fecha_vencimiento']
    search_fields = ['inscripcion__persona__nombre', 'inscripcion__persona__apellido',
                     'inscripcion__persona__documento']
    date_hierarchy = 'fecha_vencimiento'
    ordering = ['-anio', '-mes']
    autocomplete_fields = ['inscripcion']

    fieldsets = (
        ('Inscripción', {
            'fields': ('inscripcion',)
        }),
        ('Período', {
            'fields': ('mes', 'anio')
        }),
        ('Montos', {
            'fields': ('monto_base', 'descuento_porcentaje', 'monto_descuento', 'monto_final')
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_vencimiento', 'fecha_pago')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def periodo_display(self, obj):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{meses[obj.mes - 1]} {obj.anio}"

    periodo_display.short_description = 'Período'

    def vencido_display(self, obj):
        if obj.esta_vencido():
            return format_html('<span style="color: red; font-weight: bold;">✗ Vencido</span>')
        return format_html('<span style="color: green;">✓ Al día</span>')

    vencido_display.short_description = 'Estado'

    actions = ['marcar_como_pagado']

    def marcar_como_pagado(self, request, queryset):
        count = 0
        for pago in queryset.filter(estado='PENDIENTE'):
            pago.marcar_como_pagado()
            count += 1
        self.message_user(request, f"{count} pagos marcados como pagados")

    marcar_como_pagado.short_description = "Marcar como pagado"


# ============================================
# CONFIGURACIÓN GLOBAL
# ============================================

# Configurar búsqueda autocomplete
admin.site.site_header = "Administración - Club Estudiantes"
admin.site.site_title = "SGS León Club"
admin.site.index_title = "Módulo de Deportes"