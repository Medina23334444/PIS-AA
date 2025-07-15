from django.db.models.signals import post_save
from django.dispatch import receiver

from .csrf_detector import evaluar_evento
from .models import Usuario, Perfil, Evento
from datetime import date


@receiver(post_save, sender=Usuario)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(
            usuario=instance,
            fechaNacimiento=date.today(),
            descripcion='',
            usuarioInstagram='',
            usuarioFacebook='',
            usuarioTwitter=''
        )


@receiver(post_save, sender=Evento)
def on_evento_save(sender, instance, created, **kwargs):
    if created:
        evaluar_evento(instance)
