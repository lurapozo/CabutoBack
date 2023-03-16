import secrets
import random
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.models import AbstractUser

#import para Chat
from django.db.models import Count
import uuid


# Create your models here.
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    rol=models.CharField(max_length=150,default = "cliente")
    cedula=models.CharField(max_length=10)
    correo=models.EmailField(unique=True)
    contrasena=models.CharField(max_length=64, editable=True)
    foto=models.ImageField(default = " ")
    registro = models.DateTimeField(auto_now_add=True)
    codigo_unico=models.CharField(max_length=100,null=True)
    token=models.CharField(max_length=500,default = "0000")
    def __str__(self):
        return self.correo

    @property
    def photo_url(self):
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url

class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    apellido=models.CharField(max_length=100)
    rol=models.CharField(max_length=150,default = "administrador")
    cedula=models.CharField(max_length=10)
    telefono=models.CharField(max_length=10)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, )
    def __str__(self):
        return self.nombre +" "+ self.apellido


class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    logo = models.ImageField()
    razon_social=models.CharField(max_length=300)
    ruc_cedula=models.CharField(max_length=13)
    def __str__(self):
        return self.nombre

class RedSocial(models.Model):
    id_red=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    enlace=models.CharField(max_length=400)
    icono=models.ImageField()
    id_empresa=models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    @property
    def photo_url(self):
        if self.icono and hasattr(self.icono, 'url'):
            return self.icono.url

class Establecimiento(models.Model):
    id_establecimiento=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    direccion=models.CharField(max_length=100)
    telefono=models.CharField(max_length=100)
    referencia=models.CharField(max_length=200,default = "")
    latitud=models.FloatField()
    longitud=models.FloatField()
    encargado=models.CharField(max_length=100)
    image=models.ImageField()
    estado=models.CharField(max_length=1,default = "A")
    def __str__(self):
        return self.nombre

class Horario(models.Model):
    id_horario=models.AutoField(primary_key=True)
    dia=models.CharField(max_length=100)
    hora_inicio=models.CharField(max_length=100)
    hora_fin=models.CharField(max_length=100)
    estado=models.CharField(max_length=1,default = "A")
    establecimiento=models.ForeignKey(Establecimiento,on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.dia

class Categoria(models.Model):
    id_categoria=models.AutoField(primary_key=True)
    nombre = models.TextField()
    image=models.ImageField()
    id_establecimiento=models.ForeignKey(Establecimiento,on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.nombre

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url



class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    descripcion=models.CharField(max_length=300)
    precio=models.FloatField()
    image=models.ImageField()
    estado=models.CharField(max_length=1,default = "A")
    id_categoria=models.ForeignKey(Categoria,on_delete=models.SET_NULL, null=True)
    stock_disponible=models.IntegerField()
    puntos=models.IntegerField(default = 0)
    def __str__(self):
        return self.nombre

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    apellido=models.CharField(max_length=100)
    metodo_pago= models.CharField(max_length=100, default = "Efectivo")
    telefono =models.CharField(max_length=100, default = "NONE")
    direccion = models.CharField(max_length=100, default = "NONE")
    fecha_Nac=models.DateField(default=datetime.now)
    usuario = models.ForeignKey(Usuario,on_delete=models.SET_NULL,null=True)
    puntos=models.IntegerField(default = 0)
    ban=models.IntegerField(default = 0)
    numTarjetas=models.IntegerField(default = 0,null=True)
    monthCard=models.DateField(default=now,null=True)
    version =models.IntegerField(default = 0,null=True)
    def __str__(self):
        return '%s %s' %(self.nombre, self.apellido)

class DireccionEntrega(models.Model):
    id_direccion=models.AutoField(primary_key=True)
    direccion=models.CharField(max_length=200)
    descripcion=models.CharField(max_length=250)
    latitud=models.FloatField()
    longitud=models.FloatField()
    cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL,null=True)
    envio=models.FloatField()

class ZonaEnvio(models.Model):
    EstadoZona= (
        ('A', 'Activo'),
        ('I', 'Inactivo'),
    )
    id_zona=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    color=models.CharField(max_length=50)
    zona=models.CharField(max_length=3000)
    envio=models.FloatField()
    estado= models.CharField(max_length=1,choices=EstadoZona,default='A',)

class Pedido(models.Model):
    EstadoPedido = (
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Recibido', 'Recibido'),
        ('Proceso', 'Proceso'),
        ('Devuelto', 'Devuelto'),
        ('Anulado', 'Anulado'),
    )
    id_pedido=models.AutoField(primary_key=True)
    fecha=models.DateTimeField(default=now)
    tipo_entrega= models.CharField(max_length=100, default = "Domicilio")
    tipo_pago= models.CharField(max_length=100, default = "Efectivo")
    subtotal=models.FloatField()
    envio=models.FloatField()
    iva=models.FloatField()
    descuento=models.FloatField()
    total=models.FloatField()
    observacion= models.CharField(max_length=400)
    estado= models.CharField(max_length=10,choices=EstadoPedido,default='Recibido',)
    pagado= models.BooleanField(default=False)
    cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL,null=True)
    establecimiento=models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True)
    direccion=models.ForeignKey(DireccionEntrega, on_delete=models.SET_NULL, null=True)
    puntos=models.IntegerField(default=0)
    direccion=models.ForeignKey(DireccionEntrega, on_delete=models.SET_NULL, null=True)
    nombreTarjeta=models.CharField(max_length=100, default = "", null=True)
    numeroTarjeta=models.CharField(max_length=100, default = "", null=True)

