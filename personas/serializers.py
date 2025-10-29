from rest_framework import serializers
from .models import Persona, DomicilioPersona, EmailPersona, TelefonoPersona


class DomicilioPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomicilioPersona
        fields = '__all__'
        read_only_fields = ['personaid']


class EmailPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPersona
        fields = '__all__'
        read_only_fields = ['personaid']


class TelefonoPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelefonoPersona
        fields = '__all__'
        read_only_fields = ['personaid']


class PersonaSerializer(serializers.ModelSerializer):
    """Serializer de lectura"""
    domicilios = DomicilioPersonaSerializer(many=True, read_only=True)
    emails = EmailPersonaSerializer(many=True, read_only=True)
    telefonos = TelefonoPersonaSerializer(many=True, read_only=True)

    # Campos calculados - SIN source porque el método se llama igual
    nombre_completo = serializers.SerializerMethodField()
    edad = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = [
            'personaid',
            'apellido',
            'nombre',
            'documento',
            'tipodocumentoid',
            'cuil',
            'fechanacimiento',
            'fechafallecimiento',
            'sexoid',
            'estadocivilid',
            'paisid',
            'profesionid',
            'notas',
            'sendrecibos',
            'nombre_completo',
            'edad',
            'domicilios',
            'emails',
            'telefonos'
        ]

    def get_nombre_completo(self, obj):
        """Retorna el nombre completo"""
        return obj.nombre_completo()

    def get_edad(self, obj):
        """Retorna la edad"""
        return obj.edad()


class PersonaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear persona con contactos anidados"""
    domicilios = DomicilioPersonaSerializer(many=True, required=False)
    emails = EmailPersonaSerializer(many=True, required=False)
    telefonos = TelefonoPersonaSerializer(many=True, required=False)

    class Meta:
        model = Persona
        fields = [
            'apellido',
            'nombre',
            'documento',
            'tipodocumentoid',
            'cuil',
            'fechanacimiento',
            'fechafallecimiento',
            'sexoid',
            'estadocivilid',
            'paisid',
            'profesionid',
            'notas',
            'sendrecibos',
            'domicilios',
            'emails',
            'telefonos'
        ]

    def create(self, validated_data):
        domicilios_data = validated_data.pop('domicilios', [])
        emails_data = validated_data.pop('emails', [])
        telefonos_data = validated_data.pop('telefonos', [])

        persona = Persona.objects.create(**validated_data)

        # Crear domicilios
        for domicilio_data in domicilios_data:
            DomicilioPersona.objects.create(personaid=persona, **domicilio_data)

        # Crear emails
        for email_data in emails_data:
            EmailPersona.objects.create(personaid=persona, **email_data)

        # Crear teléfonos
        for telefono_data in telefonos_data:
            TelefonoPersona.objects.create(personaid=persona, **telefono_data)

        return persona