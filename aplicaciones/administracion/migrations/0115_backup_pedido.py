# Generated by Django 2.2.7 on 2023-03-15 22:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0114_auto_20230305_1542'),
    ]

    operations = [
        migrations.CreateModel(
            name='Backup_Pedido',
            fields=[
                ('id_backpedido', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('tipo_entrega', models.CharField(default='Domicilio', max_length=100)),
                ('tipo_pago', models.CharField(default='Efectivo', max_length=100)),
                ('total', models.FloatField()),
                ('nombreTarjeta', models.CharField(default='', max_length=100, null=True)),
                ('numeroTarjeta', models.CharField(default='', max_length=100, null=True)),
                ('clienteid', models.IntegerField()),
                ('clientenombre', models.CharField(max_length=100)),
                ('clienteapellido', models.CharField(max_length=100)),
                ('telefono', models.CharField(default='NONE', max_length=100)),
                ('cedula', models.CharField(max_length=10)),
                ('id_direccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.DireccionEntrega')),
                ('id_pedido', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Pedido')),
            ],
        ),
    ]
