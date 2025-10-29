from django.db import models
from personas.models import Persona
from catalogos.models import SociosEstado, CategoriaSocio, Filial


class Socio(models.Model):
    persona = models.OneToOneField(
        Persona,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='personaid'
    )
    estado = models.ForeignKey(
        SociosEstado,
        on_delete=models.PROTECT,
        db_column='socioestadoid'
    )
    categoria = models.ForeignKey(
        CategoriaSocio,
        on_delete=models.PROTECT,
        db_column='categoriasocioid'
    )
    filial = models.ForeignKey(
        Filial,
        on_delete=models.PROTECT,
        db_column='filialid',
        null=True,
        blank=True
    )

    numero_socio = models.CharField(max_length=50, blank=True)
    fecha_alta = models.DateField()

    class Meta:
        db_table = 'socios'
        managed = True

    def __str__(self):
        return f"{self.numero_socio} - {self.persona}"


class SocioGrupoFamiliar(models.Model):
    grupofamiliarid = models.BigAutoField(primary_key=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'socios_grupo_familiar'
        managed = True
        verbose_name = 'Grupo Familiar'
        verbose_name_plural = 'Grupos Familiares'

    def __str__(self):
        return f"Grupo Familiar #{self.grupofamiliarid}"

    @property
    def cantidad_miembros(self):
        return self.miembros.count()

    @property
    def socio_titular(self):
        """Retorna el socio titular del grupo"""
        titular = self.miembros.filter(es_titular=True).first()
        return titular.socio if titular else None


class SocioGrupoFamiliarMiembro(models.Model):
    grupofamiliarmiembroid = models.BigAutoField(primary_key=True)

    grupo_familiar = models.ForeignKey(
        SocioGrupoFamiliar,
        on_delete=models.CASCADE,
        db_column='grupofamiliarid',
        related_name='miembros'
    )

    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        db_column='personaid',
        related_name='grupos_familiares'
    )

    es_titular = models.BooleanField(default=False)
    fecha_alta = models.DateField()
    fecha_baja = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'socios_grupo_familiar_miembros'
        managed = True
        verbose_name = 'Miembro de Grupo Familiar'
        verbose_name_plural = 'Miembros de Grupos Familiares'
        unique_together = [['grupo_familiar', 'socio']]  # Un socio no puede estar 2 veces en el mismo grupo

    def __str__(self):
        titular = "👑 Titular" if self.es_titular else "Adherente"
        return f"{self.socio.numero_socio} - {self.socio.persona.nombre_completo} ({titular})"


class SocioDiscapacidad(models.Model):
    socio = models.OneToOneField(
        Socio,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='personaid',
        related_name='discapacidad'
    )

    numero_certificado = models.CharField(max_length=100, blank=True)
    tipo_discapacidad = models.CharField(max_length=200, blank=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField(null=True, blank=True)
    auditor_responsable = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'socios_discapacidad'
        managed = True
        verbose_name = 'Certificado de Discapacidad'
        verbose_name_plural = 'Certificados de Discapacidad'

    def __str__(self):
        return f"Certificado {self.numero_certificado} - {self.socio}"

    @property
    def esta_vigente(self):
        """Verifica si el certificado está vigente"""
        from datetime import date
        if self.fecha_hasta:
            return self.fecha_desde <= date.today() <= self.fecha_hasta
        return self.fecha_desde <= date.today()


class SocioDiscapacidadAcompanante(models.Model):
    acompananteid = models.BigAutoField(primary_key=True)

    socio_discapacidad = models.ForeignKey(
        SocioDiscapacidad,
        on_delete=models.CASCADE,
        db_column='personaid',
        related_name='acompanantes'
    )

    apellido = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    documento = models.CharField(max_length=20)
    tipo_documento = models.CharField(max_length=20, blank=True, default='DNI')
    vinculo = models.CharField(max_length=100, blank=True)  # Padre, Madre, Hermano, Cuidador, etc.
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'socios_discapacidad_acompanantes'
        managed = True
        verbose_name = 'Acompañante'
        verbose_name_plural = 'Acompañantes'

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.vinculo})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class SocioDomicilioPagoSas(models.Model):
    socio = models.OneToOneField(
        Socio,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='personaid',
        related_name='domicilio_pago_sas'
    )

    calle = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=10, blank=True)
    piso = models.CharField(max_length=10, blank=True)
    departamento = models.CharField(max_length=10, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, blank=True, default='Argentina')

    class Meta:
        db_table = 'socios_domicilio_pago_sas'
        managed = True
        verbose_name = 'Domicilio de Pago SAS'
        verbose_name_plural = 'Domicilios de Pago SAS'

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.localidad}"

    @property
    def direccion_completa(self):
        partes = [f"{self.calle} {self.numero}"]
        if self.piso:
            partes.append(f"Piso {self.piso}")
        if self.departamento:
            partes.append(f"Dto {self.departamento}")
        partes.append(self.localidad)
        if self.codigo_postal:
            partes.append(f"(CP: {self.codigo_postal})")
        return ", ".join(filter(None, partes))