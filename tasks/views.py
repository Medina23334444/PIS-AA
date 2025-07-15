from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from datetime import datetime, timedelta
from django.utils import timezone

from .forms import UsuarioForm, PerfilForm
from .models import Usuario, Rol, RolPersona, Sugerencia, PeriodoAcademico, Ciclo, Perfil, EstadisticaPeriodo, Automata, \
    Evento, Alerta
from django.contrib import messages
import tasks.RungeKutta as r
from django.http.response import JsonResponse
import json
from django.views.decorators.http import require_http_methods
import logging
from tasks.decorators import log_event

logger = logging.getLogger(__name__)


def rol_requerido(*roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                roles_persona = RolPersona.objects.filter(usuario=request.user)
                user_roles = [rp.rol.nombre for rp in roles_persona]
                if any(role in user_roles for role in roles):
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('home')
            else:
                return redirect('iniciar_sesion')

        return _wrapped_view

    return decorator


def home(request):
    return render(request, 'landingPage.html')


def iniciarSesion(request):
    if request.user.is_authenticated:

        roles_persona = RolPersona.objects.filter(usuario=request.user)
        roles = [rp.rol for rp in roles_persona]

        if any(rol.nombre == 'Personal' for rol in roles):
            return redirect('homePersonal')
        elif any(rol.nombre == 'Administrador' for rol in roles):
            return redirect('homeAdministrador')
        else:
            return redirect('iniciar_sesion')

    if request.method == "POST":
        correo = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=correo, password=password)

        if user is not None:
            login(request, user)

            roles_persona = RolPersona.objects.filter(usuario=user)
            roles = [rp.rol for rp in roles_persona]
            Evento.objects.create(
                sesion_id=request.session.session_key,
                tipo_evento="login",
                datos={"username": correo}
            )
            if any(rol.nombre == 'Personal' for rol in roles):
                return redirect('homePersonal')
            elif any(rol.nombre == 'Administrador' for rol in roles):
                return redirect('homeAdministrador')
            else:
                return redirect('iniciarSesion')
        else:
            Evento.objects.create(
                sesion_id=request.session.session_key,
                tipo_evento="failed_login",
                datos={"username": correo}
            )
            if Usuario.objects.filter(username=correo).exists():
                error = 'Contraseña incorrecta'
            else:
                error = 'La cuenta no existe'

            messages.error(request, error)
            return render(request, 'iniciarSesion.html')

    return render(request, 'iniciarSesion.html')


@log_event("logout")
@login_required
def cerrarSesion(request):
    logout(request)
    return redirect('home')


@log_event("submit_request")
@rol_requerido('Administrador')
@login_required
def registrarUsuario(request):
    if request.method == 'POST':
        data = request.POST
        dni = request.POST['dni']

        if not validar_cedula(dni):
            messages.error(request, 'La cédula ingresada no es válida.')
            return redirect('admiManage')

        try:
            with transaction.atomic():
                usuario = Usuario.objects.create(
                    username=request.POST['correo'],
                    email=request.POST['correo'],
                    dni=request.POST['dni'],
                    nombres=request.POST['nombres'],
                    apellidos=request.POST['apellidos'],
                    direccion=request.POST['direccion'],
                    telefono=request.POST['telefono'],
                )
                usuario.set_password(request.POST['dni'])
                usuario.save()

                if data['tipo_cargo'] == 'Administrador':
                    rol = Rol.objects.get(nombre='Administrador')
                elif data['tipo_cargo'] == 'Personal':
                    rol = Rol.objects.get(nombre='Personal')
                else:
                    messages.error(request, 'Tipo de cargo no válido.')
                    return redirect('admiManage')

                RolPersona.objects.create(rol=rol, usuario=usuario)
                messages.success(request, 'Usuario registrado correctamente!')
                return redirect('admiManage')

        except Rol.DoesNotExist:
            messages.error(request, 'El rol especificado no existe.')
            return redirect('admiManage')

        except IntegrityError:
            messages.error(request, 'Las credenciales ya han sido registradas por otro usuario.')
            return redirect('admiManage')

        except Exception as e:
            messages.error(request, f'Error al registrar usuario')
            return redirect('admiManage')

    return render(request, 'admiManage.html')