class TransaccionPedido(models.Model):
    id_transaccion=models.AutoField(primary_key=True)
    transaccion=models.CharField(max_length=100)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class CalificacionPedido(models.Model):
    id_calificacion=models.AutoField(primary_key=True)
    calificacion=models.IntegerField(default=5)
    justificacion=models.CharField(max_length=500)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Repartidor(models.Model):
    id_repartidor=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=120)
    apellido=models.CharField(max_length=120)
    telefono=models.CharField(max_length=120)
    token=models.CharField(max_length=120)
    estado=models.CharField(max_length=120)

class Repartidor_Pedido(models.Model):
    id_repedido = models.AutoField(primary_key=True)
    id_repartidor = models.ForeignKey(Repartidor,on_delete=models.SET_NULL, null=True)
    id_pedido = models.ForeignKey(Pedido,on_delete=models.SET_NULL, null=True)
    hora_inicio = models.DateTimeField(default=now)
    hora_fin = models.DateTimeField(default=now)

class Combo(models.Model):
    id_combo=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    imagen=models.ImageField()
    precio_total=models.FloatField()
    estado=models.CharField(max_length=100,default = "A")
    cantidad_disponible=models.IntegerField()
    cantidad_despachada=models.IntegerField()
    fecha_inicio=models.DateField()
    fecha_fin=models.DateField()
    id_establecimiento=models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.nombre

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


class Combo_Producto(models.Model) :
    id_comboxproducto=models.AutoField(primary_key=True)
    cantidad=models.IntegerField()
    id_combo=models.ForeignKey(Combo, on_delete=models.SET_NULL, null=True)
    id_producto=models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    id_establecimiento=models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True)

class Carrito(models.Model):
    id_carrito=models.AutoField(primary_key=True)
    precio_total=models.FloatField(default=0)
    tiene_combo= models.BooleanField(default=False)
    tiene_oferta=models.BooleanField(default=False)
    cantidad_disponible=models.IntegerField(default=0)
    cantidad_despachada=models.IntegerField(default=0)
    fecha_inicio=models.DateField(default=datetime.now)
    fecha_fin=models.DateField(default=datetime.now)
    id_cliente=models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)

class Detalle_Carrito(models.Model):
    id_detallexcarrito=models.AutoField(primary_key=True)
    cantidad=models.IntegerField(default=0)
    precio=models.FloatField(default=0)
    id_producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)


class Establecimiento_Producto(models.Model):
    id_estabxprod=models.AutoField(primary_key=True)
    stock_disponible=models.IntegerField()
    stock_despacho=models.IntegerField()
    id_establecimiento=models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True)
    id_producto=models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)


class Politica(models.Model):
    id_politica=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100,null=True)
    detalle=models.TextField()
    fecha=models.DateField(default=datetime.now)
    id_empresa=models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)

