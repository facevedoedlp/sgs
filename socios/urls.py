from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SocioViewSet,
    SocioGrupoFamiliarViewSet,
    SocioDiscapacidadViewSet,
    SocioDomicilioPagoSasViewSet
)

router = DefaultRouter()
router.register(r'socios', SocioViewSet, basename='socio')
router.register(r'grupos-familiares', SocioGrupoFamiliarViewSet, basename='grupo-familiar')
router.register(r'discapacidad', SocioDiscapacidadViewSet, basename='discapacidad')
router.register(r'domicilios-pago', SocioDomicilioPagoSasViewSet, basename='domicilio-pago')

urlpatterns = [
    path('', include(router.urls)),
]