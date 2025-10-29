from rest_framework import serializers
from .models import (
    Socio,
    SocioGrupoFamiliar,
    SocioGrupoFamiliarMiembro,
    SocioDiscapacidad,
    SocioDiscapacidadAcompanante,
    SocioDomicilioPagoSas
)
from personas.models import Persona
from personas.serializers import PersonaSerializer


# Serializers de lectura (GET)
class SocioGrupoFamiliarMiembroSerializer(serializers.ModelSerializer):
    socio_numero = serializers.CharField(source='socio.numero_socio', read_only=True)
    socio_nombre = serializers.CharField(source='socio.persona.nombre_completo', read_only=True)

    class Meta:
        model = SocioGrupoFamiliarMiembro
        fields = '__all__'


class SocioGrupoFamiliarSerializer(serializers.ModelSerializer):
    miembros = SocioGrupoFamiliarMiembroSerializer(many=True, read_only=True)
    socio_titular = serializers.SerializerMethodField()

    class Meta:
        model = SocioGrupoFamiliar
        fields = '__all__'

    def get_socio_titular(self, obj):
        titular = obj.socio_titular
        if titular:
            return {
                'numero_socio': titular.numero_socio,
                'nombre_completo': titular.persona.nombre_completo
            }
        return None


class AcompananteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocioDiscapacidadAcompanante
        fields = '__all__'


class SocioDiscapacidadSerializer(serializers.ModelSerializer):
    acompanantes = AcompananteSerializer(many=True, read_only=True)
    esta_vigente = serializers.BooleanField(read_only=True)

    class Meta:
        model = SocioDiscapacidad
        fields = '__all__'


class SocioDomicilioPagoSasSerializer(serializers.ModelSerializer):
    direccion_completa = serializers.CharField(read_only=True)

    class Meta:
        model = SocioDomicilioPagoSas
        fields = '__all__'


class SocioSerializer(serializers.ModelSerializer):
    """Serializer de lectura completo"""
    persona = PersonaSerializer(read_only=True)
    estado_descripcion = serializers.CharField(source='estado.descripcion', read_only=True)
    categoria_descripcion = serializers.CharField(source='categoria.descripcion', read_only=True)
    filial_descripcion = serializers.CharField(source='filial.descripcion', read_only=True)

    # Relaciones opcionales
    grupos_familiares = SocioGrupoFamiliarMiembroSerializer(many=True, read_only=True)
    discapacidad = SocioDiscapacidadSerializer(read_only=True)
    domicilio_pago_sas = SocioDomicilioPagoSasSerializer(read_only=True)

    class Meta:
        model = Socio
        fields = [
            'persona',
            'numero_socio',
            'estado',
            'estado_descripcion',
            'categoria',
            'categoria_descripcion',
            'filial',
            'filial_descripcion',
            'fecha_alta',
            'grupos_familiares',
            'discapacidad',
            'domicilio_pago_sas'
        ]


# Serializers de escritura (POST/PUT)
class SocioCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar socios"""

    class Meta:
        model = Socio
        fields = ['persona', 'numero_socio', 'estado', 'categoria', 'filial', 'fecha_alta']

    def validate_numero_socio(self, value):
        """Validar que el número de socio no esté duplicado"""
        if self.instance:  # Es un update
            if Socio.objects.exclude(pk=self.instance.pk).filter(numero_socio=value).exists():
                raise serializers.ValidationError("Este número de socio ya existe")
        else:  # Es un create
            if Socio.objects.filter(numero_socio=value).exists():
                raise serializers.ValidationError("Este número de socio ya existe")
        return value

    def validate_persona(self, value):
        """Validar que la persona no sea ya un socio"""
        if self.instance is None:  # Solo en create
            if Socio.objects.filter(persona=value).exists():
                raise serializers.ValidationError("Esta persona ya es socio")
        return value