class Reclamo(models.Model):
    id_reclamo=models.AutoField(primary_key=True)
    image=models.ImageField()
    descripcion=models.CharField(max_length=500)
    id_empresa=models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


class Notificacion(models.Model):
    id_notificacion=models.AutoField(primary_key=True)
    asunto=models.CharField(max_length=100)
    mensaje=models.CharField(max_length=500)
    image=models.ImageField()
    registro = models.DateTimeField(auto_now_add=True)
    tipo=models.CharField(max_length=100)
    estado=models.CharField(max_length=500,default="NOT")
    id_establecimiento=models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.asunto

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

class Oferta(models.Model):
    id_oferta = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=300)
    descripcion = models.CharField(max_length=300)
    precioAntes = models.FloatField(default = 0.0)
    precio = models.FloatField(default=0)
    cantidad = models.IntegerField(default=0)
    image = models.ImageField()
    estado=models.CharField(max_length=1,default = "A")
    id_establecimiento = models.ForeignKey(Establecimiento,on_delete=models.SET_NULL, null=True)
    fecha_inicio = models.DateField()
    fecha_fin=models.DateField()
    def __str__(self):
        return self.nombre

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

class Carrito_Oferta(models.Model):
    id_carritoxoferta=models.AutoField(primary_key=True)
    cantidad=models.IntegerField(default=0)
    precio=models.FloatField(default=0)
    id_oferta = models.ForeignKey(Oferta, on_delete=models.SET_NULL, null=True)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)

class Carrito_Combo(models.Model):
    id_carritoxcombo=models.AutoField(primary_key=True)
    cantidad=models.IntegerField(default=0)
    precio=models.FloatField(default=0)
    id_combo = models.ForeignKey(Combo, on_delete=models.SET_NULL, null=True)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)


class Cupones(models.Model):
    id_cupon=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    descripcion=models.CharField(max_length=100)
    estado=models.CharField(max_length=1,default = "A")
    tipo=models.CharField(max_length=1,default = "M")
    cantidad=models.IntegerField()
    precio = models.FloatField(default=0)
    fecha_inicio=models.DateField()
    fecha_fin=models.DateField()
    image = models.ImageField()
    id_establecimiento=models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

class Cupones_Monto(models.Model):
    id_cuponesmonto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    monto = models.FloatField()
    id_cupon = models.ForeignKey(Cupones,on_delete=models.SET_NULL, null=True)

class Cupones_Producto(models.Model):
    id_cuponesproducto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    id_cupon = models.ForeignKey(Cupones,on_delete=models.SET_NULL, null=True)
    id_producto = models.ForeignKey(Producto,on_delete=models.SET_NULL, null=True)
    cantidad=models.IntegerField(default = 1)

class Cupones_Cliente(models.Model):
    id_cuponxcliente =  models.AutoField(primary_key=True)
    id_cupon = models.ForeignKey(Cupones,on_delete=models.SET_NULL, null=True)
    id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL, null=True)
    estado=models.CharField(max_length=1,default = "A")

class Carrito_Cupones(models.Model):
    id_carritoxcupones=models.AutoField(primary_key=True)
    cantidad=models.IntegerField(default=0)
    precio=models.FloatField(default=0)
    id_cupon = models.ForeignKey(Cupones, on_delete=models.SET_NULL, null=True)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)

class Producto_Pedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio = models.FloatField()
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Oferta_Pedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio = models.FloatField()
    oferta = models.ForeignKey(Oferta, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Combo_Pedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio = models.FloatField()
    combo = models.ForeignKey(Combo, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Cupon_Pedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio = models.FloatField()
    cupon = models.ForeignKey(Cupones, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Cardauth(models.Model):
    id_cardauth =  models.AutoField(primary_key=True)
    token = models.CharField(max_length=20)
    auth = models.CharField(max_length=3)

class Establecimiento_ZonaEnvio(models.Model):
    id_estabxzona =  models.AutoField(primary_key=True)
    id_establecimiento = models.ForeignKey(Establecimiento,on_delete=models.SET_NULL, null=True)
    id_zona = models.ForeignKey(ZonaEnvio,on_delete=models.SET_NULL, null=True)

class Tarjeta_Producto(models.Model):
    id_tarjeta =  models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL, null=True)
    descripcion = models.CharField(max_length=100)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Tarjeta_Producto_Producto(models.Model):
    id_tarjetaxproducto =  models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto,on_delete=models.SET_NULL, null=True)
    id_tarjeta = models.ForeignKey(Tarjeta_Producto,on_delete=models.SET_NULL, null=True)
    cantidad=models.IntegerField()

class Tarjeta_Producto_Cliente(models.Model):
    id_tarjetaxcliente = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL, null=True)
    id_tarjeta = models.ForeignKey(Tarjeta_Producto,on_delete=models.SET_NULL, null=True)
    estado=models.CharField(max_length=1,default = "A")
    fecha = models.DateTimeField(null=True)

