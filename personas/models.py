"""
Modelos del módulo Personas - Compatible con PostgreSQL existente
Sistema de Gestión de Socios - Club Estudiantes de La Plata

IMPORTANTE: Estos modelos coinciden EXACTAMENTE con las tablas PostgreSQL existentes
"""

from django.db import models


class Persona(models.Model):
    """
    Modelo Persona - Mapea a tabla 'personas' existente en PostgreSQL
    """

    # Primary Key
    personaid = models.BigAutoField(
        primary_key=True,
        db_column='personaid'
    )

    # Datos básicos
    apellido = models.TextField(
        blank=True,
        null=True,
        db_column='apellido'
    )

    nombre = models.TextField(
        blank=True,
        null=True,
        db_column='nombre'
    )

    # Documentación
    documento = models.TextField(
        blank=True,
        null=True,
        db_column='documento'
    )

    tipodocumentoid = models.IntegerField(
        blank=True,
        null=True,
        db_column='tipodocumentoid',
        verbose_name='Tipo de Documento'
    )

    cuil = models.TextField(
        blank=True,
        null=True,
        db_column='cuil',
        verbose_name='CUIL'
    )

    # Fechas
    fechanacimiento = models.DateTimeField(
        blank=True,
        null=True,
        db_column='fechanacimiento',
        verbose_name='Fecha de Nacimiento'
    )

    fechafallecimiento = models.DateField(
        blank=True,
        null=True,
        db_column='fechafallecimiento',
        verbose_name='Fecha de Fallecimiento'
    )

    # Catálogos (Foreign Keys como Integer por ahora)
    sexoid = models.IntegerField(
        blank=True,
        null=True,
        default=4,
        db_column='sexoid',
        verbose_name='Sexo'
    )

    estadocivilid = models.IntegerField(
        blank=True,
        null=True,
        db_column='estadocivilid',
        verbose_name='Estado Civil'
    )

    paisid = models.IntegerField(
        blank=True,
        null=True,
        db_column='paisid',
        verbose_name='País'
    )

    profesionid = models.IntegerField(
        blank=True,
        null=True,
        db_column='profesionid',
        verbose_name='Profesión'
    )

    # Otros campos
    notas = models.TextField(
        blank=True,
        null=True,
        db_column='notas',
        verbose_name='Notas'
    )

    sendrecibos = models.BooleanField(
        default=False,
        db_column='sendrecibos',
        verbose_name='Enviar Recibos'
    )

    class Meta:
        db_table = 'personas'
        managed = False  # ← IMPORTANTE: No modificar tabla existente
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        nombre = self.nombre or ''
        apellido = self.apellido or ''
        return f"{apellido}, {nombre}".strip(', ')

    def nombre_completo(self):
        """Retorna nombre completo: Nombre Apellido"""
        nombre = self.nombre or ''
        apellido = self.apellido or ''
        return f"{nombre} {apellido}".strip()

    def edad(self):
        """Calcula la edad de la persona"""
        if not self.fechanacimiento:
            return None

        from datetime import date
        hoy = date.today()
        fecha_nac = self.fechanacimiento.date() if hasattr(self.fechanacimiento, 'date') else self.fechanacimiento

        edad = hoy.year - fecha_nac.year
        if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
            edad -= 1

        return edad

    def email_principal(self):
        """Retorna el email principal"""
        try:
            return self.emails.filter(principal=True).first().email
        except:
            return self.emails.first().email if self.emails.exists() else None

    def telefono_principal(self):
        """Retorna el teléfono principal"""
        try:
            tel = self.telefonos.filter(principal=True).first()
            if not tel:
                tel = self.telefonos.first()

            if tel:
                if tel.caracteristica:
                    return f"{tel.caracteristica} {tel.numero}"
                return tel.numero
        except:
            return None

    def domicilio_principal(self):
        """Retorna el domicilio principal"""
        try:
            return self.domicilios.filter(principal=True).first()
        except:
            return self.domicilios.first() if self.domicilios.exists() else None


class DomicilioPersona(models.Model):
    """
    Domicilios de personas
    """
    domiciliopersonaid = models.BigAutoField(
        primary_key=True,
        db_column='domiciliopersonaid'
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='domicilios',
        db_column='personaid'
    )

    calle = models.CharField(
        max_length=200,
        blank=True,
        db_column='calle'
    )

    numero = models.CharField(
        max_length=10,
        blank=True,
        db_column='numero'
    )

    piso = models.CharField(
        max_length=10,
        blank=True,
        db_column='piso'
    )

    departamento = models.CharField(
        max_length=10,
        blank=True,
        db_column='departamento'
    )

    codigo_postal = models.CharField(
        max_length=10,
        blank=True,
        db_column='codigo_postal'
    )

    localidad = models.CharField(
        max_length=100,
        blank=True,
        db_column='localidad'
    )

    provincia = models.CharField(
        max_length=100,
        blank=True,
        db_column='provincia'
    )

    principal = models.BooleanField(
        default=False,
        db_column='principal'
    )

    class Meta:
        db_table = 'domicilios_persona'
        managed = False  # ← No modificar tabla existente
        verbose_name = 'Domicilio'
        verbose_name_plural = 'Domicilios'

    def __str__(self):
        partes = []
        if self.calle:
            partes.append(self.calle)
        if self.numero:
            partes.append(self.numero)
        if self.localidad:
            partes.append(self.localidad)

        return ' '.join(partes) if partes else 'Sin dirección'


class EmailPersona(models.Model):
    """
    Emails de personas
    """
    emailpersonaid = models.BigAutoField(
        primary_key=True,
        db_column='emailpersonaid'
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='emails',
        db_column='personaid'
    )

    email = models.EmailField(
        max_length=200,
        db_column='email'
    )

    principal = models.BooleanField(
        default=False,
        db_column='principal'
    )

    validado = models.BooleanField(
        default=False,
        db_column='validado'
    )

    class Meta:
        db_table = 'emails_persona'
        managed = False  # ← No modificar tabla existente
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def __str__(self):
        return self.email


class TelefonoPersona(models.Model):
    """
    Teléfonos de personas
    """
    telefonopersonaid = models.BigAutoField(
        primary_key=True,
        db_column='telefonopersonaid'
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.CASCADE,
        related_name='telefonos',
        db_column='personaid'
    )

    numero = models.CharField(
        max_length=50,
        db_column='numero'
    )

    tipo = models.CharField(
        max_length=20,
        blank=True,
        default='Celular',
        db_column='tipo'
    )

    caracteristica = models.CharField(
        max_length=10,
        blank=True,
        db_column='caracteristica'
    )

    principal = models.BooleanField(
        default=False,
        db_column='principal'
    )

    class Meta:
        db_table = 'telefonos_persona'
        managed = False  # ← No modificar tabla existente
        verbose_name = 'Teléfono'
        verbose_name_plural = 'Teléfonos'

    def __str__(self):
        if self.caracteristica:
            return f"({self.caracteristica}) {self.numero}"
        return self.numero