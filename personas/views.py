from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Persona, DomicilioPersona, EmailPersona, TelefonoPersona
from .serializers import (
    PersonaSerializer,
    PersonaCreateSerializer,
    DomicilioPersonaSerializer,
    EmailPersonaSerializer,
    TelefonoPersonaSerializer
)


class PersonaViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gestión de personas"""
    queryset = Persona.objects.prefetch_related('domicilios', 'emails', 'telefonos').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PersonaCreateSerializer
        return PersonaSerializer


class DomicilioPersonaViewSet(viewsets.ModelViewSet):
    queryset = DomicilioPersona.objects.select_related('persona').all()
    serializer_class = DomicilioPersonaSerializer
    permission_classes = [IsAuthenticated]


class EmailPersonaViewSet(viewsets.ModelViewSet):
    queryset = EmailPersona.objects.select_related('persona').all()
    serializer_class = EmailPersonaSerializer
    permission_classes = [IsAuthenticated]


class TelefonoPersonaViewSet(viewsets.ModelViewSet):
    queryset = TelefonoPersona.objects.select_related('persona').all()
    serializer_class = TelefonoPersonaSerializer
    permission_classes = [IsAuthenticated]