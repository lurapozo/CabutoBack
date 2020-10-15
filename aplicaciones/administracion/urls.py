from django.urls import path
from .views import *


urlpatterns = [	
	path('', inicio, name='redireccionar'),

	#AUTH
	path('/login', login, name='login'),
	path('/logout', logout, name='logout'),

	#MENU PRINCIPAL
	path('principalSuperAdmin/',principalSuperAdmin, name='principalSuperAdmin'),
	path('principalAdmin/',principalAdmin,name='principalAdmin'),

	#EMPRESAS
	path('principalSuperAdmin/empresas/', empresas, name='ver_empresa'),

	#ROLES
	path('roles/',admin_rol,name='ver_roles'),


	#PRODUCTOS
	path('productos/', producto_page,name='ver_productos'),
	path('añadir_productos/', agregar_producto,name='crear_producto')
]
