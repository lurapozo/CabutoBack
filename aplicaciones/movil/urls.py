from django.urls import path
from .views import *

urlpatterns = [
    path('', login),
    path('inicio/', getInicio),
    path('categorias/', getCategoria),
    path('producto/', getProducto),
    path('producto/orderAsc/<int:page>', getProductoAaZ),
    path('producto/orderDesc/<int:page>',getProductoZaA),
    path('producto/precioMenor/<int:page>', getProductoPrecioMenor),
    path('producto/precioMayor/<int:page>', getProductoPrecioMayor),
    path('producto/<int:page>',getProductoParcial),
    path('establecimiento/', getEstablecimiento),
    path('notificacion/', getNotificacion),
    path('cliente/', getCliente),
    path('clienteCorreo/', getClienteCorreo),
    path('historial/', getHistorial),
    path('guardarPedido/',guardarPedido),
    path('cancelarPedido/',borrarPedido),
    path('pagarPedido/',pagarPedido),
    path('devolverPedido/',devolverPedido),
    path('calificarPedido/',calificarPedido),
    path('cobertura/', getCobertura),
    path('guardarDireccion/',guardarDireccion),
    path('direccion/',getDireccion),
    path('editarCliente/', modCliente),
    path('registro/', registro),
    path('login/',login),
    path('cambioContra/',cambioContra),
    path('dispositivo/',registrarDispositivo),
    path('carrito/', getCarrito),
    path('cantidadesCarrito/',modCantidades),
    path('horario/',getHorario),
    path('ofertasData/', getOferta),
    path('politicaData/', politica),
    path('contacto/', getContacto),
    path('reclamo/', envioReclamo),
    #path('actualizaCantidad/',actulizarCantidad),
    path('quitar/',quitar),
    path('cupones/', getCupones),
    path('cupones/<int:id>', getCuponesPersonales),
    path('checkcupones/', checkCupones),
    path('notificaciones/',getNotificaciones),
    path('notificaciones/<str:titulo>',getNotificacionUnica),
    path('notificacion/<str:titulo>',getNotificacionUnica),
    path('actualizarNotificacion/',actualizarNotificacion),
    path('addCupon/',addCupon),
    path('tarjeta/add/',addCodigoAuth),
    path('tarjeta/del/',delCodigoAuth),
    path('tarjeta/',getCodigoAuth),
    path('quitarusuario/',quitar_usuario),
    path('codigos/',getCodigos),
    path('codigos/<str:codigostr>',getCodigosString),
    path('tarjetasRegalo/<int:id>',getTarjetasRegalo),
    path('tarjetasRegaloP/<int:id>',getTarjetasRegaloP),

    path('crearTarjetaRegaloMonto/',crearTarjetaRegaloMonto),
    path('addTarjetaRegaloMonto/',addTarjetaRegaloMonto),
    path('crearTarjetaRegaloproducto/',crearTarjetaRegaloproducto),
    path('addTarjetaRegaloproducto/',addTarjetaRegaloproducto),
    path('eliminarCarrito/',eliminarCarrito),
]