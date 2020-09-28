"""CabutoBack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from aplicaciones.administracion.views import *
from aplicaciones.movil.views import *
from django.conf import *

# por defecto va a la parte del administracion
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('aplicaciones.administracion.urls')),
    path('administracion/',include('aplicaciones.administracion.urls')),
    path('movil/',include('aplicaciones.movil.urls')),   
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# por defecto va a la parte del movil
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('',include('aplicaciones.movil.urls')),
#     path('administracion/',include('aplicaciones.administracion.urls')),
#     path('movil/',include('aplicaciones.movil.urls')),   
# ]