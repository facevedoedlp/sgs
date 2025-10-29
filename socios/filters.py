import django_filters
from django.db import models
from .models import Socio, SocioEstado, CategoriaSocio


class SocioFilter(django_filters.FilterSet):
    """Filtros avanzados para socios"""

    # Filtros por texto
    nombre = django_filters.CharFilter(field_name='personaid__nombre', lookup_expr='icontains')
    apellido = django_filters.CharFilter(field_name='personaid__apellido', lookup_expr='icontains')
    documento = django_filters.CharFilter(field_name='personaid__documento', lookup_expr='icontains')
    legajo = django_filters.CharFilter(lookup_expr='icontains')

    # Filtros por número de socio
    nrosocio = django_filters.NumberFilter()
    nrosocio_desde = django_filters.NumberFilter(field_name='nrosocio', lookup_expr='gte')
    nrosocio_hasta = django_filters.NumberFilter(field_name='nrosocio', lookup_expr='lte')

    # Filtros por fecha
    fecha_alta_desde = django_filters.DateFilter(field_name='fecha_alta', lookup_expr='gte')
    fecha_alta_hasta = django_filters.DateFilter(field_name='fecha_alta', lookup_expr='lte')
    fecha_alta_anio = django_filters.NumberFilter(field_name='fecha_alta__year')

    # Filtros por estado (múltiples opciones)
    estado = django_filters.ModelMultipleChoiceFilter(
        field_name='socioestadoid',
        queryset=SocioEstado.objects.all()
    )

    # Filtros por categoría (múltiples opciones)
    categoria = django_filters.ModelMultipleChoiceFilter(
        field_name='categoriasocioid',
        queryset=CategoriaSocio.objects.all()
    )

    # Filtros booleanos
    socio_minuto = django_filters.BooleanFilter()
    socio_leon_america = django_filters.BooleanFilter()
    socio_leon_patria = django_filters.BooleanFilter()
    socio_leon_mundo = django_filters.BooleanFilter()

    # Filtro combinado de búsqueda general
    buscar = django_filters.CharFilter(method='filtro_busqueda_general')

    class Meta:
        model = Socio
        fields = []

    def filtro_busqueda_general(self, queryset, name, value):
        """Busca en nombre, apellido, documento y número de socio"""
        return queryset.filter(
            models.Q(personaid__nombre__icontains=value) |
            models.Q(personaid__apellido__icontains=value) |
            models.Q(personaid__documento__icontains=value) |
            models.Q(nrosocio__icontains=value) |
            models.Q(legajo__icontains=value)
        )