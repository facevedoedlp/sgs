from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Estudiantes de La Plata",
        default_version='v1',
        description="API para Sistema de Gestión de Socios",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('socios.urls')),
    path('api/', include('personas.urls')),
path('api/', include('deportes.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # Documentación
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]