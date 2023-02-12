# Generated by Django 2.2.7 on 2023-02-08 05:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0107_canal_canalmensaje_canalusuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='canalmensaje',
            name='usuario',
        ),
        migrations.AddField(
            model_name='canalmensaje',
            name='usuario_admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='administracion.Empleado'),
        ),
        migrations.AddField(
            model_name='canalmensaje',
            name='usuario_cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='administracion.Usuario'),
        ),
    ]