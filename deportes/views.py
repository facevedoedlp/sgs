"""
Views para el módulo de Deportes
Sistema de Gestión de Socios - Club Estudiantes de La Plata
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta

from .models import (
    Lugar, Frecuencia, TipoBeca, Disciplina, Categoria,
    GrupoHorario, Inscripcion, InscripcionHistorial, PagoActividad
)
from .serializers import (
    LugarSerializer, FrecuenciaSerializer, TipoBecaSerializer,
    DisciplinaListSerializer, DisciplinaDetailSerializer,
    CategoriaListSerializer, CategoriaDetailSerializer,
    GrupoHorarioListSerializer, GrupoHorarioDetailSerializer,
    InscripcionListSerializer, InscripcionDetailSerializer,
    InscripcionCreateSerializer, InscripcionHistorialSerializer,
    PagoActividadListSerializer, PagoActividadDetailSerializer,
    AprobarBecaSerializer, DarDeBajaSerializer, MarcarPagoSerializer
)


# ============================================
# VIEWSETS DE CATÁLOGOS
# ============================================

class LugarViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Lugares
    """
    queryset = Lugar.objects.all()
    serializer_class = LugarSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'direccion']
    ordering_fields = ['nombre', 'created_at']
    filterset_fields = ['activo']
    ordering = ['nombre']

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo lugares activos"""
        lugares = self.queryset.filter(activo=True)
        serializer = self.get_serializer(lugares, many=True)
        return Response(serializer.data)


class FrecuenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Frecuencias
    """
    queryset = Frecuencia.objects.all()
    serializer_class = FrecuenciaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'created_at']
    filterset_fields = ['activa']
    ordering = ['nombre']

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Retorna solo frecuencias activas"""
        frecuencias = self.queryset.filter(activa=True)
        serializer = self.get_serializer(frecuencias, many=True)
        return Response(serializer.data)


class TipoBecaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Tipos de Beca
    """
    queryset = TipoBeca.objects.all()
    serializer_class = TipoBecaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'porcentaje_descuento', 'created_at']
    filterset_fields = ['activa', 'requiere_autorizacion']
    ordering = ['nombre']

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Retorna solo becas activas"""
        becas = self.queryset.filter(activa=True)
        serializer = self.get_serializer(becas, many=True)
        return Response(serializer.data)


# ============================================
# VIEWSETS DE DISCIPLINAS Y CATEGORÍAS
# ============================================

class DisciplinaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Disciplinas
    """
    queryset = Disciplina.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'orden', 'created_at']
    filterset_fields = ['activa', 'tipo_actividad', 'es_temporada', 'requiere_apto_medico']
    ordering = ['orden', 'nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return DisciplinaListSerializer
        return DisciplinaDetailSerializer

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Retorna solo disciplinas activas"""
        disciplinas = self.queryset.filter(activa=True)
        serializer = self.get_serializer(disciplinas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def en_temporada(self, request):
        """Retorna disciplinas que están en temporada actual"""
        disciplinas = self.queryset.filter(activa=True)
        # Filtrar las que están en temporada
        disciplinas_validas = [d for d in disciplinas if d.en_temporada()]
        serializer = self.get_serializer(disciplinas_validas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def categorias(self, request, pk=None):
        """Retorna las categorías de una disciplina"""
        disciplina = self.get_object()
        categorias = disciplina.categorias.filter(activa=True)
        serializer = CategoriaListSerializer(categorias, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de disciplinas"""
        total = self.queryset.count()
        activas = self.queryset.filter(activa=True).count()
        por_tipo = self.queryset.values('tipo_actividad').annotate(
            total=Count('id')
        )

        return Response({
            'total_disciplinas': total,
            'activas': activas,
            'inactivas': total - activas,
            'por_tipo': por_tipo
        })


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Categorías
    """
    queryset = Categoria.objects.select_related('disciplina').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'orden', 'disciplina__nombre']
    filterset_fields = ['activa', 'nivel', 'disciplina']
    ordering = ['disciplina', 'orden', 'nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoriaListSerializer
        return CategoriaDetailSerializer

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Retorna solo categorías activas"""
        categorias = self.queryset.filter(activa=True)
        serializer = self.get_serializer(categorias, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def grupos(self, request, pk=None):
        """Retorna los grupos de una categoría"""
        categoria = self.get_object()
        grupos = categoria.grupos.filter(activo=True)
        serializer = GrupoHorarioListSerializer(grupos, many=True)
        return Response(serializer.data)


# ============================================
# VIEWSETS DE GRUPOS Y HORARIOS
# ============================================

class GrupoHorarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Grupos/Horarios
    """
    queryset = GrupoHorario.objects.select_related(
        'categoria__disciplina', 'lugar', 'frecuencia', 'instructor'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'categoria__nombre', 'categoria__disciplina__nombre']
    ordering_fields = ['nombre', 'arancel_socio', 'created_at']
    filterset_fields = ['activo', 'categoria', 'lugar', 'instructor']
    ordering = ['categoria', 'nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return GrupoHorarioListSerializer
        return GrupoHorarioDetailSerializer

    def get_queryset(self):
        """Filtrar grupos según rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user

        # Si es profesor, solo ver sus grupos
        if user.groups.filter(name='Profesor').exists():
            queryset = queryset.filter(instructor=user)

        return queryset

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo grupos activos"""
        grupos = self.get_queryset().filter(activo=True)
        serializer = self.get_serializer(grupos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def con_cupo(self, request):
        """Retorna grupos activos con cupo disponible"""
        grupos = self.get_queryset().filter(activo=True)
        grupos_con_cupo = [g for g in grupos if g.tiene_cupo_disponible()]
        serializer = self.get_serializer(grupos_con_cupo, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def inscriptos(self, request, pk=None):
        """Retorna los inscriptos de un grupo"""
        grupo = self.get_object()
        inscripciones = grupo.inscripciones.filter(estado='ACTIVA')
        serializer = InscripcionListSerializer(inscripciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Estadísticas del grupo"""
        grupo = self.get_object()
        inscripciones = grupo.inscripciones.filter(estado='ACTIVA')

        total_inscriptos = inscripciones.count()
        socios = inscripciones.filter(persona__socio__activo=True).count()
        no_socios = total_inscriptos - socios

        return Response({
            'total_inscriptos': total_inscriptos,
            'socios': socios,
            'no_socios': no_socios,
            'cupo_maximo': grupo.cupo_maximo,
            'cupo_disponible': (grupo.cupo_maximo - total_inscriptos) if grupo.cupo_maximo else None,
            'arancel_socio': float(grupo.arancel_socio),
            'arancel_no_socio': float(grupo.arancel_no_socio)
        })

    @action(detail=False, methods=['get'])
    def por_disciplina(self, request):
        """Agrupa los grupos por disciplina"""
        disciplina_id = request.query_params.get('disciplina_id')

        if not disciplina_id:
            return Response(
                {'error': 'Se requiere el parámetro disciplina_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        grupos = self.get_queryset().filter(
            categoria__disciplina_id=disciplina_id,
            activo=True
        )
        serializer = self.get_serializer(grupos, many=True)
        return Response(serializer.data)


# ============================================
# VIEWSETS DE INSCRIPCIONES
# ============================================

class InscripcionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Inscripciones
    """
    queryset = Inscripcion.objects.select_related(
        'persona', 'grupo_horario__categoria__disciplina',
        'beca', 'created_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'persona__nombre', 'persona__apellido', 'persona__documento',
        'grupo_horario__nombre', 'grupo_horario__categoria__disciplina__nombre'
    ]
    ordering_fields = ['fecha_inscripcion', 'fecha_inicio', 'estado']
    filterset_fields = ['estado', 'grupo_horario', 'persona', 'beca_aprobada']
    ordering = ['-fecha_inscripcion']

    def get_serializer_class(self):
        if self.action == 'create':
            return InscripcionCreateSerializer
        elif self.action == 'list':
            return InscripcionListSerializer
        return InscripcionDetailSerializer

    def get_queryset(self):
        """Filtrar inscripciones según rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user

        # Si es profesor, solo ver inscripciones de sus grupos
        if user.groups.filter(name='Profesor').exists():
            queryset = queryset.filter(grupo_horario__instructor=user)

        # Filtros adicionales por query params
        persona_id = self.request.query_params.get('persona_id')
        if persona_id:
            queryset = queryset.filter(persona_id=persona_id)

        disciplina_id = self.request.query_params.get('disciplina_id')
        if disciplina_id:
            queryset = queryset.filter(
                grupo_horario__categoria__disciplina_id=disciplina_id
            )

        return queryset

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Retorna solo inscripciones activas"""
        inscripciones = self.get_queryset().filter(estado='ACTIVA')
        serializer = self.get_serializer(inscripciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Retorna inscripciones pendientes de aprobación"""
        inscripciones = self.get_queryset().filter(estado='PENDIENTE')
        serializer = self.get_serializer(inscripciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def becas_pendientes(self, request):
        """Retorna inscripciones con becas pendientes de aprobación"""
        inscripciones = self.get_queryset().filter(
            beca__isnull=False,
            beca_aprobada=False,
            estado__in=['PENDIENTE', 'ACTIVA']
        )
        serializer = self.get_serializer(inscripciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprueba una inscripción"""
        inscripcion = self.get_object()

        if inscripcion.estado == 'ACTIVA':
            return Response(
                {'error': 'La inscripción ya está aprobada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        inscripcion.aprobar(usuario=request.user)

        # Registrar en historial
        InscripcionHistorial.objects.create(
            inscripcion=inscripcion,
            accion='ALTA',
            descripcion='Inscripción aprobada',
            usuario=request.user
        )

        serializer = self.get_serializer(inscripcion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def aprobar_beca(self, request, pk=None):
        """Aprueba la beca de una inscripción"""
        inscripcion = self.get_object()
        serializer = AprobarBecaSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not inscripcion.beca:
            return Response(
                {'error': 'Esta inscripción no tiene beca solicitada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        aprobar = serializer.validated_data.get('aprobar', True)

        if aprobar:
            inscripcion.aprobar_beca(usuario=request.user)
            accion = 'BECA_APROBADA'
            descripcion = 'Beca aprobada'
        else:
            inscripcion.beca = None
            inscripcion.save()
            accion = 'BECA_RECHAZADA'
            descripcion = 'Beca rechazada'

        # Agregar observaciones si hay
        obs = serializer.validated_data.get('observaciones')
        if obs:
            descripcion += f': {obs}'

        # Registrar en historial
        InscripcionHistorial.objects.create(
            inscripcion=inscripcion,
            accion=accion,
            descripcion=descripcion,
            usuario=request.user
        )

        response_serializer = self.get_serializer(inscripcion)
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def dar_de_baja(self, request, pk=None):
        """Da de baja una inscripción"""
        inscripcion = self.get_object()
        serializer = DarDeBajaSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if inscripcion.estado == 'BAJA':
            return Response(
                {'error': 'La inscripción ya está dada de baja'},
                status=status.HTTP_400_BAD_REQUEST
            )

        motivo = serializer.validated_data['motivo']
        fecha_baja = serializer.validated_data.get('fecha_baja')

        inscripcion.dar_de_baja(motivo=motivo)

        if fecha_baja:
            inscripcion.fecha_baja = fecha_baja
            inscripcion.save()

        # Registrar en historial
        InscripcionHistorial.objects.create(
            inscripcion=inscripcion,
            accion='BAJA',
            descripcion=f'Baja de inscripción: {motivo}',
            usuario=request.user
        )

        response_serializer = self.get_serializer(inscripcion)
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def suspender(self, request, pk=None):
        """Suspende temporalmente una inscripción"""
        inscripcion = self.get_object()
        motivo = request.data.get('motivo', 'Suspensión temporal')

        if inscripcion.estado != 'ACTIVA':
            return Response(
                {'error': 'Solo se pueden suspender inscripciones activas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        inscripcion.estado = 'SUSPENDIDA'
        inscripcion.save()

        # Registrar en historial
        InscripcionHistorial.objects.create(
            inscripcion=inscripcion,
            accion='SUSPENSION',
            descripcion=motivo,
            usuario=request.user
        )

        serializer = self.get_serializer(inscripcion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reactivar(self, request, pk=None):
        """Reactiva una inscripción suspendida"""
        inscripcion = self.get_object()

        if inscripcion.estado != 'SUSPENDIDA':
            return Response(
                {'error': 'Solo se pueden reactivar inscripciones suspendidas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        inscripcion.estado = 'ACTIVA'
        inscripcion.save()

        # Registrar en historial
        InscripcionHistorial.objects.create(
            inscripcion=inscripcion,
            accion='REACTIVACION',
            descripcion='Inscripción reactivada',
            usuario=request.user
        )

        serializer = self.get_serializer(inscripcion)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Retorna el historial de cambios de una inscripción"""
        inscripcion = self.get_object()
        historial = inscripcion.historial.all()
        serializer = InscripcionHistorialSerializer(historial, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de inscripciones"""
        queryset = self.get_queryset()

        total = queryset.count()
        activas = queryset.filter(estado='ACTIVA').count()
        pendientes = queryset.filter(estado='PENDIENTE').count()
        suspendidas = queryset.filter(estado='SUSPENDIDA').count()
        bajas = queryset.filter(estado='BAJA').count()

        con_beca = queryset.filter(beca__isnull=False, beca_aprobada=True).count()
        becas_pendientes = queryset.filter(
            beca__isnull=False, beca_aprobada=False
        ).count()

        return Response({
            'total': total,
            'activas': activas,
            'pendientes': pendientes,
            'suspendidas': suspendidas,
            'bajas': bajas,
            'con_beca': con_beca,
            'becas_pendientes': becas_pendientes
        })


# ============================================
# VIEWSETS DE PAGOS
# ============================================

class PagoActividadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Pagos de Actividades
    """
    queryset = PagoActividad.objects.select_related(
        'inscripcion__persona',
        'inscripcion__grupo_horario__categoria__disciplina'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'inscripcion__persona__nombre',
        'inscripcion__persona__apellido',
        'inscripcion__persona__documento'
    ]
    ordering_fields = ['mes', 'anio', 'fecha_vencimiento', 'monto_final']
    filterset_fields = ['estado', 'mes', 'anio', 'inscripcion']
    ordering = ['-anio', '-mes']

    def get_serializer_class(self):
        if self.action == 'list':
            return PagoActividadListSerializer
        return PagoActividadDetailSerializer

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Retorna pagos pendientes"""
        pagos = self.queryset.filter(estado='PENDIENTE')
        serializer = self.get_serializer(pagos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Retorna pagos vencidos"""
        pagos = self.queryset.filter(
            estado='PENDIENTE',
            fecha_vencimiento__lt=timezone.now().date()
        )
        serializer = self.get_serializer(pagos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_pagado(self, request, pk=None):
        """Marca un pago como pagado"""
        pago = self.get_object()
        serializer = MarcarPagoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if pago.estado == 'PAGADO':
            return Response(
                {'error': 'Este pago ya está marcado como pagado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fecha_pago = serializer.validated_data.get('fecha_pago')
        observaciones = serializer.validated_data.get('observaciones')

        pago.marcar_como_pagado(fecha=fecha_pago)

        if observaciones:
            pago.observaciones = observaciones
            pago.save()

        response_serializer = self.get_serializer(pago)
        return Response(response_serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de pagos"""
        queryset = self.queryset

        total = queryset.count()
        pendientes = queryset.filter(estado='PENDIENTE').count()
        pagados = queryset.filter(estado='PAGADO').count()
        vencidos = queryset.filter(
            estado='PENDIENTE',
            fecha_vencimiento__lt=timezone.now().date()
        ).count()

        monto_pendiente = queryset.filter(estado='PENDIENTE').aggregate(
            total=Sum('monto_final')
        )['total'] or 0

        monto_cobrado = queryset.filter(estado='PAGADO').aggregate(
            total=Sum('monto_final')
        )['total'] or 0

        return Response({
            'total_pagos': total,
            'pendientes': pendientes,
            'pagados': pagados,
            'vencidos': vencidos,
            'monto_pendiente': float(monto_pendiente),
            'monto_cobrado': float(monto_cobrado)
        })