from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Empresa)
admin.site.register(Establecimiento)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Combo)
admin.site.register(Carrito)
admin.site.register(Detalle_Carrito)
admin.site.register(Combo_Producto)
admin.site.register(Establecimiento_Producto)
admin.site.register(Politica)
admin.site.register(Oferta)
admin.site.register(Carrito_Oferta)
admin.site.register(Carrito_Combo)
admin.site.register(Cupones)
admin.site.register(Notificacion)
admin.site.register(Carrito_Cupones)
admin.site.register(Reclamo)
admin.site.register(Pedido)
admin.site.register(ZonaEnvio)
admin.site.register(Empleado)
admin.site.register(Cardauth)





#Para visualizar el chat en administracion
class CanalMensajeInline(admin.TabularInline):
    model=CanalMensaje
    extra=1

class CanalUsuarioInline(admin.TabularInline):
    model=CanalUsuario
    extra=1

class CanalAdmin(admin.ModelAdmin):
    inlines= [CanalMensajeInline,CanalUsuarioInline]

    class Meta:
        model = Canal

admin.site.register(Canal,CanalAdmin)
admin.site.register(CanalUsuario)
admin.site.register(CanalMensaje)