# Generated by Django 5.0.6 on 2025-07-14 14:40

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_alter_perfil_fotoperfil'),
    ]

    operations = [
        migrations.CreateModel(
            name='Automata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('estados', models.JSONField()),
                ('alfabeto', models.JSONField()),
                ('inicial', models.CharField(max_length=20)),
                ('finales', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sesion_id', models.CharField(max_length=128, verbose_name='ID de sesión')),
                ('tipo_evento', models.CharField(max_length=50, verbose_name='Tipo de evento')),
                ('fecha_hora', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha y hora')),
                ('datos', models.JSONField(blank=True, null=True, verbose_name='Datos adicionales')),
            ],
        ),
        migrations.CreateModel(
            name='Alerta',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sesion_id', models.CharField(max_length=128, verbose_name='ID de sesión')),
                ('fecha_generada', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de generación')),
                ('probabilidades', models.JSONField(verbose_name='Distribución de probabilidades')),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.evento', verbose_name='Evento relacionado')),
            ],
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(max_length=20)),
                ('evento', models.CharField(max_length=50)),
                ('destino', models.CharField(max_length=20)),
                ('prob', models.FloatField()),
                ('automaton', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transitions', to='tasks.automata')),
            ],
            options={
                'unique_together': {('automaton', 'estado', 'evento', 'destino')},
            },
        ),
    ]