class Tarjeta_Monto(models.Model):
    id_tarjeta =  models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL, null=True)
    monto = models.FloatField()
    descripcion = models.CharField(max_length=100)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Tarjeta_Monto_Cliente(models.Model):
    id_tarjetaxcliente = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL, null=True)
    id_tarjeta = models.ForeignKey(Tarjeta_Monto,on_delete=models.SET_NULL, null=True)
    estado=models.CharField(max_length=1,default = "A")
    fecha = models.DateTimeField(null=True)

class Carrito_Tarjeta_Monto(models.Model):
    id_carritoxtarjeta=models.AutoField(primary_key=True)
    precio=models.FloatField(default=0)
    id_tarjeta = models.ForeignKey(Tarjeta_Monto, on_delete=models.SET_NULL, null=True)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)

class Carrito_Tarjeta_Producto(models.Model):
    id_carritoxtarjeta=models.AutoField(primary_key=True)
    precio=models.FloatField(default=0)
    id_tarjeta = models.ForeignKey(Tarjeta_Producto, on_delete=models.SET_NULL, null=True)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, null=True)

class Tarjeta_Monto_Pedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    precio = models.FloatField()
    id_tarjeta = models.ForeignKey(Tarjeta_Monto, on_delete=models.SET_NULL, null=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Tarjeta_Producto_Pedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_tarjeta = models.ForeignKey(Tarjeta_Producto, on_delete=models.SET_NULL, null=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)

class Codigo(models.Model):
    id_codigo = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20)
    descripcion=models.CharField(max_length=100)
    fecha_inicio=models.DateField()
    fecha_fin=models.DateField()
    estado=models.CharField(max_length=1,default = "A")
    tipo=models.CharField(max_length=1,default = "M")
    precio=models.FloatField(default = 0)
    cantidad=models.IntegerField(default = 0)
    image = models.ImageField()
    id_cupon=models.ForeignKey(Cupones, on_delete=models.SET_NULL, null=True)
    id_tarjetamonto=models.ForeignKey(Tarjeta_Monto, on_delete=models.SET_NULL, null=True)
    id_establecimiento=models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.codigo
    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

class Codigo_Monto(models.Model):
    id_codigomonto = models.AutoField(primary_key=True)
    codigomonto = models.CharField(max_length=20)
    monto = models.FloatField()
    id_codigo = models.ForeignKey(Codigo,on_delete=models.SET_NULL, null=True)

class Codigo_Producto(models.Model):
    id_codigoproducto = models.AutoField(primary_key=True)
    codigoproducto = models.CharField(max_length=20)
    id_codigo = models.ForeignKey(Codigo,on_delete=models.SET_NULL, null=True)
    id_producto = models.ForeignKey(Producto,on_delete=models.SET_NULL, null=True)
    cantidad=models.IntegerField(default = 1)

class Codigo_Cliente(models.Model):
    id_codxcliente =  models.AutoField(primary_key=True)
    id_codigo = models.ForeignKey(Codigo,on_delete=models.SET_NULL, null=True)
    id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL, null=True)
    estado=models.CharField(max_length=1,default = "A")

class Sorteo(models.Model):
    id_sorteo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=100)
    fecha_inicio=models.DateField()
    fecha_fin=models.DateField()
    numGanadores=models.IntegerField(default = 0)
    maxGanadores=models.IntegerField()
    image = models.ImageField()
    def __str__(self):
        return self.nombre

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


