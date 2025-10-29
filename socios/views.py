from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Socio, SocioEstado, CategoriaSocio
from .serializers import (
    SocioSerializer,
    SocioListSerializer,
    SocioEstadoSerializer,
    CategoriaSocioSerializer
)
from .filters import SocioFilter


class SocioEstadoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para estados de socio

    Endpoints:
    - GET /api/estados/ - Lista todos los estados
    - GET /api/estados/{id}/ - Detalle de un estado
    """
    queryset = SocioEstado.objects.all()
    serializer_class = SocioEstadoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['socioestadoid', 'nombre']
    ordering = ['socioestadoid']


class CategoriaSocioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para categorías de socio

    Endpoints:
    - GET /api/categorias/ - Lista todas las categorías
    - GET /api/categorias/{id}/ - Detalle de una categoría

    Filtros disponibles:
    - ?grupo=1 - Filtrar por grupo
    - ?search=activo - Buscar por nombre o alias
    """
    queryset = CategoriaSocio.objects.all()
    serializer_class = CategoriaSocioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'alias']
    filterset_fields = ['grupo']
    ordering_fields = ['orden', 'nombre', 'categoriasocioid']
    ordering = ['orden']


class SocioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para socios con filtros avanzados

    Endpoints:
    - GET /api/socios/ - Lista todos los socios (con filtros)
    - GET /api/socios/{id}/ - Detalle de un socio

    Filtros disponibles:
    ==================

    Búsqueda general:
    - ?buscar=juan - Busca en nombre, apellido, documento, nro socio, legajo

    Filtros específicos:
    - ?nombre=juan - Filtrar por nombre
    - ?apellido=perez - Filtrar por apellido
    - ?documento=12345678 - Filtrar por documento
    - ?legajo=ABC123 - Filtrar por legajo

    Filtros por número de socio:
    - ?nrosocio=12345 - Número exacto
    - ?nrosocio_desde=1000 - Desde número
    - ?nrosocio_hasta=2000 - Hasta número

    Filtros por fecha:
    - ?fecha_alta_desde=2020-01-01 - Desde fecha
    - ?fecha_alta_hasta=2023-12-31 - Hasta fecha
    - ?fecha_alta_anio=2022 - Por año específico

    Filtros por estado y categoría:
    - ?estado=2 - Un estado (puede repetir para múltiples: ?estado=2&estado=4)
    - ?categoria=1 - Una categoría (puede repetir para múltiples)

    Filtros booleanos:
    - ?socio_minuto=true
    - ?socio_leon_america=true
    - ?socio_leon_patria=true
    - ?socio_leon_mundo=true

    Ordenamiento:
    - ?ordering=nrosocio - Ascendente por número
    - ?ordering=-nrosocio - Descendente por número
    - ?ordering=personaid__apellido - Por apellido
    - ?ordering=-personaid__apellido - Por apellido desc
    - ?ordering=fecha_alta - Por fecha de alta
    - ?ordering=-fecha_alta - Por fecha de alta desc

    Paginación:
    - ?page=2 - Página 2
    - ?page_size=100 - Tamaño de página

    Ejemplos de uso:
    ================

    # Buscar socios vigentes
    GET /api/socios/?estado=2

    # Buscar por nombre "Juan"
    GET /api/socios/?buscar=juan

    # Socios activos dados de alta en 2022
    GET /api/socios/?estado=2&fecha_alta_anio=2022

    # Socios del interior ordenados por apellido
    GET /api/socios/?categoria=6&ordering=personaid__apellido

    # Combinación de filtros
    GET /api/socios/?estado=2&categoria=1&fecha_alta_desde=2020-01-01&ordering=-nrosocio
    """

    queryset = Socio.objects.select_related(
        'personaid',
        'socioestadoid',
        'categoriasocioid'
    ).all()

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    # Usar el filtro personalizado
    filterset_class = SocioFilter

    # Búsqueda simple de DRF (adicional al filtro personalizado)
    search_fields = [
        'nrosocio',
        'legajo',
        'personaid__nombre',
        'personaid__apellido',
        'personaid__documento'
    ]

    # Campos por los que se puede ordenar
    ordering_fields = [
        'nrosocio',
        'fecha_alta',
        'personaid__apellido',
        'personaid__nombre',
        'legajo'
    ]

    # Ordenamiento por defecto
    ordering = ['nrosocio']

    def get_serializer_class(self):
        """
        Usar serializer simplificado para listados (más rápido)
        y serializer completo para detalle individual
        """
        if self.action == 'list':
            return SocioListSerializer
        return SocioSerializer

    def get_queryset(self):
        """
        Permite optimizaciones adicionales en el queryset si es necesario
        """
        queryset = super().get_queryset()

        # Si se está listando, optimizar con only() para traer menos campos
        if self.action == 'list':
            queryset = queryset.only(
                'personaid',
                'nrosocio',
                'legajo',
                'socioestadoid',
                'categoriasocioid',
                'fecha_alta',
                'personaid__nombre',
                'personaid__apellido',
                'socioestadoid__nombre',
                'categoriasocioid__nombre'
            )

        return queryset