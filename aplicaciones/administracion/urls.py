from django.urls import path
from .views import *


urlpatterns = [	
	path('', inicio),
	path('principalSuperAdmin/',principalSuperAdmin),
	path('principalAdmin/',principalAdmin),
	path('empresas/', getEmpresas),
	path('roles/',admin_rol),
]
