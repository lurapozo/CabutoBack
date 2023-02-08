from django.urls import path
from .views import *
from django.conf.urls import url

urlpatterns = [
	path('', principal),
	url(r'^login/',inicio,name='login'),
	#path('login/', inicio),
	url(r'^logout/',cerrar,name='logout'),
	path('principalSuperAdmin/',principalSuperAdmin),
	path('principalAdmin/',principalAdmin,name='principalAdmin'),
	path('pagos/', pagosPedido_page),
	path('tc/', tc),
	path('usuarios/', usuario_page),
	path('clientes/', cliente_page),
	path('pedidos/', pedido_page),
	path("repartidores/",repartidores),
	url(r'^repartidores/asignar_repartidores/(?P<id_pedido>\d+)', asignar_repartidores, name="asignar_repartidores"),
	url(r'^repartidores/asignar_repartidores/ocupar_repartidores/(?P<id_repartidor>\d+)/(?P<id_pedido>\d+)', ocupar_repartidores, name="ocupar_repartidores"),
	path("crud_repartidores/",crud_repartidores, name="crud_repartidores"),
	url(r'^crud_repartidores/add_repartidor/', agregar_repartidor, name="add_repartidor"),
	url(r'^crud_repartidores/edit_repartidor/(?P<id_repartidor>\d+)', edit_repartidor, name="edit_repartidor"),
	path('notificaciones/', notificacion_page),
	path('pedidosEspera/', pedidosEspera_page),
	path('devoluciones/', devueltos_page),
	path('entregas/', get_entregas),
	path('ventas/', get_ventas),
	path('reclamos/', reclamo_page, name="reclamos"),
	path('web_push/', register_wp_notifications, name='register_wp_notifications'),
	url(r'^clientes/ver_cliente/(?P<id_cliente>\d+)', ver_cliente, name="ver_cliente"),
	url(r'^notificaciones/add_notificaciones/', agregar_notificacion, name="add_notificaciones"),
	url(r'^notificaciones/ver_notificacion/(?P<id_notificacion>\d+)', ver_notificacion, name="ver_notificacion"),
	url(r'^notificaciones/enviar_notificacion/(?P<id_notificacion>\d+)', enviar_notificacion, name="enviar_notificacion"),
	url(r'^notificaciones/editar_notificacion/(?P<id_notificacion>\d+)', editar_notificacion, name="editar_notificacion"),
	url(r'^notificaciones/eliminar_notificacion/(?P<id_notificacion>\d+)', eliminar_notificacion, name="eliminar_notificacion"),
	path('establecimientos/',establecimiento_page),
	url(r'^establecimientos/add_establecimientos/', agregar_establecimiento, name="add_establecimientos"),
	url(r'^establecimientos/horario/(?P<id_establecimiento>\d+)', horario_page, name="ver_horario"),
	path('empleados/', empleado_page),
	path('principalSuperAdmin/empresas/', empresas),
	path('roles/',admin_rol),
	path('politica/', agregar_politica),
	path('productos/', producto_page, name="productos"),

    url(r'^usuarios/add_usuarios/', agregar_usuario, name="agregar_usuario"),
	url(r'^usuarios/editar_usuario/(?P<id_usuario>\d+)', editar_usuario, name="editar_usuario"),
	url(r'^productos/añadir_productos/', agregar_producto, name="añadir_productos"),
	url(r'^productos/editar_producto/(?P<id_producto>\d+)', editar_producto, name="editar_producto"),
	url(r'^productos/eliminar_producto/(?P<id_producto>\d+)', eliminar_producto, name="eliminar_producto"),
	url(r'^productos/ver_producto/(?P<id_producto>\d+)', ver_producto, name="ver_producto"),
	path('codigos/',codigos_page),
	url(r'^codigos/add_codigo/', add_codigo, name="add_codigo"),
	url(r'^codigos/add_codigo2/', add_codigo2, name="add_codigo2"),
	url(r'^codigos/tipo_codigo/', tipo_codigo, name="tipo_codigo"),
	url(r'^codigos/editar_codigo/(?P<id_codigo>\d+)', editar_codigo, name="editar_codigo"),
	url(r'^codigos/eliminar_codigo/(?P<id_codigo>\d+)', eliminar_codigo, name="eliminar_codigo"),
	path('sorteos/',sorteos_page),
	url(r'^sorteos/add_sorteo/', add_sorteo, name="add_sorteo"),
	url(r'^sorteos/editar_sorteo/(?P<id_sorteo>\d+)', editar_sorteo, name="editar_csorteo"),
	url(r'^sorteos/eliminar_sorteo/(?P<id_sorteo>\d+)', eliminar_sorteo, name="eliminar_sorteo"),
	url(r'^sorteos/nuevoganador_sorteo/(?P<id_sorteo>\d+)', nuevoganador_sorteo, name="nuevoganador_sorteo"),
	url(r'^sorteos/verganador_sorteo/(?P<id_sorteo>\d+)', verganador_sorteo, name="verganador_sorteo"),
	path('estadisticas/',estadisticas_page),
	path('ofertas/',oferta_page),
	url(r'^ofertas/añadir_ofertas/', agregar_ofertas, name="añadir_ofertas"),
	url(r'^ofertas/editar_ofertas/(?P<id_oferta>\d+)', editar_ofertas, name="editar_ofertas"),
	url(r'^ofertas/eliminar_ofertas/(?P<id_oferta>\d+)', eliminar_ofertas, name="eliminar_ofertas"),
	path('redesSociales/',redes_page),
	url(r'^redesSociales/add_redes/', agregar_red, name="add_redes"),
	url(r'^redesSociales/ver_red/(?P<id_red>\d+)', ver_red, name="ver_red"),
	url(r'^redesSociales/editar_red/(?P<id_red>\d+)', editar_red, name="editar_red"),
	url(r'^redesSociales/eliminar_redes/(?P<id_red>\d+)', eliminar_red, name="eliminar_red"),
	path('coberturaEnvio/',cobertura_page),
	url(r'coberturaEnvio/add_zona/', agregar_cobertura, name="add_zona"),
	url(r'^coberturaEnvio/ver_zona/(?P<id_zona>\d+)', ver_cobertura, name="ver_zona"),
		url(r'coberturaEnvio/ver_coberturatotal/', ver_coberturatotal, name="ver_coberturatotal"),
	url(r'^coberturaEnvio/editar_zona/(?P<id_zona>\d+)', editar_cobertura, name="editar_zona"),
	url(r'^coberturaEnvio/eliminar_zona/(?P<id_zona>\d+)', eliminar_cobertura, name="eliminar_zona"),
	url(r'^coberturaEnvio/inactivar_zona/(?P<id_zona>\d+)', estado_cobertura, name="inactivar_zona"),
	url(r'^calificacion/(?P<id_pedido>\d+)', get_calificacion, name="calificacion"),
	url(r'^buscar_pedido/(?P<id_pedido>\d+)', get_pedido, name="buscar_pedido"),
	url(r'^detalle_pedido/(?P<id_pedido>\d+)', detalle_pedido, name="detalle_pedido"),
	url(r'^pedidosEspera/confirmar_pedido/(?P<id_pedido>\d+)', confirmar_pedido, name="confirmar_pedido"),
	path('cupones/',cupon_page),
	url(r'cupones/add_cupon/', add_cupon, name="add_cupon"),
	url(r'cupones/add_cupon2/', add_cupon2, name="add_cupon2"),
	url(r'cupones/tipo_cupon/', tipo_cupon, name="tipo_cupon"),
	url(r'^cupones/editar_cupon/(?P<id_cupon>\d+)', editar_cupon, name="editar_cupon"),
	url(r'^cupones/eliminar_cupon/(?P<id_cupon>\d+)', eliminar_cupon, name="eliminar_cupon"),
	url(r'^reclamos/ver_reclamo/(?P<id_reclamo>\d+)', ver_reclamo, name="ver_reclamo"),
	#path('combos/',combo_page),

    path('publicidad/', publicidad_page, name="publicidad"),
    url(r'^publicidad/add_publicidades/', agregar_publicidad, name="add_publicidades"),
    url(r'^publicidad/eliminar_publicidad/(?P<id_publicidad>\d+)', eliminar_publicidad, name="eliminar_publicidad"),
    url(r'^publicidad/editar_publicidad/(?P<id_publicidad>\d+)', editar_publicidad, name="editar_publicidad"),

    path('puntos/', puntos_page),
	url(r'^puntos/editar_puntos/(?P<id_producto>\d+)', editar_puntos, name="editar_puntos"),
	url(r'puntos/add_puntos/', add_puntos, name="add_puntos"),
    url(r'^puntos/eliminar_puntos/(?P<id_producto>\d+)', eliminar_puntos, name="eliminar_puntos"),
    url(r'puntos/puntosxpuntos/', puntosxpuntos, name="puntosxpuntos"),

    path('premios/', premios_page),
    url(r'premios/add_premios/', add_premios, name="add_premios"),
    url(r'premios/add_premios2/', add_premios2, name="add_premios2"),
    url(r'premios/tipo_premios/', tipo_premios, name="tipo_premios"),
    url(r'^premios/editar_premios/(?P<id_premio>\d+)', editar_premios, name="editar_premios"),
	url(r'^premios/eliminar_premios/(?P<id_premio>\d+)', eliminar_premios, name="eliminar_premios"),

    path('historial_premios/', historial_premios_page),
    url(r'^detalle_premios/(?P<id_premioXcliente>\d+)', detalle_premios, name="detalle_premios"),



	#URLS PARA CHAT
    path("api/chat/<str:usuario_receptor>/<str:usuario_actual>/",verificar_y_crear_canal),
    #path("api/chat/inbox/<str:usuario_actual>/",obtener_ca_usuario_actual),
    path("api/chat/sms_update/<str:id_mensaje>/",actualizar_sms_leido),
    


]