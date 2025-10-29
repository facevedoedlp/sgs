from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocioViewSet, SocioEstadoViewSet, CategoriaSocioViewSet

router = DefaultRouter()
router.register(r'socios', SocioViewSet, basename='socio')
router.register(r'estados', SocioEstadoViewSet, basename='socio-estado')
router.register(r'categorias', CategoriaSocioViewSet, basename='categoria-socio')

urlpatterns = [
    path('', include(router.urls)),
]