from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonaViewSet,
    DomicilioPersonaViewSet,
    EmailPersonaViewSet,
    TelefonoPersonaViewSet
)

router = DefaultRouter()
router.register(r'personas', PersonaViewSet, basename='persona')
router.register(r'domicilios', DomicilioPersonaViewSet, basename='domicilio')
router.register(r'emails', EmailPersonaViewSet, basename='email')
router.register(r'telefonos', TelefonoPersonaViewSet, basename='telefono')

urlpatterns = [
    path('', include(router.urls)),
]