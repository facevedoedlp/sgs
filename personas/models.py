from django.db import models


class Persona(models.Model):
    personaid = models.BigAutoField(primary_key=True)
    apellido = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'personas'
        managed = True
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        """Retorna nombre completo en formato: Nombre Apellido"""
        return f"{self.nombre} {self.apellido}"


class DomicilioPersona(models.Model):
    domiciliopersonaid = models.BigAutoField(primary_key=True)
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='domicilios',
        db_column='personaid'
    )
    calle = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=10, blank=True)
    piso = models.CharField(max_length=10, blank=True)
    departamento = models.CharField(max_length=10, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'domicilios_persona'
        managed = True
        verbose_name = 'Domicilio'
        verbose_name_plural = 'Domicilios'

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.localidad}"


class EmailPersona(models.Model):
    emailpersonaid = models.BigAutoField(primary_key=True)
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='emails',
        db_column='personaid'
    )
    email = models.EmailField(max_length=200)
    principal = models.BooleanField(default=False)
    validado = models.BooleanField(default=False)

    class Meta:
        db_table = 'emails_persona'
        managed = True
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def __str__(self):
        return self.email


class TelefonoPersona(models.Model):
    telefonopersonaid = models.BigAutoField(primary_key=True)
    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='telefonos',
        db_column='personaid'
    )
    numero = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, blank=True, default='Celular')
    caracteristica = models.CharField(max_length=10, blank=True)
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'telefonos_persona'
        managed = True
        verbose_name = 'Teléfono'
        verbose_name_plural = 'Teléfonos'

    def __str__(self):
        if self.caracteristica:
            return f"{self.caracteristica} {self.numero}"
        return self.numero