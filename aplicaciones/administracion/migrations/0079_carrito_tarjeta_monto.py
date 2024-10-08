# Generated by Django 2.2.7 on 2022-09-30 22:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0078_tarjeta_producto_cliente_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrito_Tarjeta_Monto',
            fields=[
                ('id_carritoxtarjeta', models.AutoField(primary_key=True, serialize=False)),
                ('precio', models.FloatField(default=0)),
                ('id_carrito', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Carrito')),
                ('id_tarjeta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Tarjeta_Monto')),
            ],
        ),
    ]
