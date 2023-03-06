from django.urls import path
from .views import *

urlpatterns = [
    path('', login),
    path('getCodigo/', getCodigo),
    path('inicio/', getInicio),
    path('inicio2/<int:establecimiento>', getInicio2),
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
    path('cliente2/', getCliente2),
    path('clienteCorreo/', getClienteCorreo),
    path('historial/', getHistorial),
    path('guardarPedido/',guardarPedido),
    path('guardarPedido2/',guardarPedido2),
    path('cancelarPedido/',borrarPedido),
    path('cancelarPedido2/',borrarPedido2),
    path('pagarPedido/',pagarPedido),
    path('devolverPedido/',devolverPedido),
    path('calificarPedido/',calificarPedido),
    path('cobertura/', getCobertura),
    path('guardarDireccion/',guardarDireccion),
    path('direccion/',getDireccion),
    path('editarCliente/', modCliente),
    path('registro/', registro),
    path('registro2/', registro2),
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
    path('cuponesDatos/<str:name>', getDatosCupon),
    path('cupones/<int:id>', getCuponesPersonales),
    path('cuponesH/<int:id>', getCuponesHistorial),
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
    path('addToken/',addToken),
    path('getPublicidadSuperior/',getPublicidadSuperior),
    path('getPublicidadInferior/',getPublicidadInferior),
    path('premios/', getPremios),
    path('misPuntos/<int:id>', getPuntosPersonales),
    path('misPremios/<int:id>', getPremiosPersonales),
    path('getPremiosUtlizados/<int:id>', getPremiosUtlizados),
    path('reclamarPremio/', recalmarPremio),
    path('restarPuntos/', restarPuntos),
    path('revisarBan/<int:id>', revisarBan),
    path('modContra/', modContra),
    path('getMes/<int:id>', getMes),

	#URLS PARA CHAT
    path("api/chat/<str:cliente>/<str:admin>/",verificar_y_crear_canal),
    #path("api/chat/inbox/<str:usuario_actual>/",obtener_ca_usuario_actual),
    path("sms_update/<str:id_mensaje>/",actualizar_sms_leido),
    path("obtenerAdmin",obtener_data_empleado_admin),

]