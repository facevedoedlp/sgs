from django.db import models


class SociosEstado(models.Model):
    socioestadoid = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    vigente = models.BooleanField(default=True)
    indica_socio_activo = models.BooleanField(default=False)

    class Meta:
        db_table = 'socios_estado'
        managed = True  # ← CAMBIAR A TRUE

    def __str__(self):
        return self.descripcion


class CategoriaSocio(models.Model):
    categoriasocioid = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'categorias_socio'
        managed = True  # ← CAMBIAR A TRUE

    def __str__(self):
        return self.descripcion


class Filial(models.Model):
    filialid = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    domicilio = models.CharField(max_length=300, blank=True)
    vigente = models.BooleanField(default=True)

    class Meta:
        db_table = 'filiales'
        managed = True

    def __str__(self):
        return self.descripcion


class SociosHistoriaAccion(models.Model):
    accionid = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = 'socios_historia_accion'
        managed = True
        verbose_name = 'Acción'
        verbose_name_plural = 'Acciones'

    def __str__(self):
        return self.descripcion