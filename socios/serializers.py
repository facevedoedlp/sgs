from rest_framework import serializers
from .models import Socio, SocioEstado, CategoriaSocio
from personas.serializers import PersonaSerializer


class SocioEstadoSerializer(serializers.ModelSerializer):
    """Serializer para estados de socio"""

    class Meta:
        model = SocioEstado
        fields = '__all__'


class CategoriaSocioSerializer(serializers.ModelSerializer):
    """Serializer para categorías de socio"""

    class Meta:
        model = CategoriaSocio
        fields = '__all__'


class SocioSerializer(serializers.ModelSerializer):
    """Serializer de lectura completo para socios"""
    persona = PersonaSerializer(source='personaid', read_only=True)
    estado = SocioEstadoSerializer(source='socioestadoid', read_only=True)
    categoria = CategoriaSocioSerializer(source='categoriasocioid', read_only=True)

    # Campos calculados
    nombre_completo = serializers.SerializerMethodField()
    estado_nombre = serializers.CharField(source='socioestadoid.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoriasocioid.nombre', read_only=True)

    class Meta:
        model = Socio
        fields = [
            'personaid',
            'legajo',
            'nrosocio_sas',
            'nrosocio',
            'fecha_alta',
            'socioestadoid',
            'categoriasocioid',
            'filialid',
            'tipoexcepcionid',
            'descuento_antiguedad_meses',
            'recomendado_por',
            'socio_minuto',
            'socio_leon_america',
            'socio_leon_patria',
            'socio_leon_mundo',
            # Relaciones expandidas
            'persona',
            'estado',
            'categoria',
            # Campos calculados
            'nombre_completo',
            'estado_nombre',
            'categoria_nombre'
        ]

    def get_nombre_completo(self, obj):
        """Retorna el nombre completo de la persona"""
        if obj.personaid:
            return obj.personaid.nombre_completo()
        return None


class SocioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    nombre_completo = serializers.SerializerMethodField()
    estado_nombre = serializers.CharField(source='socioestadoid.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoriasocioid.nombre', read_only=True)

    class Meta:
        model = Socio
        fields = [
            'personaid',
            'nrosocio',
            'legajo',
            'nombre_completo',
            'estado_nombre',
            'categoria_nombre',
            'fecha_alta'
        ]

    def get_nombre_completo(self, obj):
        """Retorna el nombre completo de la persona"""
        if obj.personaid:
            return obj.personaid.nombre_completo()
        return None


class SocioCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar socios"""

    class Meta:
        model = Socio
        fields = [
            'personaid',
            'legajo',
            'nrosocio_sas',
            'nrosocio',
            'fecha_alta',
            'socioestadoid',
            'categoriasocioid',
            'filialid',
            'tipoexcepcionid',
            'descuento_antiguedad_meses',
            'recomendado_por',
            'socio_minuto',
            'socio_leon_america',
            'socio_leon_patria',
            'socio_leon_mundo'
        ]

    def validate_nrosocio(self, value):
        """Validar que el número de socio no esté duplicado"""
        if value:
            if self.instance:  # Es un update
                if Socio.objects.exclude(personaid=self.instance.personaid).filter(nrosocio=value).exists():
                    raise serializers.ValidationError("Este número de socio ya existe")
            else:  # Es un create
                if Socio.objects.filter(nrosocio=value).exists():
                    raise serializers.ValidationError("Este número de socio ya existe")
        return value

    def validate_personaid(self, value):
        """Validar que la persona no sea ya un socio"""
        if self.instance is None:  # Solo en create
            if Socio.objects.filter(personaid=value).exists():
                raise serializers.ValidationError("Esta persona ya es socio")
        return value

# TODO: Estos modelos serán implementados en el futuro
# class SocioGrupoFamiliarMiembroSerializer(serializers.ModelSerializer):
#     pass
#
# class SocioGrupoFamiliarSerializer(serializers.ModelSerializer):
#     pass
#
# class AcompananteSerializer(serializers.ModelSerializer):
#     pass
#
# class SocioDiscapacidadSerializer(serializers.ModelSerializer):
#     pass
#
# class SocioDomicilioPagoSasSerializer(serializers.ModelSerializer):
#     pass