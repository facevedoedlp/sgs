"""
URLs para el módulo de Deportes
Sistema de Gestión de Socios - Club Estudiantes de La Plata
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LugarViewSet, FrecuenciaViewSet, TipoBecaViewSet,
    DisciplinaViewSet, CategoriaViewSet, GrupoHorarioViewSet,
    InscripcionViewSet, PagoActividadViewSet
)

# Router para las APIs REST
router = DefaultRouter()
router.register(r'lugares', LugarViewSet, basename='lugar')
router.register(r'frecuencias', FrecuenciaViewSet, basename='frecuencia')
router.register(r'tipos-beca', TipoBecaViewSet, basename='tipo-beca')
router.register(r'disciplinas', DisciplinaViewSet, basename='disciplina')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'grupos-horarios', GrupoHorarioViewSet, basename='grupo-horario')
router.register(r'inscripciones', InscripcionViewSet, basename='inscripcion')
router.register(r'pagos', PagoActividadViewSet, basename='pago-actividad')

app_name = 'deportes'

urlpatterns = [
    path('', include(router.urls)),
]