def validar_cedula(cedula):
    if len(cedula) != 10:
        return False

    try:
        digitos_cedula = [int(d) for d in cedula]
    except ValueError:
        return False

    cod_provincia = int(cedula[:2])  # Validar código de provincia
    if cod_provincia < 1 or cod_provincia > 24:
        return False

    digito_3 = digitos_cedula[2]  # Validar digito 3, este entre 0 y 6
    if digito_3 < 0 or digito_3 > 6:
        return False

    # coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(0, 9):
        x = digitos_cedula[i]
        if i % 2 == 0:
            x = x * 2
            if x > 9:
                x -= 9
        total += x
        """product = coefficients[i] * digitos_cedula[i]
        if product >= 10:
            product -= 9
        total += product"""

    digito_verificador = 10 - (total % 10)
    if digito_verificador == 10:
        digito_verificador = 0

    return digito_verificador == digitos_cedula[9]


@log_event("submit_request")
@rol_requerido('Administrador')
@login_required
def editarPersonalAdmi(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Usuario actualizado correctamente!')
            return redirect('admiManage')
        else:
            messages.error(request, 'Error al actualizar usuario. Por favor, revisa el formulario.')
        return redirect('admiManage')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'admiManage.html',
                  {'form': form, 'personalAdministrativo': Usuario.objects.all()})


@log_event("delete_user")
@rol_requerido('Administrador')
@login_required
def eliminarUsuario(request, id):
    usuario = Usuario.objects.get(id=id)
    usuario.delete()
    return redirect('admiManage')


