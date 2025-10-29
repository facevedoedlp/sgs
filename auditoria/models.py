from django.db import models
from django.contrib.auth.models import User
from socios.models import Socio
from catalogos.models import SociosEstado, CategoriaSocio, SociosHistoriaAccion


class SocioHistoria(models.Model):
    sociohistoriaid = models.AutoField(primary_key=True)

    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        db_column='socioid',
        related_name='historial'
    )

    categoria = models.ForeignKey(
        CategoriaSocio,
        on_delete=models.PROTECT,
        db_column='categoriasocioid',
        null=True,
        blank=True
    )

    estado = models.ForeignKey(
        SociosEstado,
        on_delete=models.PROTECT,
        db_column='socioestadoid',
        null=True,
        blank=True
    )

    accion = models.ForeignKey(
        SociosHistoriaAccion,
        on_delete=models.PROTECT,
        db_column='accionid'
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_socios'
    )

    numero_socio = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'socios_historia'
        managed = True
        verbose_name = 'Historia de Socio'
        verbose_name_plural = 'Historias de Socios'
        ordering = ['-fecha_accion']

    def __str__(self):
        return f"{self.socio} - {self.accion} ({self.fecha_accion.strftime('%d/%m/%Y')})"