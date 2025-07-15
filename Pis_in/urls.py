from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from Pis_in import settings
from tasks import views

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', views.home, name='home'),
                  path('admiManage/', views.admiManage, name='admiManage'),
                  path('iniciarSesion/', views.iniciarSesion, name='iniciar_sesion'),
                  path('editarPersonalAdmi/<str:id>/', views.editarPersonalAdmi, name='editarPersonalAdmi'),
                  path('registrarUsuario/', views.registrarUsuario, name='registrarUsuario'),
                  path('eliminarUsuario/<id>', views.eliminarUsuario, name='eliminarUsuario'),
                  path('homeAdministrador/', views.homeAdministrador, name='homeAdministrador'),
                  path('perfilAdministrador/', views.perfilAdministrador, name='perfilAdministrador'),
                  path('homePersonal/', views.homePersonal, name='homePersonal'),
                  path('mostrarPeriodos/', views.mostrarPeriodos, name='mostrarPeriodos'),
                  path('gestionPeriodos/', views.guardar_editar_Periodos, name='gestionPeriodos'),
                  path('obtener_eventos/', views.obtener_eventos),
                  path('registrarPeriodo/', views.registrarPeriodo),
                  path('cerrar_sesion', views.cerrarSesion, name='cerrar_sesion'),
                  path('Prediccion/', views.graficaPrediccion, name='GraficaPrediccion'),
                  path('api/', include('tasks.urls')),
                  path('prediccionCiclos/', views.prediccionCiclos, name="prediccionCiclos"),
                  path('sugerencia/', views.sugerenciaPersonal, name='sugerenciaPersonal'),
                  path('modeloMatematico/', views.modeloMatematico, name='modeloMatematico'),
                  path('agregarDatos/', views.agregarDatos, name='agregarDatos'),
                  path('cargarDatos/<int:periodo_id>/', views.cargar_datos, name='cargar_datos'),
                  path('guardarcambiosDatos/<int:periodo_id>/', views.guardarcambios_datos,
                       name='guardarcambios_datos'),
                  path('mostrarDatosHistoricos/', views.mostrarDatosHistoricos, name='mostrarDatosHistoricos'),
                  path('mostrarDatosPeriodo/<id>', views.mostrarDatosPeriodo, name='mostrarDatosPeriodo'),
                  path('listaSugerencias/', views.listaSugerencias, name='listaSugerencias'),
                  path('ayuda/', views.ayuda, name='ayuda'),
                  path('ayudaAdministrador/', views.ayudaAdmin, name='ayudaAdministrador'),
                  path('perfilPersonal/', views.perfilPersonal, name='perfilPersonal'),
                  path('editarPerfilAdmi/', views.editarPerfilAdmi, name='editarPerfilAdmi'),
                  path('editarPerfilPersonal/', views.editarPerfilPersonal, name='editarPerfilPersonal'),
                  path('mostrarDatosHAuditoria/', views.mostrarDatosHAuditoria, name='mostrarDatosHAuditoria'),
                  path('change-password/', views.change_password, name='change_password'),
                  path("alertas/", views.list_alertas, name="list_alertas"),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