@rol_requerido('Administrador')
@login_required
def admiManage(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    personalAdministrativo = Usuario.objects.all()
    return render(request, 'admiManage.html',
                  {"personalAdministrativo": personalAdministrativo, 'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def homeAdministrador(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'homeAdministrador.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def perfilAdministrador(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'perfilAdministrador.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def editarPerfilAdmi(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, '¡El perfil actualizado correctamente!')
            return redirect('perfilAdministrador')
        else:
            messages.error(request, 'Error al actualizar el perfil. Por favor, revisa el formulario.')
        return redirect('perfilAdministrador')
    else:
        form = PerfilForm(request.POST, instance=perfil)
    return render(request, 'perfilAdministrador.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Personal')
@login_required
def homePersonal(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'homePersonal.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def mostrarPeriodos(request):  # Vista general de Periodos
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    periodos = PeriodoAcademico.objects.all()
    # messages.success(request, '!Lista actualizada!')
    return render(request, "gestionPeriodoHome.html", {"periodos": periodos, 'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def guardar_editar_Periodos(request):  # Vista para editar o agregar
    periodos = PeriodoAcademico.objects.all()
    messages.success(request, '!Lista actualizada!')
    return render(request, "gestionPeriodo.html", {"periodos": periodos})


@rol_requerido('Administrador')
@login_required
def obtener_eventos(request):  # Método para cargar los periodos registrados en calendar
    periodos = PeriodoAcademico.objects.all()
    eventos = []

    for periodo in periodos:
        eventos.append({
            'title': periodo.nombre,
            'start': periodo.fechaInicio.isoformat(),
            'end': (periodo.fechaFin + timedelta(days=1)).isoformat(),
            'allDay': True,
        })

    return JsonResponse(eventos, safe=False)


@rol_requerido('Administrador')
@login_required
def registrarPeriodo(request):
    # Se los recibe como strings
    fechaI_str = request.POST.get('fecha_inicio')
    fechaF_str = request.POST.get('fecha_fin')

    # Se los convierte
    fechaI = datetime.strptime(fechaI_str, '%Y-%m-%d').date()
    fechaF = datetime.strptime(fechaF_str, '%Y-%m-%d').date()
    nombreP = PeriodoAcademico.fijarNombre(fechaI, fechaF)

    # Condicional para guardar o editar
    try:  # Si puede convertir el id a entero, existe, debe actualizar
        idP = int(request.POST['txtId'])

        periodos_antiguos = PeriodoAcademico.objects.all().exclude(id=idP)
        if periodos_antiguos.exists():
            for periodo in periodos_antiguos:
                if periodo.fechaInicio <= fechaI <= periodo.fechaFin or periodo.fechaInicio <= fechaF <= periodo.fechaFin:
                    messages.error(request, '¡Las fechas coinciden con períodos anteriores. Revise!')
                    return redirect('/mostrarPeriodos/')

        periodo = PeriodoAcademico.objects.get(id=idP)
        periodo.fechaInicio = fechaI
        periodo.fechaFin = fechaF
        periodo.nombre = nombreP
        periodo.save()
    except ValueError:  # Si devuelve un ID nulo, crear

        periodos_antiguos = PeriodoAcademico.objects.all()
        if periodos_antiguos.exists():
            for periodo in periodos_antiguos:
                if periodo.fechaInicio <= fechaI <= periodo.fechaFin or periodo.fechaInicio <= fechaF <= periodo.fechaFin:
                    messages.error(request, '¡Las fechas coinciden con períodos anteriores. Revise!')
                    return redirect('/mostrarPeriodos/')

        periodo = PeriodoAcademico.objects.create(fechaInicio=fechaI, fechaFin=fechaF, nombre=nombreP)
        for i in range(1, 10):
            ciclo = Ciclo.objects.create(idPeriodo=periodo, numero=i)

    messages.success(request, '¡Período registrado correctamente!')
    return redirect('/mostrarPeriodos/')


@rol_requerido('Personal')
@login_required
def sugerenciaPersonal(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    if request.method == 'POST':
        try:
            sugerencia = Sugerencia.objects.create(
                asunto=request.POST['asunto'],
                descripcion=request.POST['descripcion'],
                usuario=request.user
            )
            messages.success(request, 'Sugerencia enviada con éxito.')
            return redirect('sugerenciaPersonal')
        except Exception as e:
            print(f'Ocurrió un error: {str(e)}')
            messages.error(request, f'Ocurrió un error: {str(e)}')
            return redirect('sugerenciaPersonal')

    return render(request, 'sugerencia.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Personal')
@login_required
def graficaPrediccion(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'InterfazPrediccion.html', {'usuario': usuario, 'perfil': perfil})


@login_required
def index(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'InterfazPrediccion.html', {'usuario': usuario, 'perfil': perfil})


@login_required
def index1(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'InterfazCiclos.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Personal')
@login_required
def prediccionCiclos(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'InterfazCiclos.html', {'usuario': usuario, 'perfil': perfil})


def generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, valorFinalHistorico):
    chart = {
        'xAxis': {
            'type': 'category',
            'data': listaTNombres,
            'name': 'periodos'
        },
        'yAxis': {
            'type': 'value',
            'name': 'Nro Estudiantes',
            'nameTextStyle': {
                'left': '25%',
                'bottom': '89%',
                'padding': [0, 0, 0, -20],
                'fontSize': 12
            }
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {
                'type': 'cross',
                'label': {
                    'backgroundColor': '#6a7985'
                }
            }
        },
        'legend': {
            'data': ['Foraneos', 'Desertores', 'Aprobados', 'Matriculados', 'Reprobados'],
            'bottom': '93%'
        },
        'toolbox': {
            'feature': {
                'saveAsImage': {}
            }
        },
        'dataZoom': {
            'type': 'slider',
            'start': 0,
            'end': 100
        },
        'animationDuration': 2000,
        'animationEasing': 'cubicInOut',
        'series': [
            {
                'name': 'Foraneos',
                'type': 'line',
                'smooth': True,
                'data': listaF,
                'markPoint': {
                    'data': [
                        {
                            'type': 'max',
                            'name': 'Último Valor Foraneos',
                            'xAxis': listaTNombres[-1],  # Último valor en el eje x
                            'yAxis': listaF[-1]  # Último valor en el eje y
                        }
                    ]
                }
            },
            {
                'name': 'Desertores',
                'type': 'line',
                'smooth': True,
                'areaStyle': {},
                'emphasis': {
                    'focus': 'series'
                },
                'data': listaD
            },
            {
                'name': 'Aprobados',
                'type': 'line',
                'smooth': True,
                'data': listaA
            },
            {
                'name': 'Matriculados',
                'type': 'line',
                'smooth': True,
                'data': listaM
            },
            {
                'name': 'Reprobados',
                'type': 'line',
                'smooth': True,
                'data': listaR
            },
            {
                'type': 'line',  # Puedes usar 'line' o 'scatter', dependiendo de cómo quieras representar el área
                'data': [],  # Deja vacío si solo estás usando esto para `markArea`
                'markArea': {
                    'itemStyle': {
                        'color': 'rgba(200, 200, 200, 0.4)'
                    },
                    'data': [
                        [
                            {
                                'name': "Datos Historicos",
                                'xAxis': listaTNombres[0]  # Primer valor de xAxis
                            },
                            {
                                'name': "Final Histórico",
                                'xAxis': valorFinalHistorico  # Último valor del área
                            }
                        ]
                    ]
                },
                'tooltip': {
                    'show': False  # Opcional: Desactiva el tooltip para esta serie
                }
            }
        ]
    }
    return chart


@require_http_methods(["GET", "POST"])
def get_chart(request):
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__isnull=True)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@login_required
def validarPeriodo(lista):
    len(lista)


@require_http_methods(["GET", "POST"])
def get_chart1(request):
    ciclo_ids = Ciclo.objects.filter(numero=1)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@require_http_methods(["GET", "POST"])
def get_chart2(request):
    ciclo_ids = Ciclo.objects.filter(numero=2)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@require_http_methods(["GET", "POST"])
def get_chart3(request):
    ciclo_ids = Ciclo.objects.filter(numero=3)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@require_http_methods(["GET", "POST"])
def get_chart4(request):
    ciclo_ids = Ciclo.objects.filter(numero=4)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@require_http_methods(["GET", "POST"])
def get_chart5(request):
    ciclo_ids = Ciclo.objects.filter(numero=5)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@require_http_methods(["GET", "POST"])
def get_chart6(request):
    ciclo_ids = Ciclo.objects.filter(numero=6)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@require_http_methods(["GET", "POST"])
def get_chart7(request):
    ciclo_ids = Ciclo.objects.filter(numero=7)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


@require_http_methods(["GET", "POST"])
def get_chart8(request):
    ciclo_ids = Ciclo.objects.filter(numero=8)
    estadisticasPeriodos = EstadisticaPeriodo.objects.filter(idCiclo__in=ciclo_ids)
    listaD = list(estadisticasPeriodos.values_list('numDesertores', flat=True))
    listaT = list(PeriodoAcademico.objects.values_list('fechaFin', flat=True))
    listaA = list(estadisticasPeriodos.values_list('numAprobados', flat=True))
    listaR = list(estadisticasPeriodos.values_list('numReprobados', flat=True))
    listaM = list(estadisticasPeriodos.values_list('numMatriculados', flat=True))
    listaF = list(estadisticasPeriodos.values_list('numForaneos', flat=True))
    listaTNombres = list(PeriodoAcademico.objects.values_list('nombre', flat=True))
    ultimoValorHistorico = listaTNombres[-1]
    if request.method == "POST":
        logger.info("Recibida solicitud POST char1")
        data = json.loads(request.body)
        selected_year = int(data.get('year'))
        logger.info(f"Año seleccionado: {selected_year}")
        listaDesetores, listaTiempo, listaReprobados, listaAprobados, listaMatriculados, listaForaneos = r.realizarPrediccion(
            listaD, listaT, listaR, listaA, listaM, listaF, selected_year)
        listaTNombresActuales = r.obtener_periodos(listaTNombres, selected_year)
        chart = generate_chart_data(listaTiempo, listaDesetores, listaAprobados, listaReprobados, listaMatriculados,
                                    listaForaneos, listaTNombresActuales, ultimoValorHistorico)
    else:
        logger.info("Recibida solicitud GET char1")
        chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF, listaTNombres, ultimoValorHistorico)
    return JsonResponse(chart)


def get_chart9(request):
    listaD = [73, 66, 74, 84, 65, 65, 84, 76, 62, 73, 63, 63, 70, 47, 49, 61, 57, 71, 58, 52, 83, 65, 68, 52, 62, 69]
    listaT = ['2023-04-29', '2020-07-24', '2022-07-02', '2022-08-28', '2021-06-15', '2022-01-03', '2022-04-17',
              '2022-10-02', '2022-12-31', '2022-05-25', '2021-08-24', '2021-05-14', '2020-01-28', '2022-03-08',
              '2022-10-05', '2020-04-19', '2023-08-19', '2023-11-08', '2021-02-26', '2020-03-02', '2021-10-22',
              '2023-03-11', '2023-10-16', '2022-07-01', '2023-10-06', '2020-10-27']
    listaA = [55, 71, 61, 64, 61, 87, 67, 56, 76, 55, 70, 47, 53, 70, 75, 69, 66, 64, 52, 60, 63, 79, 71, 49, 71, 63]
    listaR = [60, 74, 78, 77, 59, 64, 71, 78, 62, 65, 56, 55, 76, 82, 67, 78, 71, 61, 71, 84, 67, 84, 40, 76, 68, 64]
    listaM = [60, 74, 78, 77, 59, 64, 71, 78, 62, 65, 56, 55, 76, 82, 67, 78, 71, 61, 71, 84, 67, 84, 40, 76, 68, 64]
    listaF = [73, 66, 74, 84, 65, 65, 84, 76, 62, 73, 63, 63, 70, 47, 49, 61, 57, 71, 58, 52, 83, 65, 68, 52, 62, 69]
    chart = generate_chart_data(listaT, listaD, listaA, listaR, listaM, listaF)
    return JsonResponse(chart)


@rol_requerido('Personal')
@login_required
def modeloMatematico(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'modeloMatematicoInfo.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def variablesAdministrador(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'agregarDatos.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def listaSugerencias(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    sugerencias = Sugerencia.objects.all()
    if not sugerencias:
        messages.info(request, 'Ningun usuario ha enviado sugerencias')
    return render(request, 'listaSugerencia.html', {"sugerencias": sugerencias, 'usuario': usuario, 'perfil': perfil})


@rol_requerido('Personal')
@login_required
def mostrarDatosHistoricos(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    periodos = PeriodoAcademico.objects.all()

    # Arreglo para almacenar los periodos con sus estadísticas
    datos = []

    for periodo in periodos:
        estadisticas_ciclo = EstadisticaPeriodo.objects.filter(
            idCiclo__idPeriodo=periodo)  # Estadísticas asociadas con ciclos específicos

        # Estadística total del periodo, sin asociación con ciclos
        estadistica_general = EstadisticaPeriodo.objects.filter(idPeriodo=periodo, idCiclo=None).first()

        datos.append({
            'periodo': periodo,
            'estadisticas_ciclo': estadisticas_ciclo,
            'estadistica_general': estadistica_general
        })

    context = {
        'datos': datos,
        'usuario': usuario,
        'perfil': perfil
    }

    return render(request, "mostrarDatosHistoricos.html", context)


@rol_requerido('Administrador')
@login_required
def mostrarDatosHAuditoria(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    periodos = PeriodoAcademico.objects.all()

    datos = []
    for periodo in periodos:
        estadisticas_ciclo = EstadisticaPeriodo.objects.filter(
            idCiclo__idPeriodo=periodo
        )
        estadistica_general = EstadisticaPeriodo.objects.filter(
            idPeriodo=periodo, idCiclo=None
        ).first()

        if estadistica_general:
            administrador = str(estadistica_general.idAdministrador)
        else:
            administrador = 'Ninguno'

        datos.append({
            'periodo': periodo,
            'estadisticas_ciclo': estadisticas_ciclo,
            'estadistica_general': estadistica_general,
            'administrador': administrador
        })

    return render(request, "auditoríaDatosHReporte.html", {
        'datos': datos,
        'usuario': usuario,
        'perfil': perfil,
    })


@login_required
def mostrarDatosPeriodo(request, id):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    estadisticasPeriodo = EstadisticaPeriodo.objects.filter(idCiclo__idPeriodo=id)
    # IDEA: Mostrar todos los periodos en tabla y mostrar error en los que no tengan datos asociados
    """if not estadisticasPeriodo.exists():
        messages.error(request, '¡Las fechas coinciden con períodos anteriores. Revise!')
        return redirect('/mostrarDatosHistoricos/')"""
    return render(request, "mostrarDatosHistoricos.html",
                  {"estadisticasPeriodo": estadisticasPeriodo, 'usuario': usuario, 'perfil': perfil})


@rol_requerido('Personal')
@login_required
def ayuda(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'ayuda.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Administrador')
@login_required
def agregarDatos(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    if request.method == 'POST':
        id_periodo = request.POST.get('idPeriodo')

        # Verificar si ya existen registros con el mismo idPeriodo
        if EstadisticaPeriodo.objects.filter(idPeriodo=id_periodo).exists():
            messages.error(request,
                           'Ya existen datos guardados para este periodo académico. No se pueden agregar nuevos datos.')
            return redirect('agregarDatos')

        # Validar que todos los campos no estén vacíos
        all_filled = True
        for tipo in ['matriculados', 'aprobados', 'reprobados', 'desertores', 'foraneos']:
            for i in range(1, 10):
                if not request.POST.get(f'{tipo}_{i}', ''):
                    all_filled = False
                    break
            if not all_filled:
                break

        if not all_filled:
            messages.error(request, 'Todos los campos deben ser llenados. No se pueden dejar campos vacíos.')
            return redirect('agregarDatos')

        # Guardar el registro con los datos totales asociados al idPeriodo
        total_matriculados = sum(int(request.POST.get(f'matriculados_{i}', 0)) for i in range(1, 10))
        total_aprobados = sum(int(request.POST.get(f'aprobados_{i}', 0)) for i in range(1, 10))
        total_reprobados = sum(int(request.POST.get(f'reprobados_{i}', 0)) for i in range(1, 10))
        total_desertores = sum(int(request.POST.get(f'desertores_{i}', 0)) for i in range(1, 10))
        total_foraneos = sum(int(request.POST.get(f'foraneos_{i}', 0)) for i in range(1, 10))

        estadistica_total = EstadisticaPeriodo(
            numMatriculados=total_matriculados,
            numAprobados=total_aprobados,
            numReprobados=total_reprobados,
            numDesertores=total_desertores,
            numForaneos=total_foraneos,
            idPeriodo=PeriodoAcademico.objects.get(id=id_periodo),
            idAdministrador=request.user
        )
        estadistica_total.save()

        # Obtener ciclos asociados con el idPeriodo
        ciclos = Ciclo.objects.filter(idPeriodo_id=id_periodo)

        # Crear los registros para cada ciclo asociado al idPeriodo
        for ciclo in ciclos:
            ciclo_numero = ciclo.numero
            num_matriculados = request.POST.get(f'matriculados_{ciclo_numero}', 0)
            num_aprobados = request.POST.get(f'aprobados_{ciclo_numero}', 0)
            num_reprobados = request.POST.get(f'reprobados_{ciclo_numero}', 0)
            num_desertores = request.POST.get(f'desertores_{ciclo_numero}', 0)
            num_foraneos = request.POST.get(f'foraneos_{ciclo_numero}', 0)

            estadistica_ciclo = EstadisticaPeriodo(
                numMatriculados=num_matriculados,
                numAprobados=num_aprobados,
                numReprobados=num_reprobados,
                numDesertores=num_desertores,
                numForaneos=num_foraneos,
                idCiclo=ciclo,
                idAdministrador=request.user
            )
            estadistica_ciclo.save()

        messages.success(request, 'Datos guardados correctamente.')
        return redirect('agregarDatos')
    else:
        periodos = PeriodoAcademico.objects.all()
        print(periodos)
        return render(request, 'agregarDatos.html', {'periodos': periodos, 'usuario': usuario, 'perfil': perfil})


@login_required
def cargar_datos(request, periodo_id):
    try:
        # Obtener el registro del periodo
        periodo_data = EstadisticaPeriodo.objects.get(idPeriodo_id=periodo_id)

        # Obtener los ciclos asociados al periodo
        ciclos = Ciclo.objects.filter(idPeriodo_id=periodo_id)
        print(ciclos)
        # Obtener los registros de estadística para los ciclos
        ciclos_data = {ciclo_data.idCiclo.numero: ciclo_data for ciclo_data in
                       EstadisticaPeriodo.objects.filter(idCiclo_id__in=ciclos)}

        # Preparar la respuesta
        response_data = {
            "total_matriculados": periodo_data.numMatriculados,
            "total_aprobados": periodo_data.numAprobados,
            "total_reprobados": periodo_data.numReprobados,
            "total_desertores": periodo_data.numDesertores,
            "total_foraneos": periodo_data.numForaneos,
            **{
                f"ciclo_{ciclo.numero}": {
                    "matriculados": ciclos_data[ciclo.numero].numMatriculados if ciclo.numero in ciclos_data else 0,
                    "aprobados": ciclos_data[ciclo.numero].numAprobados if ciclo.numero in ciclos_data else 0,
                    "reprobados": ciclos_data[ciclo.numero].numReprobados if ciclo.numero in ciclos_data else 0,
                    "desertores": ciclos_data[ciclo.numero].numDesertores if ciclo.numero in ciclos_data else 0,
                    "foraneos": ciclos_data[ciclo.numero].numForaneos if ciclo.numero in ciclos_data else 0,
                } for ciclo in ciclos
            }
        }

        return JsonResponse(response_data, safe=False)
    except EstadisticaPeriodo.DoesNotExist:
        return JsonResponse({"error": "No data found"}, status=404)


@login_required
def guardarcambios_datos(request, periodo_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)

            total_matriculados = data.get('total_matriculados', 0)
            total_aprobados = data.get('total_aprobados', 0)
            total_reprobados = data.get('total_reprobados', 0)
            total_desertores = data.get('total_desertores', 0)
            total_foraneos = data.get('total_foraneos', 0)

            print("Totales:", total_matriculados, total_aprobados, total_reprobados, total_desertores, total_foraneos)

            periodo_academico = get_object_or_404(PeriodoAcademico, pk=periodo_id)

            # Actualizar o crear el registro del periodo
            EstadisticaPeriodo.objects.update_or_create(
                idPeriodo_id=periodo_academico.id,
                idCiclo_id=None,
                defaults={
                    'numMatriculados': total_matriculados,
                    'numAprobados': total_aprobados,
                    'numReprobados': total_reprobados,
                    'numDesertores': total_desertores,
                    'numForaneos': total_foraneos,
                    'idAdministrador_id': request.user.id
                }
            )

            ciclos = data.get('ciclos', [])
            print("Ciclos recibidos:", ciclos)

            for ciclo_data in ciclos:
                ciclo_numero = ciclo_data.get('numero')
                print(f"Procesando ciclo {ciclo_numero}: {ciclo_data}")

                ciclo = get_object_or_404(Ciclo, idPeriodo_id=periodo_academico.id, numero=ciclo_numero)

                EstadisticaPeriodo.objects.update_or_create(
                    idCiclo_id=ciclo.id,
                    idPeriodo_id=None,
                    defaults={
                        'numMatriculados': ciclo_data.get('matriculados', 0),
                        'numAprobados': ciclo_data.get('aprobados', 0),
                        'numReprobados': ciclo_data.get('reprobados', 0),
                        'numDesertores': ciclo_data.get('desertores', 0),
                        'numForaneos': ciclo_data.get('foraneos', 0),
                        'idAdministrador_id': request.user.id
                    }
                )

            return JsonResponse({'message': 'Datos guardados correctamente.', 'status': 'success'})
        except Exception as e:
            print("Error al guardarrr los datos:", str(e))
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


@rol_requerido('Administrador')
@login_required
def ayudaAdmin(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'ayudaAdministrador.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Personal')
@login_required
def perfilPersonal(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'perfilPersonal.html', {'usuario': usuario, 'perfil': perfil})


@rol_requerido('Personal')
@login_required
def editarPerfilPersonal(request):
    usuario = request.user
    perfil = get_object_or_404(Perfil, usuario=usuario)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, '¡El perfil actualizado correctamente!')
            return redirect('perfilPersonal')
        else:
            messages.error(request, 'Error al actualizar el perfil. Por favor, revisa el formulario.')
        return redirect('perfilPersonal')
    else:
        form = PerfilForm(request.POST, instance=perfil)
    return render(request, 'perfilPersonal.html', {'usuario': usuario, 'perfil': perfil})


def csrf_failure(request, reason=""):
    """
    Esta vista se invoca cuando falla la validación CSRF.
    """
    tipo = "missing_token" if "CSRF" in reason and "present" not in reason else "invalid_token"
    Evento.objects.create(
        sesion_id=request.session.session_key or "",
        tipo_evento=tipo,
        datos={
            "path": request.path,
            "reason": reason,
            "username": request.user.username if request.user.is_authenticated else None
        },
        fecha_hora=timezone.now()
    )
    return render(request, "403csrf.html", status=403)


@rol_requerido('Administrador', 'Personal')
@log_event("sensitive_action")
@login_required
def change_password(request):
    if RolPersona.objects.filter(usuario=request.user, rol__nombre='Administrador').exists():
        template_name = 'cambioClaveAdmin.html'
        redirect_to = 'perfilAdministrador'
    else:
        template_name = 'cambioClave.html'
        redirect_to = 'perfilPersonal'

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Tu contraseña se ha cambiado correctamente!')
            return redirect(redirect_to)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, template_name, {'form': form})


@login_required
@rol_requerido('Administrador')
@rol_requerido('Administrador')
def list_alertas(request):
    # 1) traer las alertas
    alertas = Alerta.objects.select_related('evento').order_by('-fecha_generada')[:200]

    # 2) agrupar *todos* los eventos de cada sesión que tenga alerta
    eventos_por_sid = {}
    for alerta in alertas:
        sid = alerta.sesion_id
        if sid not in eventos_por_sid:
            eventos_por_sid[sid] = list(
                Evento.objects
                .filter(sesion_id=sid)
                .order_by('fecha_hora')
            )

    return render(request, "list_alertas.html", {
        "alertas": alertas,
        "eventos_por_sid": eventos_por_sid,
    })