class Sorteo_Usuario(models.Model):
    id_sorteoxusuario =  models.AutoField(primary_key=True)
    id_sorteo = models.ForeignKey(Sorteo,on_delete=models.SET_NULL, null=True)
    id_usuario = models.ForeignKey(Usuario,on_delete=models.SET_NULL, null=True)


class Publicidad(models.Model):
    TiposPublicidad = (
        ('Superior', 'Superior'),
        ('Inferior', 'Inferior'),
    )
    id_publicidad =models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    image=models.ImageField()
    tipo=models.CharField(max_length=100,choices=TiposPublicidad,default="Superior")
    url=models.CharField(max_length=100, null=True)
    fecha_inicio=models.DateField()
    fecha_fin=models.DateField()
    def __str__(self):
        return self.asunto

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

class Puntos(models.Model):
    id_puntos =models.AutoField(primary_key=True)
    dolarAPuntos =models.IntegerField(default=0)
    puntosADolar =models.IntegerField(default=0)
    puntosATarjeta =models.IntegerField(default=0)
    tarjetaAPuntos =models.IntegerField(default=0)

class Premios(models.Model):
    id_premio =models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=100)
    image=models.ImageField()
    descripcion = models.CharField(max_length=300)
    cantidad=models.IntegerField()
    puntos=models.IntegerField()
    fecha_inicio=models.DateField()
    fecha_fin=models.DateField()

    def __str__(self):
        return self.asunto

    @property
    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

class Premios_Cliente(models.Model):
    Estado = (
        ('Entregado', 'Entregado'),
        ('Recibido', 'Recibido'),
    )
    id_premioXcliente =  models.AutoField(primary_key=True)
    fecha_canje=models.DateField()
    fecha_entrega=models.DateField(null=True)
    id_premio = models.ForeignKey(Premios,on_delete=models.SET_NULL,null=True)
    id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL,null=True)
    estado= models.CharField(max_length=10,choices=Estado,default='Recibido',)


#Modelos para Chat
class ModelBase(models.Model):
    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True, db_index=True, editable=False)
    tiempo = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class CanalMensaje(ModelBase):
    canal = models.ForeignKey("Canal", on_delete=models.CASCADE)
    usuario_cliente = models.ForeignKey(Cliente, null=True,blank=True, on_delete=models.CASCADE)
    usuario_admin = models.ForeignKey(Empleado,null=True,blank=True, on_delete=models.CASCADE)
    texto = models.TextField()
    check_leido = models.BooleanField()
    esAdmin=models.BooleanField()


    def obtener_data_mensaje_usuarios(id_canal):
        qs = CanalMensaje.objects.filter(
            canal_id=id_canal).values("id","esAdmin","check_leido","texto", "usuario_admin__nombre", "usuario_admin__apellido", "usuario_admin__cedula","usuario_cliente__nombre", "usuario_cliente__apellido", "usuario_cliente__usuario__cedula","tiempo")
        mensajes = list(qs.order_by("tiempo"))
        return list(mensajes)

    def verificar_leido(id_mensaje):
        qs=CanalMensaje.objects.filter(
            id=id_mensaje
        )
        return qs.update(check_leido=True)

    def __str__(self):
        return str(self.canal)


class CanalQuerySet(models.QuerySet):


    def filtrar_por_admin(self, username):
        return self.filter(usuario_admin__cedula=username)

    def filtrar_por_cliente(self, username):
        return self.filter(usuario_cliente__usuario__cedula=username)

    def filtrar_por_username(self, username):
        return  self.filtrar_por_admin(username) | self.filtrar_por_cliente(username)


    def filtrar_por_usuario(self, usuario_a, usuario_b):
        #qsAdmin=self.filtrar_por_admin(usuario_a) | self.filtrar_por_admin(usuario_b)
        #qsCliente=self.filtrar_por_cliente(usuario_a) | self.filtrar_por_cliente(usuario_b)
        #return qsAdmin and qsCliente
        return self.filtrar_por_username(usuario_a).filtrar_por_username(usuario_b)

    def verificar_existencia_usuario(self,usuario_c):
        print(Empleado.objects.filter(cedula=usuario_c))
        return Empleado.objects.filter(cedula=usuario_c).exists() or Usuario.objects.filter(cedula=usuario_c).exists()

    def verificar_existencia_cliente(self, usuario_c):
        print(Usuario.objects.filter(cedula=usuario_c))
        return Usuario.objects.filter(cedula=usuario_c).exists()

    def verificar_existencia_admin(self, usuario_c):
        print(Empleado.objects.filter(cedula=usuario_c))
        return Empleado.objects.filter(cedula=usuario_c).exists()

