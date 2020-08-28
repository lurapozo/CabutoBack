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


class Establecimiento(models.Model):
	id_establecimiento=models.AutoField(primary_key=True)
	nombre=models.CharField(max_length=100)
	direccion=models.CharField(max_length=100)
	telefono=models.CharField(max_length=100)
	latitud=models.FloatField()
	longitud=models.FloatField()
	encargado=models.CharField(max_length=100)
	image=models.BinaryField()
	estado=models.CharField(max_length=1)

def __str__(self):
	return self.nombre

class Categoria(models.Model):
	id_categoria=models.AutoField(primary_key=True)
	nombre = models.TextField()
	image=models.BinaryField()
	id_establecimiento=models.ForeignKey(Establecimiento,on_delete=models.SET_NULL, null=True)

def __str__(self):
	return self.nombre

class Producto(models.Model):
	id_producto = models.AutoField(primary_key=True)
	nombre=models.CharField(max_length=100)
	descripcion=models.CharField(max_length=100)
	precio=models.FloatField()
	image=models.BinaryField(blank = True, null = True)
	estado=models.CharField(max_length=1)
	id_categoria=models.ForeignKey(Categoria,on_delete=models.SET_NULL, null=True)

def __str__(self):
	return self.nombre