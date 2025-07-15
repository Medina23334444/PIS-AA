from django.contrib import admin
from .models import Rol, Usuario, RolPersona, PeriodoAcademico, EstadisticaPeriodo, Automata, Transition, Alerta

admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(RolPersona)
admin.site.register(PeriodoAcademico)
admin.site.register(EstadisticaPeriodo)


@admin.register(Automata)
class AutomataAdmin(admin.ModelAdmin):
    list_display = ("nombre", "inicial")


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    list_display = ("automaton", "estado", "evento", "destino", "prob")


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ("sesion_id", "evento", "fecha_generada")
    list_filter = ("fecha_generada",)
    search_fields = ("sesion_id",)
