"""
Serializers para el módulo de Deportes
Sistema de Gestión de Socios - Club Estudiantes de La Plata
"""

from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Lugar, Frecuencia, TipoBeca, Disciplina, Categoria,
    GrupoHorario, Inscripcion, InscripcionHistorial, PagoActividad
)
from personas.models import Persona


# ============================================
# SERIALIZERS DE CATÁLOGOS
# ============================================

class LugarSerializer(serializers.ModelSerializer):
    """Serializer para Lugares"""

    class Meta:
        model = Lugar
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class FrecuenciaSerializer(serializers.ModelSerializer):
    """Serializer para Frecuencias"""
    dias_semana = serializers.SerializerMethodField()

    class Meta:
        model = Frecuencia
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_dias_semana(self, obj):
        return obj.get_dias_semana()


class TipoBecaSerializer(serializers.ModelSerializer):
    """Serializer para Tipos de Beca"""

    class Meta:
        model = TipoBeca
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# ============================================
# SERIALIZERS DE DISCIPLINAS Y CATEGORÍAS
# ============================================

class CategoriaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado de Categoría para listados"""

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'nivel', 'edad_desde', 'edad_hasta', 'activa']


class DisciplinaListSerializer(serializers.ModelSerializer):
    """Serializer para listado de Disciplinas"""
    total_categorias = serializers.SerializerMethodField()
    en_temporada = serializers.SerializerMethodField()

    class Meta:
        model = Disciplina
        fields = [
            'id', 'nombre', 'tipo_actividad', 'activa',
            'requiere_apto_medico', 'es_temporada',
            'total_categorias', 'en_temporada'
        ]

    def get_total_categorias(self, obj):
        return obj.categorias.filter(activa=True).count()

    def get_en_temporada(self, obj):
        return obj.en_temporada()


class DisciplinaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de Disciplina"""
    categorias = CategoriaListSerializer(many=True, read_only=True)
    en_temporada = serializers.SerializerMethodField()

    class Meta:
        model = Disciplina
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_en_temporada(self, obj):
        return obj.en_temporada()


class CategoriaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de Categoría"""
    disciplina = DisciplinaListSerializer(read_only=True)
    disciplina_id = serializers.PrimaryKeyRelatedField(
        queryset=Disciplina.objects.all(),
        source='disciplina',
        write_only=True
    )
    total_grupos = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_total_grupos(self, obj):
        return obj.grupos.filter(activo=True).count()


# ============================================
# SERIALIZERS DE GRUPOS Y HORARIOS
# ============================================

class InstructorSerializer(serializers.ModelSerializer):
    """Serializer para Usuario como Instructor"""
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'nombre_completo']

    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class GrupoHorarioListSerializer(serializers.ModelSerializer):
    """Serializer para listado de Grupos/Horarios"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    disciplina_nombre = serializers.CharField(source='categoria.disciplina.nombre', read_only=True)
    lugar_nombre = serializers.CharField(source='lugar.nombre', read_only=True)
    frecuencia_nombre = serializers.CharField(source='frecuencia.nombre', read_only=True)
    instructor_nombre = serializers.SerializerMethodField()
    inscriptos_count = serializers.SerializerMethodField()
    tiene_cupo = serializers.SerializerMethodField()

    class Meta:
        model = GrupoHorario
        fields = [
            'id', 'nombre', 'categoria_nombre', 'disciplina_nombre',
            'lugar_nombre', 'frecuencia_nombre', 'horario_inicio', 'horario_fin',
            'arancel_socio', 'arancel_no_socio', 'cupo_maximo',
            'inscriptos_count', 'tiene_cupo', 'instructor_nombre', 'activo'
        ]

    def get_instructor_nombre(self, obj):
        if obj.instructor:
            return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip() or obj.instructor.username
        return None

    def get_inscriptos_count(self, obj):
        return obj.get_inscriptos_count()

    def get_tiene_cupo(self, obj):
        return obj.tiene_cupo_disponible()


class GrupoHorarioDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de Grupo/Horario"""
    categoria = CategoriaDetailSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True
    )
    lugar = LugarSerializer(read_only=True)
    lugar_id = serializers.PrimaryKeyRelatedField(
        queryset=Lugar.objects.all(),
        source='lugar',
        write_only=True
    )
    frecuencia = FrecuenciaSerializer(read_only=True)
    frecuencia_id = serializers.PrimaryKeyRelatedField(
        queryset=Frecuencia.objects.all(),
        source='frecuencia',
        write_only=True
    )
    instructor = InstructorSerializer(read_only=True)
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='instructor',
        write_only=True,
        required=False,
        allow_null=True
    )
    inscriptos_count = serializers.SerializerMethodField()
    tiene_cupo = serializers.SerializerMethodField()

    class Meta:
        model = GrupoHorario
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_inscriptos_count(self, obj):
        return obj.get_inscriptos_count()

    def get_tiene_cupo(self, obj):
        return obj.tiene_cupo_disponible()


# ============================================
# SERIALIZERS DE INSCRIPCIONES
# ============================================

class PersonaBasicSerializer(serializers.ModelSerializer):
    """Serializer básico de Persona para inscripciones"""
    nombre_completo = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = ['personaid', 'nombre', 'apellido', 'nombre_completo', 'documento', 'email']

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()

    def get_email(self, obj):
        """Obtiene el email principal de la persona"""
        email_obj = obj.emails.filter(principal=True).first()
        return email_obj.email if email_obj else None


class InscripcionListSerializer(serializers.ModelSerializer):
    """Serializer para listado de Inscripciones"""
    persona = PersonaBasicSerializer(read_only=True)
    grupo_nombre = serializers.CharField(source='grupo_horario.nombre', read_only=True)
    disciplina_nombre = serializers.CharField(
        source='grupo_horario.categoria.disciplina.nombre',
        read_only=True
    )
    categoria_nombre = serializers.CharField(
        source='grupo_horario.categoria.nombre',
        read_only=True
    )
    arancel_base = serializers.SerializerMethodField()
    arancel_final = serializers.SerializerMethodField()
    descuento_total = serializers.SerializerMethodField()
    es_socio = serializers.SerializerMethodField()
    necesita_apto = serializers.SerializerMethodField()

    class Meta:
        model = Inscripcion
        fields = [
            'id', 'persona', 'grupo_nombre', 'disciplina_nombre', 'categoria_nombre',
            'estado', 'fecha_inscripcion', 'fecha_inicio', 'fecha_baja',
            'beca', 'beca_aprobada', 'arancel_base', 'arancel_final',
            'descuento_total', 'es_socio', 'necesita_apto'
        ]

    def get_arancel_base(self, obj):
        return float(obj.get_arancel_base())

    def get_arancel_final(self, obj):
        return float(obj.get_arancel_con_descuento())

    def get_descuento_total(self, obj):
        return float(obj.get_descuento_total())

    def get_es_socio(self, obj):
        return obj.es_socio()

    def get_necesita_apto(self, obj):
        return obj.necesita_renovar_apto_medico()


class InscripcionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de Inscripción"""
    persona = PersonaBasicSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(),
        source='persona',
        write_only=True
    )
    grupo_horario = GrupoHorarioDetailSerializer(read_only=True)
    grupo_horario_id = serializers.PrimaryKeyRelatedField(
        queryset=GrupoHorario.objects.all(),
        source='grupo_horario',
        write_only=True
    )
    beca_detail = TipoBecaSerializer(source='beca', read_only=True)
    beca_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoBeca.objects.all(),
        source='beca',
        write_only=True,
        required=False,
        allow_null=True
    )
    arancel_base = serializers.SerializerMethodField()
    arancel_final = serializers.SerializerMethodField()
    descuento_total = serializers.SerializerMethodField()
    es_socio = serializers.SerializerMethodField()
    necesita_apto = serializers.SerializerMethodField()
    beca_aprobada_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Inscripcion
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'created_by',
            'beca_aprobada_por', 'beca_aprobada_fecha'
        ]

    def get_arancel_base(self, obj):
        return float(obj.get_arancel_base())

    def get_arancel_final(self, obj):
        return float(obj.get_arancel_con_descuento())

    def get_descuento_total(self, obj):
        return float(obj.get_descuento_total())

    def get_es_socio(self, obj):
        return obj.es_socio()

    def get_necesita_apto(self, obj):
        return obj.necesita_renovar_apto_medico()

    def get_beca_aprobada_por_nombre(self, obj):
        if obj.beca_aprobada_por:
            return f"{obj.beca_aprobada_por.first_name} {obj.beca_aprobada_por.last_name}".strip()
        return None

    def validate(self, attrs):
        """Validaciones personalizadas"""
        grupo_horario = attrs.get('grupo_horario')

        # Verificar cupo disponible
        if grupo_horario and not grupo_horario.tiene_cupo_disponible():
            raise serializers.ValidationError({
                'grupo_horario': 'Este grupo no tiene cupo disponible'
            })

        # Verificar que fecha_inicio no sea anterior a hoy
        fecha_inicio = attrs.get('fecha_inicio')
        if fecha_inicio and fecha_inicio < timezone.now().date():
            raise serializers.ValidationError({
                'fecha_inicio': 'La fecha de inicio no puede ser anterior a hoy'
            })

        return attrs


class InscripcionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear inscripciones"""

    class Meta:
        model = Inscripcion
        fields = [
            'persona_id', 'grupo_horario_id', 'fecha_inicio',
            'beca_id', 'porcentaje_descuento_adicional',
            'apto_medico_presentado', 'apto_medico_vencimiento',
            'observaciones'
        ]

    def create(self, validated_data):
        # Agregar usuario que crea la inscripción
        validated_data['created_by'] = self.context['request'].user
        validated_data['estado'] = 'PENDIENTE'
        return super().create(validated_data)


# ============================================
# SERIALIZERS DE HISTORIAL
# ============================================

class InscripcionHistorialSerializer(serializers.ModelSerializer):
    """Serializer para Historial de Inscripciones"""
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = InscripcionHistorial
        fields = '__all__'
        read_only_fields = ['fecha']

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return f"{obj.usuario.first_name} {obj.usuario.last_name}".strip() or obj.usuario.username
        return "Sistema"


# ============================================
# SERIALIZERS DE PAGOS
# ============================================

class PagoActividadListSerializer(serializers.ModelSerializer):
    """Serializer para listado de Pagos"""
    persona_nombre = serializers.CharField(
        source='inscripcion.persona.nombre_completo',
        read_only=True
    )
    disciplina_nombre = serializers.CharField(
        source='inscripcion.grupo_horario.categoria.disciplina.nombre',
        read_only=True
    )
    esta_vencido = serializers.SerializerMethodField()

    class Meta:
        model = PagoActividad
        fields = [
            'id', 'persona_nombre', 'disciplina_nombre', 'mes', 'anio',
            'monto_final', 'estado', 'fecha_vencimiento', 'fecha_pago',
            'esta_vencido'
        ]

    def get_esta_vencido(self, obj):
        return obj.esta_vencido()


class PagoActividadDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado de Pago"""
    inscripcion_detail = InscripcionListSerializer(source='inscripcion', read_only=True)
    esta_vencido = serializers.SerializerMethodField()

    class Meta:
        model = PagoActividad
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_esta_vencido(self, obj):
        return obj.esta_vencido()


# ============================================
# SERIALIZERS DE ACCIONES
# ============================================

class AprobarBecaSerializer(serializers.Serializer):
    """Serializer para aprobar becas"""
    aprobar = serializers.BooleanField(default=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)


class DarDeBajaSerializer(serializers.Serializer):
    """Serializer para dar de baja inscripciones"""
    motivo = serializers.CharField(required=True, max_length=500)
    fecha_baja = serializers.DateField(required=False)


class MarcarPagoSerializer(serializers.Serializer):
    """Serializer para marcar pagos como pagados"""
    fecha_pago = serializers.DateField(required=False)
    observaciones = serializers.CharField(required=False, allow_blank=True)