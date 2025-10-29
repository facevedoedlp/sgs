from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Socio,
    SocioGrupoFamiliar,
    SocioGrupoFamiliarMiembro,
    SocioDiscapacidad,
    SocioDiscapacidadAcompanante,
    SocioDomicilioPagoSas
)
from .serializers import (
    SocioSerializer,
    SocioCreateUpdateSerializer,
    SocioGrupoFamiliarSerializer,
    SocioDiscapacidadSerializer,
    SocioDomicilioPagoSasSerializer
)
from auditoria.models import SocioHistoria
from catalogos.models import SociosHistoriaAccion


class SocioViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de socios

    list: Listar todos los socios
    retrieve: Obtener detalle de un socio
    create: Crear nuevo socio
    update: Actualizar socio completo
    partial_update: Actualizar campos específicos
    destroy: Dar de baja un socio
    """
    queryset = Socio.objects.select_related(
        'persona',
        'estado',
        'categoria',
        'filial'
    ).prefetch_related(
        'persona__domicilios',
        'persona__emails',
        'persona__telefonos',
        'grupos_familiares',
        'historial'
    ).all()

    permission_classes = [IsAuthenticated]

    # --- Filtros, búsqueda y orden ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'categoria', 'filial']
    search_fields = ['numero_socio', 'persona__apellido', 'persona__nombre', 'persona__documento']
    ordering_fields = ['numero_socio', 'fecha_alta', 'persona__apellido']
    ordering = ['numero_socio']
    # ----------------------------------

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SocioCreateUpdateSerializer
        return SocioSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Crear nuevo socio y registrar en historial"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        socio = serializer.save()

        # Registrar en historial
        try:
            accion = SociosHistoriaAccion.objects.get(descripcion='Alta de socio')
            SocioHistoria.objects.create(
                socio=socio,
                categoria=socio.categoria,
                estado=socio.estado,
                accion=accion,
                numero_socio=socio.numero_socio,
                usuario=request.user if request.user.is_authenticated else None,
                observaciones=f'Socio creado vía API por {request.user.username if request.user.is_authenticated else "sistema"}'
            )
        except SociosHistoriaAccion.DoesNotExist:
            pass

        headers = self.get_success_headers(serializer.data)
        return Response(
            SocioSerializer(socio).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Actualizar socio y registrar cambios en historial"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Guardar estados anteriores
        estado_anterior = instance.estado
        categoria_anterior = instance.categoria

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        socio = serializer.save()

        # Registrar en historial si cambió estado o categoría
        if estado_anterior != socio.estado or categoria_anterior != socio.categoria:
            try:
                if estado_anterior != socio.estado:
                    accion = SociosHistoriaAccion.objects.get(descripcion='Cambio de estado')
                else:
                    accion = SociosHistoriaAccion.objects.get(descripcion='Cambio de categoría')

                SocioHistoria.objects.create(
                    socio=socio,
                    categoria=socio.categoria,
                    estado=socio.estado,
                    accion=accion,
                    numero_socio=socio.numero_socio,
                    usuario=request.user if request.user.is_authenticated else None,
                    observaciones=f'Modificado vía API por {request.user.username if request.user.is_authenticated else "sistema"}'
                )
            except SociosHistoriaAccion.DoesNotExist:
                pass

        return Response(SocioSerializer(socio).data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """Dar de baja un socio (soft delete)"""
        instance = self.get_object()

        # Registrar en historial
        try:
            accion = SociosHistoriaAccion.objects.get(descripcion='Baja de socio')
            SocioHistoria.objects.create(
                socio=instance,
                categoria=instance.categoria,
                estado=instance.estado,
                accion=accion,
                numero_socio=instance.numero_socio,
                usuario=request.user if request.user.is_authenticated else None,
                observaciones=f'Socio dado de baja vía API por {request.user.username if request.user.is_authenticated else "sistema"}'
            )
        except SociosHistoriaAccion.DoesNotExist:
            pass

        # Soft delete (cambiar estado)
        from catalogos.models import SociosEstado
        try:
            estado_baja = SociosEstado.objects.get(descripcion='Baja')
            instance.estado = estado_baja
            instance.save()
            return Response(
                {'message': 'Socio dado de baja exitosamente'},
                status=status.HTTP_200_OK
            )
        except SociosEstado.DoesNotExist:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Endpoint: /api/socios/activos/ - Solo socios activos"""
        socios_activos = self.queryset.filter(estado__indica_socio_activo=True)
        page = self.paginate_queryset(socios_activos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(socios_activos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Endpoint: /api/socios/{id}/historial/ - Ver historial del socio"""
        socio = self.get_object()
        historial = socio.historial.all()
        from auditoria.serializers import SocioHistoriaSerializer
        serializer = SocioHistoriaSerializer(historial, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint: /api/socios/{id}/cambiar_estado/
        Body: {"estado_id": 2, "observaciones": "Motivo del cambio"}
        """
        socio = self.get_object()
        estado_id = request.data.get('estado_id')
        observaciones = request.data.get('observaciones', '')

        if not estado_id:
            return Response(
                {'error': 'Se requiere estado_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from catalogos.models import SociosEstado
            nuevo_estado = SociosEstado.objects.get(socioestadoid=estado_id)

            estado_anterior = socio.estado
            socio.estado = nuevo_estado
            socio.save()

            # Registrar en historial
            accion = SociosHistoriaAccion.objects.get(descripcion='Cambio de estado')
            SocioHistoria.objects.create(
                socio=socio,
                categoria=socio.categoria,
                estado=nuevo_estado,
                accion=accion,
                numero_socio=socio.numero_socio,
                usuario=request.user if request.user.is_authenticated else None,
                observaciones=observaciones or f'Cambio de {estado_anterior.descripcion} a {nuevo_estado.descripcion}'
            )

            return Response(
                SocioSerializer(socio).data,
                status=status.HTTP_200_OK
            )
        except SociosEstado.DoesNotExist:
            return Response(
                {'error': 'Estado no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except SociosHistoriaAccion.DoesNotExist:
            return Response(
                {'error': 'Acción de historial no configurada'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SocioGrupoFamiliarViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de grupos familiares"""
    queryset = SocioGrupoFamiliar.objects.prefetch_related('miembros__socio__persona').all()
    serializer_class = SocioGrupoFamiliarSerializer
    permission_classes = [IsAuthenticated]


class SocioDiscapacidadViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de certificados de discapacidad"""
    queryset = SocioDiscapacidad.objects.select_related('socio__persona').prefetch_related('acompanantes').all()
    serializer_class = SocioDiscapacidadSerializer
    permission_classes = [IsAuthenticated]


class SocioDomicilioPagoSasViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de domicilios de pago SAS"""
    queryset = SocioDomicilioPagoSas.objects.select_related('socio__persona').all()
    serializer_class = SocioDomicilioPagoSasSerializer
    permission_classes = [IsAuthenticated]
