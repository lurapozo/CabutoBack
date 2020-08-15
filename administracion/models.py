from django.db import models

# Create your models here.
class Empresa(models.Model):
	id_empresa = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=100)
	logo = models.BinaryField()
	razon_social=models.CharField(max_length=300)
	ruc_cedula=models.CharField(max_length=13)

def __str__(self):
	return self.nombre