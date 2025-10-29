"""
Modelos para el módulo de Deportes
Sistema de Gestión de Socios - Club Estudiantes de La Plata
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from personas.models import Persona
from socios.models import Socio


# ============================================
# 1. CATÁLOGOS BASE
# ============================================

class Lugar(models.Model):
    """Lugares/Sedes donde se realizan actividades deportivas"""
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    capacidad_maxima = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Capacidad máxima del lugar (opcional)"
    )
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deportes_lugares'
        verbose_name = 'Lugar'
        verbose_name_plural = 'Lugares'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Frecuencia(models.Model):
    """Frecuencias de actividades (días de la semana)"""
    nombre = models.CharField(
        max_length=50,
        unique=True,
        help_text="Ej: 'LU MI VI', 'MA JU', 'PASE LIBRE'"
    )

    # Días de la semana
    lunes = models.BooleanField(default=False)
    martes = models.BooleanField(default=False)
    miercoles = models.BooleanField(default=False)
    jueves = models.BooleanField(default=False)
    viernes = models.BooleanField(default=False)
    sabado = models.BooleanField(default=False)
    domingo = models.BooleanField(default=False)

    activa = models.BooleanField(default=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deportes_frecuencias'
        verbose_name = 'Frecuencia'
        verbose_name_plural = 'Frecuencias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_dias_semana(self):
        """Retorna lista de días activos"""
        dias = []
        if self.lunes: dias.append('Lunes')
        if self.martes: dias.append('Martes')
        if self.miercoles: dias.append('Miércoles')
        if self.jueves: dias.append('Jueves')
        if self.viernes: dias.append('Viernes')
        if self.sabado: dias.append('Sábado')
        if self.domingo: dias.append('Domingo')
        return dias


class TipoBeca(models.Model):
    """Tipos de becas y descuentos para actividades deportivas"""
    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código único para identificar la beca"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    porcentaje_descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento (0-100)"
    )

    requiere_autorizacion = models.BooleanField(
        default=True,
        help_text="Si requiere aprobación de Secretaría de Deportes"
    )
    requiere_documentacion = models.BooleanField(
        default=False,
        help_text="Si requiere presentar documentación"
    )
    documentacion_requerida = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de la documentación necesaria"
    )

    activa = models.BooleanField(default=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deportes_tipos_beca'
        verbose_name = 'Tipo de Beca'
        verbose_name_plural = 'Tipos de Beca'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje_descuento}%)"


# ============================================
# 2. DISCIPLINAS Y CATEGORÍAS
# ============================================

class Disciplina(models.Model):
    """Disciplinas deportivas del club"""

    TIPO_ACTIVIDAD_CHOICES = [
        ('DEPORTE', 'Deporte'),
        ('NATACION', 'Natación'),
        ('GIMNASIO', 'Gimnasio'),
        ('COLONIA', 'Colonia'),
        ('CURSO', 'Curso'),
        ('EVENTO', 'Evento'),
        ('OTRO', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    tipo_actividad = models.CharField(
        max_length=20,
        choices=TIPO_ACTIVIDAD_CHOICES,
        default='DEPORTE'
    )
    descripcion = models.TextField(blank=True, null=True)

    # Requisitos
    requiere_apto_medico = models.BooleanField(
        default=False,
        help_text="Si requiere certificado médico"
    )
    edad_minima = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Edad mínima para inscribirse (opcional)"
    )
    edad_maxima = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Edad máxima para inscribirse (opcional)"
    )

    # Temporalidad
    es_temporada = models.BooleanField(
        default=False,
        help_text="Si la actividad es por temporada (ej: colonias)"
    )
    fecha_inicio_temporada = models.DateField(null=True, blank=True)
    fecha_fin_temporada = models.DateField(null=True, blank=True)

    activa = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de visualización"
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deportes_disciplinas'
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    def en_temporada(self):
        """Verifica si la disciplina está en temporada actual"""
        if not self.es_temporada:
            return True

        if not self.fecha_inicio_temporada or not self.fecha_fin_temporada:
            return False

        hoy = timezone.now().date()
        return self.fecha_inicio_temporada <= hoy <= self.fecha_fin_temporada


class Categoria(models.Model):
    """Categorías dentro de cada disciplina (por edad/nivel)"""

    NIVEL_CHOICES = [
        ('INICIACION', 'Iniciación'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
        ('COMPETENCIA', 'Competencia'),
        ('LIBRE', 'Libre'),
    ]

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='categorias'
    )
    nombre = models.CharField(
        max_length=100,
        help_text="Ej: 'Infantil', 'Juvenil', 'Mayores'"
    )
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='INICIACION'
    )

    # Rango de edad
    edad_desde = models.PositiveIntegerField(null=True, blank=True)
    edad_hasta = models.PositiveIntegerField(null=True, blank=True)

    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deportes_categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['disciplina', 'orden', 'nombre']
        unique_together = [['disciplina', 'nombre']]

    def __str__(self):
        return f"{self.disciplina.nombre} - {self.nombre}"


# ============================================
# 3. GRUPOS Y HORARIOS
# ============================================

class GrupoHorario(models.Model):
    """Grupos/Horarios específicos para cada categoría"""

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='grupos'
    )
    nombre = models.CharField(
        max_length=150,
        help_text="Nombre descriptivo del grupo"
    )

    # Horario
    frecuencia = models.ForeignKey(
        Frecuencia,
        on_delete=models.PROTECT,
        related_name='grupos'
    )
    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fin = models.TimeField(null=True, blank=True)

    # Lugar
    lugar = models.ForeignKey(
        Lugar,
        on_delete=models.PROTECT,
        related_name='grupos'
    )

    # Cupos
    cupo_maximo = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cantidad máxima de inscriptos (opcional)"
    )

    # Profesor/Instructor
    instructor = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grupos_asignados',
        help_text="Profesor a cargo del grupo"
    )

    # Aranceles
    arancel_socio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Precio mensual para socios"
    )
    arancel_no_socio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Precio mensual para no socios"
    )

    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deportes_grupos_horarios'
        verbose_name = 'Grupo/Horario'
        verbose_name_plural = 'Grupos/Horarios'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        horario = ""
        if self.horario_inicio and self.horario_fin:
            horario = f" - {self.horario_inicio.strftime('%H:%M')}-{self.horario_fin.strftime('%H:%M')}"
        return f"{self.categoria} - {self.nombre}{horario}"

    def get_inscriptos_count(self):
        """Retorna cantidad de inscriptos activos"""
        return self.inscripciones.filter(estado='ACTIVA').count()

    def tiene_cupo_disponible(self):
        """Verifica si hay cupo disponible"""
        if not self.cupo_maximo:
            return True
        return self.get_inscriptos_count() < self.cupo_maximo

    def get_arancel_para_persona(self, persona):
        """Retorna el arancel correspondiente según si es socio o no"""
        try:
            # Verificar si la persona es socio activo
            socio = Socio.objects.get(persona=persona, activo=True)
            return self.arancel_socio
        except Socio.DoesNotExist:
            return self.arancel_no_socio


# ============================================
# 4. INSCRIPCIONES
# ============================================

class Inscripcion(models.Model):
    """Inscripciones de personas a actividades deportivas"""

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('ACTIVA', 'Activa'),
        ('SUSPENDIDA', 'Suspendida'),
        ('BAJA', 'Baja'),
    ]

    # Relaciones principales
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='inscripciones_deportivas'
    )
    grupo_horario = models.ForeignKey(
        GrupoHorario,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )

    # Estado y fechas
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    fecha_inscripcion = models.DateField(default=timezone.now)
    fecha_inicio = models.DateField(
        help_text="Fecha desde la cual empieza a pagar"
    )
    fecha_baja = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de baja de la actividad"
    )

    # Becas y descuentos
    beca = models.ForeignKey(
        TipoBeca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscripciones'
    )
    beca_aprobada = models.BooleanField(
        default=False,
        help_text="Si la beca fue aprobada por Secretaría"
    )
    beca_aprobada_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='becas_aprobadas'
    )
    beca_aprobada_fecha = models.DateTimeField(null=True, blank=True)

    porcentaje_descuento_adicional = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Descuento adicional manual (0-100)"
    )

    # Certificado médico
    apto_medico_presentado = models.BooleanField(
        default=False,
        help_text="Si presentó el apto médico"
    )
    apto_medico_vencimiento = models.DateField(null=True, blank=True)

    observaciones = models.TextField(blank=True, null=True)
    observaciones_internas = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones solo visibles para administradores"
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscripciones_creadas'
    )

    class Meta:
        db_table = 'deportes_inscripciones'
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        ordering = ['-fecha_inscripcion']
        indexes = [
            models.Index(fields=['persona', 'estado']),
            models.Index(fields=['grupo_horario', 'estado']),
            models.Index(fields=['fecha_inscripcion']),
        ]

    def __str__(self):
        return f"{self.persona.nombre_completo()} - {self.grupo_horario}"

    def get_descuento_total(self):
        """Calcula el descuento total aplicable"""
        descuento = self.porcentaje_descuento_adicional

        if self.beca and self.beca_aprobada:
            descuento += self.beca.porcentaje_descuento

        # El descuento no puede superar el 100%
        return min(descuento, 100)

    def get_arancel_base(self):
        """Obtiene el arancel base según si es socio o no"""
        return self.grupo_horario.get_arancel_para_persona(self.persona)

    def get_arancel_con_descuento(self):
        """Calcula el arancel final con descuentos aplicados"""
        arancel_base = self.get_arancel_base()
        descuento_total = self.get_descuento_total()

        monto_descuento = arancel_base * (descuento_total / 100)
        return arancel_base - monto_descuento

    def es_socio(self):
        """Verifica si la persona inscripta es socio activo"""
        try:
            return Socio.objects.filter(persona=self.persona, activo=True).exists()
        except:
            return False

    def necesita_renovar_apto_medico(self):
        """Verifica si necesita renovar el apto médico"""
        if not self.grupo_horario.categoria.disciplina.requiere_apto_medico:
            return False

        if not self.apto_medico_presentado:
            return True

        if self.apto_medico_vencimiento:
            return self.apto_medico_vencimiento < timezone.now().date()

        return False

    def aprobar(self, usuario=None):
        """Aprueba la inscripción"""
        self.estado = 'ACTIVA'
        if usuario:
            self.created_by = usuario
        self.save()

    def dar_de_baja(self, motivo=None):
        """Da de baja la inscripción"""
        self.estado = 'BAJA'
        self.fecha_baja = timezone.now().date()
        if motivo:
            self.observaciones_internas = f"{self.observaciones_internas or ''}\nBaja: {motivo}"
        self.save()

    def aprobar_beca(self, usuario):
        """Aprueba la beca solicitada"""
        if self.beca:
            self.beca_aprobada = True
            self.beca_aprobada_por = usuario
            self.beca_aprobada_fecha = timezone.now()
            self.save()


# ============================================
# 5. HISTORIAL DE CAMBIOS
# ============================================

class InscripcionHistorial(models.Model):
    """Historial de cambios en inscripciones"""

    ACCION_CHOICES = [
        ('ALTA', 'Alta'),
        ('MODIFICACION', 'Modificación'),
        ('BAJA', 'Baja'),
        ('SUSPENSION', 'Suspensión'),
        ('REACTIVACION', 'Reactivación'),
        ('BECA_SOLICITADA', 'Beca Solicitada'),
        ('BECA_APROBADA', 'Beca Aprobada'),
        ('BECA_RECHAZADA', 'Beca Rechazada'),
    ]

    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    descripcion = models.TextField()

    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deportes_inscripciones_historial'
        verbose_name = 'Historial de Inscripción'
        verbose_name_plural = 'Historial de Inscripciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.inscripcion} - {self.get_accion_display()} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"


# ============================================
# 6. PAGOS DE ACTIVIDADES
# ============================================

class PagoActividad(models.Model):
    """Pagos mensuales de actividades deportivas"""

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('VENCIDO', 'Vencido'),
        ('CANCELADO', 'Cancelado'),
    ]

    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='pagos'
    )

    # Período
    mes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    anio = models.PositiveIntegerField()

    # Montos
    monto_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    monto_descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    monto_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # Estado y fechas
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)

    # Relación con recibo (si existe módulo de facturación)
    # recibo = models.ForeignKey('facturacion.Recibo', null=True, blank=True)

    observaciones = models.TextField(blank=True, null=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deportes_pagos'
        verbose_name = 'Pago de Actividad'
        verbose_name_plural = 'Pagos de Actividades'
        ordering = ['-anio', '-mes']
        unique_together = [['inscripcion', 'mes', 'anio']]
        indexes = [
            models.Index(fields=['estado', 'fecha_vencimiento']),
            models.Index(fields=['inscripcion', 'estado']),
        ]

    def __str__(self):
        return f"{self.inscripcion.persona.nombre_completo()} - {self.mes}/{self.anio} - ${self.monto_final}"

    def marcar_como_pagado(self, fecha=None):
        """Marca el pago como pagado"""
        self.estado = 'PAGADO'
        self.fecha_pago = fecha or timezone.now().date()
        self.save()

    def esta_vencido(self):
        """Verifica si el pago está vencido"""
        if self.estado == 'PAGADO':
            return False
        return self.fecha_vencimiento < timezone.now().date()