from rest_framework import serializers
from .models import Persona, DomicilioPersona, EmailPersona, TelefonoPersona


class DomicilioPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomicilioPersona
        fields = '__all__'
        read_only_fields = ['persona']


class EmailPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPersona
        fields = '__all__'
        read_only_fields = ['persona']


class TelefonoPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelefonoPersona
        fields = '__all__'
        read_only_fields = ['persona']


class PersonaSerializer(serializers.ModelSerializer):
    """Serializer de lectura"""
    domicilios = DomicilioPersonaSerializer(many=True, read_only=True)
    emails = EmailPersonaSerializer(many=True, read_only=True)
    telefonos = TelefonoPersonaSerializer(many=True, read_only=True)
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Persona
        fields = '__all__'


class PersonaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear persona con contactos anidados"""
    domicilios = DomicilioPersonaSerializer(many=True, required=False)
    emails = EmailPersonaSerializer(many=True, required=False)
    telefonos = TelefonoPersonaSerializer(many=True, required=False)

    class Meta:
        model = Persona
        fields = ['apellido', 'nombre', 'documento', 'fecha_nacimiento', 'domicilios', 'emails', 'telefonos']

    def create(self, validated_data):
        domicilios_data = validated_data.pop('domicilios', [])
        emails_data = validated_data.pop('emails', [])
        telefonos_data = validated_data.pop('telefonos', [])

        persona = Persona.objects.create(**validated_data)

        # Crear domicilios
        for domicilio_data in domicilios_data:
            DomicilioPersona.objects.create(persona=persona, **domicilio_data)

        # Crear emails
        for email_data in emails_data:
            EmailPersona.objects.create(persona=persona, **email_data)

        # Crear teléfonos
        for telefono_data in telefonos_data:
            TelefonoPersona.objects.create(persona=persona, **telefono_data)

        return persona