from django.urls import path
from .views import *


urlpatterns = [	
	path('', inicio),
	path('principalSuperAdmin/',principalSuperAdmin),
	path('principalAdmin/',principalAdmin),
	path('principalSuperAdmin/empresas/', empresas),
	path('roles/',admin_rol),
	path('productos/', producto_page),
	path('añadir_productos/', agregar_producto)
]
