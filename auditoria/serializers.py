from rest_framework import serializers
from .models import SocioHistoria


class SocioHistoriaSerializer(serializers.ModelSerializer):
    socio_numero = serializers.CharField(source='socio.numero_socio', read_only=True)
    socio_nombre = serializers.CharField(source='socio.persona.nombre_completo', read_only=True)
    accion_descripcion = serializers.CharField(source='accion.descripcion', read_only=True)
    estado_descripcion = serializers.CharField(source='estado.descripcion', read_only=True)
    categoria_descripcion = serializers.CharField(source='categoria.descripcion', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SocioHistoria
        fields = '__all__'

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.username
        return None