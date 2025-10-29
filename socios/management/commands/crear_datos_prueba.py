"""
Comando para crear datos de prueba de alta calidad para el módulo de Deportes
Club Estudiantes de La Plata

Uso:
python manage.py crear_datos_deportes --disciplinas 15 --inscripciones 200
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta, time
from decimal import Decimal
import random
from faker import Faker

from personas.models import Persona, DomicilioPersona, EmailPersona, TelefonoPersona
from socios.models import Socio
from catalogos.models import SociosEstado, CategoriaSocio, Filial
from deportes.models import (
    Lugar, Frecuencia, TipoBeca, Disciplina, Categoria,
    GrupoHorario, Inscripcion, InscripcionHistorial, PagoActividad
)


class Command(BaseCommand):
    help = 'Crea datos de prueba realistas y completos para el módulo de Deportes'

    def __init__(self):
        super().__init__()
        self.fake = Faker('es_AR')  # Faker con locale argentino
        Faker.seed(12345)  # Semilla para reproducibilidad
        random.seed(12345)

    def add_arguments(self, parser):
        parser.add_argument(
            '--disciplinas',
            type=int,
            default=15,
            help='Cantidad de disciplinas a crear'
        )
        parser.add_argument(
            '--inscripciones',
            type=int,
            default=200,
            help='Cantidad de inscripciones a crear'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpia datos existentes antes de crear nuevos'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('CREACIÓN DE DATOS DE PRUEBA - MÓDULO DEPORTES'))
        self.stdout.write(self.style.SUCCESS('Club Estudiantes de La Plata'))
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))

        cantidad_disciplinas = options['disciplinas']
        cantidad_inscripciones = options['inscripciones']
        limpiar = options['limpiar']

        if limpiar:
            self.limpiar_datos()

        try:
            with transaction.atomic():
                # 1. Crear/verificar usuarios y grupos
                self.crear_usuarios_y_grupos()

                # 2. Crear lugares
                lugares = self.crear_lugares()

                # 3. Crear frecuencias
                frecuencias = self.crear_frecuencias()

                # 4. Crear tipos de beca
                tipos_beca = self.crear_tipos_beca()

                # 5. Crear disciplinas
                disciplinas = self.crear_disciplinas(cantidad_disciplinas)

                # 6. Crear categorías por disciplina
                categorias = self.crear_categorias(disciplinas)

                # 7. Crear grupos/horarios
                grupos = self.crear_grupos_horarios(categorias, lugares, frecuencias)

                # 8. Crear/obtener personas y socios
                personas = self.crear_personas_y_socios(cantidad_inscripciones)

                # 9. Crear inscripciones
                inscripciones = self.crear_inscripciones(
                    personas, grupos, tipos_beca, cantidad_inscripciones
                )

                # 10. Crear pagos
                self.crear_pagos(inscripciones)

                self.mostrar_resumen()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error: {str(e)}'))
            import traceback
            traceback.print_exc()

    def limpiar_datos(self):
        """Limpia datos existentes"""
        self.stdout.write('\n🗑️  Limpiando datos existentes...')

        PagoActividad.objects.all().delete()
        InscripcionHistorial.objects.all().delete()
        Inscripcion.objects.all().delete()
        GrupoHorario.objects.all().delete()
        Categoria.objects.all().delete()
        Disciplina.objects.all().delete()
        TipoBeca.objects.all().delete()
        Frecuencia.objects.all().delete()
        Lugar.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('  ✓ Datos limpiados\n'))

    def crear_usuarios_y_grupos(self):
        """Crea usuarios y grupos necesarios"""
        self.stdout.write('\n👥 Creando usuarios y grupos...')

        # Crear grupos
        grupo_profesor, _ = Group.objects.get_or_create(name='Profesor')
        grupo_admin_deportes, _ = Group.objects.get_or_create(name='Admin Deportes')

        # Crear usuarios profesores
        self.profesores = []
        nombres_profesores = [
            ('Carlos', 'Fernández', 'cfernandez'),
            ('María', 'González', 'mgonzalez'),
            ('Roberto', 'Silva', 'rsilva'),
            ('Laura', 'Martínez', 'lmartinez'),
            ('Diego', 'Rodríguez', 'drodriguez'),
            ('Ana', 'López', 'alopez'),
            ('Pablo', 'García', 'pgarcia'),
            ('Sofía', 'Pérez', 'sperez'),
        ]

        for nombre, apellido, username in nombres_profesores:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': nombre,
                    'last_name': apellido,
                    'email': f'{username}@estudiantes.edu.ar',
                    'is_staff': True
                }
            )
            if created:
                user.set_password('profesor123')
                user.save()
            user.groups.add(grupo_profesor)
            self.profesores.append(user)

        # Crear admin deportes
        self.admin_deportes, created = User.objects.get_or_create(
            username='admin_deportes',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Deportes',
                'email': 'deportes@estudiantes.edu.ar',
                'is_staff': True,
                'is_superuser': False
            }
        )
        if created:
            self.admin_deportes.set_password('admin123')
            self.admin_deportes.save()
        self.admin_deportes.groups.add(grupo_admin_deportes)

        self.stdout.write(f'  ✓ {len(self.profesores)} profesores creados')
        self.stdout.write(f'  ✓ 1 administrador deportivo creado')

    def crear_lugares(self):
        """Crea lugares realistas"""
        self.stdout.write('\n📍 Creando lugares...')

        lugares_data = [
            ('Country Club', 'Av. Country Club 1050, Gonnet', 200),
            ('Sede Social', 'Calle 1 y 57, La Plata', 500),
            ('Estadio UNO', '56 y 115, La Plata', 5000),
            ('Gimnasio Principal', 'Calle 1 y 57, La Plata', 80),
            ('Gimnasio Auxiliar', 'Calle 1 y 57, La Plata', 40),
            ('Pileta Olímpica', 'Country Club, Gonnet', 100),
            ('Pileta Infantil', 'Country Club, Gonnet', 50),
            ('Canchas de Tenis', 'Country Club, Gonnet', 20),
            ('Cancha Fútbol 5', 'Calle 7 y 33, La Plata', 50),
            ('Salón de Danzas', 'Sede Social, La Plata', 60),
            ('Tatami (Judo)', 'Gimnasio Principal', 30),
            ('Ring de Boxeo', 'Gimnasio Principal', 25),
        ]

        lugares = []
        for nombre, direccion, capacidad in lugares_data:
            lugar, created = Lugar.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'direccion': direccion,
                    'capacidad_maxima': capacidad,
                    'activo': True
                }
            )
            lugares.append(lugar)
            status = '✓' if created else '○'
            self.stdout.write(f'  {status} {nombre}')

        return lugares

    def crear_frecuencias(self):
        """Crea frecuencias de actividades"""
        self.stdout.write('\n📅 Creando frecuencias...')

        frecuencias_data = [
            ('LU-MI-VI', True, False, True, False, True, False, False),
            ('MA-JU', False, True, False, True, False, False, False),
            ('LU-JU', True, False, False, True, False, False, False),
            ('MA-VI', False, True, False, False, True, False, False),
            ('LU-MI', True, False, True, False, False, False, False),
            ('MI-VI', False, False, True, False, True, False, False),
            ('LU-MA-MI-JU-VI', True, True, True, True, True, False, False),
            ('SÁBADOS', False, False, False, False, False, True, False),
            ('DOMINGOS', False, False, False, False, False, False, True),
            ('LU-MI-VI-SÁ', True, False, True, False, True, True, False),
            ('PASE LIBRE', False, False, False, False, False, False, False),
        ]

        frecuencias = []
        for nombre, lu, ma, mi, ju, vi, sa, do in frecuencias_data:
            frecuencia, created = Frecuencia.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'lunes': lu,
                    'martes': ma,
                    'miercoles': mi,
                    'jueves': ju,
                    'viernes': vi,
                    'sabado': sa,
                    'domingo': do,
                    'activa': True
                }
            )
            frecuencias.append(frecuencia)
            status = '✓' if created else '○'
            self.stdout.write(f'  {status} {nombre}')

        return frecuencias

    def crear_tipos_beca(self):
        """Crea tipos de beca realistas"""
        self.stdout.write('\n🎓 Creando tipos de beca...')

        becas_data = [
            ('HIJO_EMPLEADO', 'Hijo de Empleado del Club', 100, False, False, ''),
            ('HERMANO_DEPORTE', 'Hermano practicante del mismo deporte', 50, False, False, ''),
            ('HERMANO_SEGUNDO', 'Segundo hermano (cualquier deporte)', 30, False, False, ''),
            ('HERMANO_TERCERO', 'Tercer hermano o más', 50, False, False, ''),
            ('SOCIO_VITALICIO', 'Socio Vitalicio', 100, False, False, ''),
            ('LESION_MEDICA', 'Lesión con certificado médico', 100, True, True, 'Certificado médico'),
            ('BECA_RENDIMIENTO', 'Beca por Rendimiento Deportivo', 75, True, True, 'Informe del entrenador'),
            ('BECA_SOCIAL', 'Beca Social', 60, True, True, 'Documentación socioeconómica'),
            ('EMPLEADO_DOCENTE', 'Empleado Docente', 80, False, False, ''),
            ('DESDE_DIA_16', 'Inscripción desde día 16 del mes', 50, False, False, ''),
            ('DESDE_DIA_21', 'Inscripción desde día 21 del mes', 70, False, False, ''),
            ('COMPETENCIA_ALTA', 'Deportista de Alto Rendimiento', 90, True, True, 'Certificado federación'),
        ]

        tipos_beca = []
        for codigo, nombre, porcentaje, req_aut, req_doc, doc_req in becas_data:
            beca, created = TipoBeca.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'porcentaje_descuento': Decimal(str(porcentaje)),
                    'requiere_autorizacion': req_aut,
                    'requiere_documentacion': req_doc,
                    'documentacion_requerida': doc_req if doc_req else None,
                    'activa': True
                }
            )
            tipos_beca.append(beca)
            status = '✓' if created else '○'
            self.stdout.write(f'  {status} {nombre} ({porcentaje}%)')

        return tipos_beca

    def crear_disciplinas(self, cantidad):
        """Crea disciplinas deportivas realistas"""
        self.stdout.write(f'\n🏅 Creando disciplinas...')

        disciplinas_data = [
            ('Natación', 'NATACION', True, 5, None, False),
            ('Fútbol', 'DEPORTE', True, 5, None, False),
            ('Básquet', 'DEPORTE', True, 6, None, False),
            ('Hockey', 'DEPORTE', True, 6, None, False),
            ('Tenis', 'DEPORTE', True, 5, None, False),
            ('Handball', 'DEPORTE', True, 7, None, False),
            ('Voleibol', 'DEPORTE', True, 8, None, False),
            ('Gimnasia Artística', 'DEPORTE', True, 4, None, False),
            ('Taekwondo', 'DEPORTE', True, 5, None, False),
            ('Judo', 'DEPORTE', True, 5, None, False),
            ('Boxeo', 'DEPORTE', True, 14, None, False),
            ('Patín Artístico', 'DEPORTE', True, 4, None, False),
            ('Ajedrez', 'DEPORTE', False, 5, None, False),
            ('Yoga', 'GIMNASIO', False, 16, None, False),
            ('Pilates', 'GIMNASIO', False, 16, None, False),
            ('Musculación', 'GIMNASIO', True, 14, None, False),
            ('Funcional', 'GIMNASIO', False, 14, None, False),
            ('Zumba', 'GIMNASIO', False, 8, None, False),
            ('Colonia de Verano', 'COLONIA', False, 4, 14, True),
            ('Colonia de Invierno', 'COLONIA', False, 4, 14, True),
            ('Escuela de Arqueros', 'CURSO', True, 8, None, False),
            ('Preparación Física', 'GIMNASIO', False, 12, None, False),
        ]

        disciplinas = []
        orden = 1

        for nombre, tipo, req_apto, edad_min, edad_max, es_temp in disciplinas_data[:cantidad]:
            # Determinar si es temporada
            fecha_inicio = fecha_fin = None
            if es_temp:
                if 'Verano' in nombre:
                    fecha_inicio = date(timezone.now().year, 12, 15)
                    fecha_fin = date(timezone.now().year + 1, 2, 28)
                elif 'Invierno' in nombre:
                    fecha_inicio = date(timezone.now().year, 7, 1)
                    fecha_fin = date(timezone.now().year, 7, 31)

            disciplina, created = Disciplina.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'tipo_actividad': tipo,
                    'requiere_apto_medico': req_apto,
                    'edad_minima': edad_min,
                    'edad_maxima': edad_max,
                    'es_temporada': es_temp,
                    'fecha_inicio_temporada': fecha_inicio,
                    'fecha_fin_temporada': fecha_fin,
                    'activa': True,
                    'orden': orden,
                    'descripcion': self.fake.text(max_nb_chars=150)
                }
            )
            disciplinas.append(disciplina)
            orden += 1

            status = '✓' if created else '○'
            self.stdout.write(f'  {status} {nombre}')

        return disciplinas

    def crear_categorias(self, disciplinas):
        """Crea categorías por edad para cada disciplina"""
        self.stdout.write('\n📊 Creando categorías...')

        # Categorías estándar por edad
        categorias_edad = [
            ('Infantil', 'INICIACION', 4, 7),
            ('Pre-Juvenil', 'INICIACION', 8, 11),
            ('Juvenil', 'INTERMEDIO', 12, 15),
            ('Cadetes', 'INTERMEDIO', 16, 17),
            ('Mayores', 'AVANZADO', 18, 35),
            ('Adultos', 'LIBRE', 36, None),
        ]

        categorias = []
        total = 0

        for disciplina in disciplinas:
            # Para colonias, crear categorías diferentes
            if disciplina.tipo_actividad == 'COLONIA':
                cats_colonia = [
                    ('Grupo 1 (4-6 años)', 'INICIACION', 4, 6),
                    ('Grupo 2 (7-9 años)', 'INICIACION', 7, 9),
                    ('Grupo 3 (10-12 años)', 'INTERMEDIO', 10, 12),
                    ('Grupo 4 (13-15 años)', 'INTERMEDIO', 13, 15),
                ]
                cats_a_crear = cats_colonia
            # Para gimnasio, categorías simplificadas
            elif disciplina.tipo_actividad == 'GIMNASIO':
                cats_gimnasio = [
                    ('Principiantes', 'INICIACION', 14, None),
                    ('Intermedio', 'INTERMEDIO', 14, None),
                    ('Avanzado', 'AVANZADO', 14, None),
                ]
                cats_a_crear = cats_gimnasio
            else:
                cats_a_crear = categorias_edad

            orden = 1
            for nombre, nivel, edad_desde, edad_hasta in cats_a_crear:
                # Verificar compatibilidad con edad mínima de la disciplina
                if disciplina.edad_minima and edad_desde and edad_desde < disciplina.edad_minima:
                    edad_desde = disciplina.edad_minima

                categoria, created = Categoria.objects.get_or_create(
                    disciplina=disciplina,
                    nombre=nombre,
                    defaults={
                        'nivel': nivel,
                        'edad_desde': edad_desde,
                        'edad_hasta': edad_hasta,
                        'activa': True,
                        'orden': orden
                    }
                )
                categorias.append(categoria)
                orden += 1

                if created:
                    total += 1

        self.stdout.write(f'  ✓ {total} categorías creadas')
        return categorias

    def crear_grupos_horarios(self, categorias, lugares, frecuencias):
        """Crea grupos con horarios realistas"""
        self.stdout.write('\n👥 Creando grupos/horarios...')

        horarios_manana = [
            (time(8, 0), time(9, 0)),
            (time(9, 0), time(10, 0)),
            (time(10, 0), time(11, 0)),
            (time(11, 0), time(12, 0)),
        ]

        horarios_tarde = [
            (time(14, 0), time(15, 0)),
            (time(15, 0), time(16, 0)),
            (time(16, 0), time(17, 0)),
            (time(17, 0), time(18, 0)),
            (time(18, 0), time(19, 0)),
            (time(19, 0), time(20, 0)),
        ]

        horarios_noche = [
            (time(20, 0), time(21, 0)),
            (time(21, 0), time(22, 0)),
        ]

        todos_horarios = horarios_manana + horarios_tarde + horarios_noche

        grupos = []
        total = 0

        for categoria in categorias:
            # Número de grupos según popularidad
            num_grupos = random.randint(1, 3)

            for i in range(num_grupos):
                # Seleccionar lugar apropiado
                nombre_disciplina = categoria.disciplina.nombre.lower()
                if 'natación' in nombre_disciplina or 'natacion' in nombre_disciplina:
                    lugar = next((l for l in lugares if 'Pileta' in l.nombre), random.choice(lugares))
                elif 'tenis' in nombre_disciplina:
                    lugar = next((l for l in lugares if 'Tenis' in l.nombre), random.choice(lugares))
                elif 'boxeo' in nombre_disciplina:
                    lugar = next((l for l in lugares if 'Ring' in l.nombre or 'Gimnasio' in l.nombre),
                                 random.choice(lugares))
                elif 'judo' in nombre_disciplina or 'taekwondo' in nombre_disciplina:
                    lugar = next((l for l in lugares if 'Tatami' in l.nombre or 'Gimnasio' in l.nombre),
                                 random.choice(lugares))
                elif categoria.disciplina.tipo_actividad == 'GIMNASIO':
                    lugar = next((l for l in lugares if 'Gimnasio' in l.nombre), random.choice(lugares))
                else:
                    lugar = random.choice(lugares)

                frecuencia = random.choice(frecuencias)
                horario_inicio, horario_fin = random.choice(todos_horarios)

                # Definir aranceles realistas
                arancel_base = random.choice([8000, 10000, 12000, 15000, 18000, 20000])
                arancel_socio = Decimal(str(arancel_base))
                arancel_no_socio = Decimal(str(int(arancel_base * 1.5)))  # 50% más para no socios

                # Cupo según tipo de actividad
                if categoria.disciplina.tipo_actividad == 'GIMNASIO':
                    cupo = random.randint(15, 30)
                elif 'Infantil' in categoria.nombre or 'Pre-Juvenil' in categoria.nombre:
                    cupo = random.randint(12, 20)
                else:
                    cupo = random.randint(15, 25)

                # Asignar profesor
                instructor = random.choice(self.profesores)

                nombre_grupo = f"{categoria.nombre} - Grupo {i + 1}"
                if horario_inicio.hour < 12:
                    nombre_grupo += " (Mañana)"
                elif horario_inicio.hour < 18:
                    nombre_grupo += " (Tarde)"
                else:
                    nombre_grupo += " (Noche)"

                grupo, created = GrupoHorario.objects.get_or_create(
                    categoria=categoria,
                    nombre=nombre_grupo,
                    defaults={
                        'frecuencia': frecuencia,
                        'horario_inicio': horario_inicio,
                        'horario_fin': horario_fin,
                        'lugar': lugar,
                        'cupo_maximo': cupo,
                        'instructor': instructor,
                        'arancel_socio': arancel_socio,
                        'arancel_no_socio': arancel_no_socio,
                        'activo': True,
                        'observaciones': f'Grupo a cargo de {instructor.get_full_name()}'
                    }
                )
                grupos.append(grupo)

                if created:
                    total += 1

        self.stdout.write(f'  ✓ {total} grupos/horarios creados')
        return grupos

    def crear_personas_y_socios(self, cantidad):
        """Crea o usa personas existentes"""
        self.stdout.write(f'\n👤 Verificando personas y socios...')

        # Primero intentar usar personas existentes
        personas_existentes = list(Persona.objects.all()[:cantidad])

        if len(personas_existentes) >= cantidad:
            self.stdout.write(f'  ✓ Usando {len(personas_existentes)} personas existentes')
            return personas_existentes

        # Si no hay suficientes, crear nuevas
        faltantes = cantidad - len(personas_existentes)
        self.stdout.write(f'  ! Faltan {faltantes} personas, creando...')

        personas_nuevas = []

        for i in range(faltantes):
            try:
                # Datos realistas con Faker
                nombre = self.fake.first_name()
                apellido = self.fake.last_name()
                documento = self.fake.unique.random_number(digits=8, fix_len=True)

                persona = Persona.objects.create(
                    apellido=apellido,
                    nombre=nombre,
                    documento=str(documento),
                    fecha_nacimiento=self.fake.date_of_birth(minimum_age=4, maximum_age=70)
                )

                # Email
                EmailPersona.objects.create(
                    persona=persona,
                    email=f"{nombre.lower()}.{apellido.lower()}@email.com".replace(' ', ''),
                    principal=True,
                    validado=random.choice([True, False])
                )

                # Teléfono
                TelefonoPersona.objects.create(
                    persona=persona,
                    caracteristica='221',
                    numero=str(self.fake.random_number(digits=7, fix_len=True)),
                    tipo='Celular',
                    principal=True
                )

                personas_nuevas.append(persona)

            except Exception as e:
                continue

        self.stdout.write(f'  ✓ {len(personas_nuevas)} personas nuevas creadas')

        return personas_existentes + personas_nuevas

    def crear_inscripciones(self, personas, grupos, tipos_beca, cantidad):
        """Crea inscripciones realistas"""
        self.stdout.write(f'\n✍️  Creando inscripciones...')

        inscripciones = []
        estados = ['PENDIENTE', 'ACTIVA', 'ACTIVA', 'ACTIVA', 'SUSPENDIDA']  # Más activas

        personas_usadas = set()

        for _ in range(cantidad):
            try:
                # Seleccionar persona que no tenga muchas inscripciones
                persona = random.choice([p for p in personas if personas_usadas.count(p.id) < 3])
                personas_usadas.add(persona.id)

                # Calcular edad de la persona
                edad = (date.today() - persona.fecha_nacimiento).days // 365

                # Filtrar grupos apropiados por edad
                grupos_validos = [
                    g for g in grupos
                    if (not g.categoria.edad_desde or edad >= g.categoria.edad_desde) and
                       (not g.categoria.edad_hasta or edad <= g.categoria.edad_hasta)
                ]

                if not grupos_validos:
                    continue

                grupo = random.choice(grupos_validos)

                # Verificar que no esté ya inscripto en el mismo grupo
                if Inscripcion.objects.filter(persona=persona, grupo_horario=grupo, estado='ACTIVA').exists():
                    continue

                # Estado de la inscripción
                estado = random.choice(estados)

                # Fechas
                fecha_inscripcion = self.fake.date_between(start_date='-6m', end_date='today')
                fecha_inicio = fecha_inscripcion
                fecha_baja = None

                if estado == 'BAJA':
                    fecha_baja = self.fake.date_between(start_date=fecha_inscripcion, end_date='today')

                # Beca (30% de probabilidad)
                beca = None
                beca_aprobada = False
                if random.random() < 0.3:
                    beca = random.choice(tipos_beca)
                    # Si requiere autorización, 70% aprobadas, 30% pendientes
                    if beca.requiere_autorizacion:
                        beca_aprobada = random.random() < 0.7
                    else:
                        beca_aprobada = True

                # Apto médico
                apto_presentado = False
                apto_vencimiento = None
                if grupo.categoria.disciplina.requiere_apto_medico:
                    apto_presentado = random.random() < 0.85  # 85% presentó apto
                    if apto_presentado:
                        # Apto vigente por 1 año desde hace 6 meses
                        apto_vencimiento = date.today() + timedelta(days=180)

                inscripcion = Inscripcion.objects.create(
                    persona=persona,
                    grupo_horario=grupo,
                    estado=estado,
                    fecha_inscripcion=fecha_inscripcion,
                    fecha_inicio=fecha_inicio,
                    fecha_baja=fecha_baja,
                    beca=beca,
                    beca_aprobada=beca_aprobada,
                    beca_aprobada_por=self.admin_deportes if beca_aprobada and beca else None,
                    beca_aprobada_fecha=timezone.now() if beca_aprobada and beca else None,
                    apto_medico_presentado=apto_presentado,
                    apto_medico_vencimiento=apto_vencimiento,
                    created_by=self.admin_deportes,
                    observaciones=self.fake.text(max_nb_chars=100) if random.random() < 0.2 else ''
                )

                inscripciones.append(inscripcion)

                # Crear historial de alta
                InscripcionHistorial.objects.create(
                    inscripcion=inscripcion,
                    accion='ALTA',
                    descripcion='Inscripción inicial',
                    usuario=self.admin_deportes
                )

                if estado == 'BAJA':
                    InscripcionHistorial.objects.create(
                        inscripcion=inscripcion,
                        accion='BAJA',
                        descripcion='Baja por ' + random.choice([
                            'cambio de horario',
                            'razones personales',
                            'mudanza',
                            'lesión'
                        ]),
                        usuario=self.admin_deportes
                    )

            except Exception as e:
                continue

        self.stdout.write(f'  ✓ {len(inscripciones)} inscripciones creadas')
        return inscripciones

    def crear_pagos(self, inscripciones):
        """Crea pagos mensuales para inscripciones activas"""
        self.stdout.write('\n💰 Creando pagos...')

        inscripciones_activas = [i for i in inscripciones if i.estado == 'ACTIVA']

        total_pagos = 0

        for inscripcion in inscripciones_activas:
            # Crear pagos de los últimos 3 meses
            mes_actual = date.today().month
            anio_actual = date.today().year

            for offset in range(3):
                mes = mes_actual - offset
                anio = anio_actual

                if mes <= 0:
                    mes += 12
                    anio -= 1

                # Calcular montos
                arancel_base = inscripcion.get_arancel_base()
                descuento_total = inscripcion.get_descuento_total()
                monto_descuento = arancel_base * (descuento_total / 100)
                monto_final = arancel_base - monto_descuento

                # Fecha de vencimiento (día 10 de cada mes)
                fecha_vencimiento = date(anio, mes, 10)

                # Estado del pago
                if offset == 0:  # Mes actual
                    estado = random.choice(['PENDIENTE', 'PENDIENTE', 'PAGADO'])
                    fecha_pago = None if estado == 'PENDIENTE' else self.fake.date_between(
                        start_date=fecha_vencimiento,
                        end_date='today'
                    )
                else:  # Meses anteriores
                    estado = random.choice(['PAGADO', 'PAGADO', 'PAGADO', 'VENCIDO'])
                    fecha_pago = self.fake.date_between(
                        start_date=fecha_vencimiento,
                        end_date=fecha_vencimiento + timedelta(days=15)
                    ) if estado == 'PAGADO' else None

                try:
                    pago, created = PagoActividad.objects.get_or_create(
                        inscripcion=inscripcion,
                        mes=mes,
                        anio=anio,
                        defaults={
                            'monto_base': arancel_base,
                            'descuento_porcentaje': descuento_total,
                            'monto_descuento': monto_descuento,
                            'monto_final': monto_final,
                            'estado': estado,
                            'fecha_vencimiento': fecha_vencimiento,
                            'fecha_pago': fecha_pago
                        }
                    )

                    if created:
                        total_pagos += 1

                except Exception as e:
                    continue

        self.stdout.write(f'  ✓ {total_pagos} pagos creados')

    def mostrar_resumen(self):
        """Muestra resumen de datos creados"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('RESUMEN DE DATOS CREADOS'))
        self.stdout.write('=' * 70 + '\n')

        resumen = [
            ('Lugares', Lugar.objects.count()),
            ('Frecuencias', Frecuencia.objects.count()),
            ('Tipos de Beca', TipoBeca.objects.count()),
            ('Disciplinas', Disciplina.objects.count()),
            ('Categorías', Categoria.objects.count()),
            ('Grupos/Horarios', GrupoHorario.objects.count()),
            ('Inscripciones', Inscripcion.objects.count()),
            ('  - Activas', Inscripcion.objects.filter(estado='ACTIVA').count()),
            ('  - Pendientes', Inscripcion.objects.filter(estado='PENDIENTE').count()),
            ('  - Con beca aprobada', Inscripcion.objects.filter(beca__isnull=False, beca_aprobada=True).count()),
            ('Pagos', PagoActividad.objects.count()),
            ('  - Pagados', PagoActividad.objects.filter(estado='PAGADO').count()),
            ('  - Pendientes', PagoActividad.objects.filter(estado='PENDIENTE').count()),
        ]

        for label, valor in resumen:
            self.stdout.write(f'  {label}: {valor}')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✓ DATOS DE PRUEBA CREADOS EXITOSAMENTE'))
        self.stdout.write('=' * 70 + '\n')

        self.stdout.write('\n📝 Próximos pasos:')
        self.stdout.write('  1. Accede al admin: http://localhost:8000/admin/')
        self.stdout.write('  2. Revisa las disciplinas y grupos creados')
        self.stdout.write('  3. Prueba la API: http://localhost:8000/api/deportes/')
        self.stdout.write('  4. Usuarios de prueba:')
        self.stdout.write('     - Admin: admin_deportes / admin123')
        self.stdout.write('     - Profesores: cfernandez, mgonzalez, etc. / profesor123')
        self.stdout.write('')