from django.db import models
from personas.models import Persona


class SocioEstado(models.Model):
    """Estados de socio"""
    socioestadoid = models.BigAutoField(primary_key=True, db_column='socioestadoid')
    nombre = models.CharField(max_length=100, db_column='nombre')
    habilitado = models.BooleanField(default=True, db_column='habilitado')
    visible = models.BooleanField(default=True, db_column='visible')

    class Meta:
        db_table = 'socio_estados'
        managed = False
        verbose_name = 'Estado de Socio'
        verbose_name_plural = 'Estados de Socio'

    def __str__(self):
        return self.nombre


class CategoriaSocio(models.Model):
    """Categorías de socio"""
    categoriasocioid = models.AutoField(primary_key=True, db_column='categoriasocioid')
    created_at = models.DateTimeField(blank=True, null=True, db_column='created_at')
    deleted_at = models.DateTimeField(blank=True, null=True, db_column='deleted_at')
    grupo = models.IntegerField(blank=True, null=True, db_column='grupo')
    nombre = models.CharField(max_length=200, blank=True, null=True, db_column='nombre')
    habilita_grupo_familiar = models.BooleanField(blank=True, null=True, db_column='habilita_grupo_familiar')
    habilita_acceso_instalaciones = models.BooleanField(blank=True, null=True,
                                                        db_column='habilita_acceso_instalaciones')
    tiene_vencimiento = models.BooleanField(blank=True, null=True, db_column='tiene_vencimiento')
    alias = models.CharField(max_length=100, blank=True, null=True, db_column='alias')
    requiere_pago = models.BooleanField(blank=True, null=True, db_column='requiere_pago')
    habilita_plateas = models.BooleanField(blank=True, null=True, db_column='habilita_plateas')
    orden = models.IntegerField(blank=True, null=True, db_column='orden')

    class Meta:
        db_table = 'categoria_socio'
        managed = False
        verbose_name = 'Categoría de Socio'
        verbose_name_plural = 'Categorías de Socio'
        ordering = ['orden']

    def __str__(self):
        return self.nombre or f"Categoría {self.categoriasocioid}"


class Socio(models.Model):
    """Socios del club"""
    personaid = models.OneToOneField(
        Persona,
        primary_key=True,
        on_delete=models.CASCADE,
        db_column='personaid',
        related_name='socio'
    )
    legajo = models.TextField(blank=True, null=True, db_column='legajo')
    nrosocio_sas = models.TextField(blank=True, null=True, db_column='nrosocio_sas')
    fecha_alta = models.DateField(blank=True, null=True, db_column='fecha_alta')
    socioestadoid = models.ForeignKey(
        SocioEstado,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='socioestadoid',
        related_name='socios'
    )
    nrosocio = models.BigIntegerField(blank=True, null=True, db_column='nrosocio')
    categoriasocioid = models.ForeignKey(
        CategoriaSocio,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='categoriasocioid',
        related_name='socios'
    )
    filialid = models.IntegerField(blank=True, null=True, db_column='filialid')
    tipoexcepcionid = models.IntegerField(blank=True, null=True, db_column='tipoexcepcionid')
    descuento_antiguedad_meses = models.IntegerField(blank=True, null=True, db_column='descuento_antiguedad_meses')
    recomendado_por = models.BigIntegerField(blank=True, null=True, db_column='recomendado_por')
    socio_minuto = models.BooleanField(default=False, db_column='socio_minuto')
    socio_leon_america = models.BooleanField(default=False, db_column='socio_leon_america')
    socio_leon_patria = models.BooleanField(default=False, db_column='socio_leon_patria')
    socio_leon_mundo = models.BooleanField(default=False, db_column='socio_leon_mundo')

    class Meta:
        db_table = 'socios'
        managed = False
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'

    def __str__(self):
        return f"Socio {self.nrosocio} - {self.personaid}"