class CanalManager(models.Manager):
    def get_queryset(self, *args, **kwards):
        return CanalQuerySet(self.model, using=self._db)

    def filtrar_ms_por_privado(self, username_a, username_b):
        return self.get_queryset().filtrar_por_cliente(username_a).filtrar_por_admin(username_b)

    def obtener_o_crear_canal_ms(self, username_a, username_b):
        qs0=self.get_queryset().verificar_existencia_cliente(username_a) and self.get_queryset().verificar_existencia_admin(username_b)
        print(qs0)
        print(Usuario.objects.filter(cedula=username_a))
        print(Empleado.objects.filter(cedula=username_b))
        print(Empleado.objects.all().values())



        print("PRUEBAAAAAAAAAAAAAAAAA====")
        if(qs0):
            pass
        else:
            return None, False

        qs = self.filtrar_ms_por_privado(username_a, username_b)
        print(qs)
        if qs.exists():
            print("El canal existe")
            return qs.order_by("tiempo").first(), False  # obj, Created
        print("el canal no existe")
        usuario_a, usuario_b = None, None
        administrador,cliente=None,None
        canal_usuario_a,canal_usuario_b=None,None

        if(Empleado.objects.filter(cedula=username_a).exists()):
            usuario_a=Empleado.objects.filter(cedula=username_a)[0]
            administrador=usuario_a
            print(str(usuario_a.rol)+"ROLES")


        elif(Cliente.objects.filter(usuario__cedula=username_a).exists()):
            usuario_a=Cliente.objects.filter(usuario__cedula=username_a)[0]
            cliente=usuario_a
            print(str(usuario_a.usuario.rol)+"ROLES")


        if(Empleado.objects.filter(cedula=username_b).exists()):
            usuario_b=Empleado.objects.filter(cedula=username_b)[0]
            administrador=usuario_b
            print(str(usuario_b.rol)+"ROLES")

        elif(Cliente.objects.filter(usuario__cedula=username_b).exists()):
            usuario_b=Cliente.objects.filter(usuario__cedula=username_b)[0]
            cliente=usuario_b
            print(str(usuario_b.usuario.rol)+"ROLES")

        else:
            return None, False

        if (usuario_a == None or usuario_b == None):
            return None, False

        print(administrador)
        print(cliente)

        obj_canal = Canal.objects.create(
            usuario_cliente=cliente,
            usuario_admin=administrador
        )


        return obj_canal, True

    def obtener_datos_usuario(id_usuario):
        qs =Usuario.objects.filter(cedula=id_usuario)
        return qs

class Canal(ModelBase):
    usuario_cliente = models.ForeignKey(Cliente, blank=True,null=True,  on_delete=models.CASCADE)
    usuario_admin=models.ForeignKey(Empleado,blank=True,null=True, on_delete=models.CASCADE)
    objects = CanalManager()

class Backup_Pedido(models.Model):
    EstadoPedido = (
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Recibido', 'Recibido'),
        ('Proceso', 'Proceso'),
        ('Devuelto', 'Devuelto'),
        ('Anulado', 'Anulado'),
    )
    id_backpedido=models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)
    id_direccion=models.ForeignKey(DireccionEntrega, on_delete=models.SET_NULL, null=True)
    fecha=models.DateTimeField(default=now)
    tipo_entrega= models.CharField(max_length=100, default = "Domicilio")
    tipo_pago= models.CharField(max_length=100, default = "Efectivo")
    total=models.FloatField()
    nombreTarjeta=models.CharField(max_length=100, default = "", null=True)
    numeroTarjeta=models.CharField(max_length=100, default = "", null=True)
    clienteid = models.IntegerField()
    clientenombre=models.CharField(max_length=100)
    clienteapellido=models.CharField(max_length=100)
    telefono =models.CharField(max_length=100, default = "NONE")
    cedula=models.CharField(max_length=10)