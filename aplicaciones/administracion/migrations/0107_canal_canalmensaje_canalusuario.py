# Generated by Django 2.2.7 on 2023-02-08 04:31

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0106_cliente_ban'),
    ]

    operations = [
        migrations.CreateModel(
            name='Canal',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tiempo', models.DateTimeField(auto_now_add=True)),
                ('usuario_admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='administracion.Empleado')),
                ('usuario_cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='administracion.Cliente')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CanalUsuario',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tiempo', models.DateTimeField(auto_now_add=True)),
                ('canal', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='administracion.Canal')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administracion.Usuario')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CanalMensaje',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tiempo', models.DateTimeField(auto_now_add=True)),
                ('texto', models.TextField()),
                ('check_leido', models.BooleanField()),
                ('esAdmin', models.BooleanField()),
                ('canal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administracion.Canal')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administracion.Usuario')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]