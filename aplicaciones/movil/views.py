from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage, EmailMultiAlternatives, BadHeaderError, send_mail
from email.mime.image import MIMEImage
from django.conf import settings
from push_notifications.webpush import WebPushError
from django.core.serializers import serialize
from django.template.loader import render_to_string
from push_notifications.models import WebPushDevice
from push_notifications.models import GCMDevice
from django.db.models import Count, Sum, Avg
from datetime import datetime
from django.utils import timezone
import requests
import json
import random
from django.core import serializers
from .models import *
from aplicaciones.administracion.models import *
import re
import string

notificacion_URL = "https://fcm.googleapis.com/fcm/send"
notificacion_header = {"Authorization": "key=AAAAfK-HTLc:APA91bHkgzXZbzKIhpfreDv215qmTHJjhq1A2GPPm4R9Qc4VGjuTHkuYpsq6bike4TI7zraeehle2Uakv7CWfsp4zzjeKj8NBuOSNvmZigHnybD7a2CdITlJYfMJGjr0R2Gr_eks2CnE"}
# Create your views here.



#aqui  es donde agrego un elemento al mysql
@csrf_exempt
def addCodigoAuth(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        print(response)
        ntoken=response["token"]
        nauth=response["cvc"]

        try:
            existe = Cardauth.objects.filter(token=ntoken)
            total = existe.count()
            if total==0:
                ncard=Cardauth(token=ntoken,auth=nauth)
                ncard.save()
                response_data = {
                    'valid':'OK'
                }
                return JsonResponse(response_data,safe=False)
        except Cardauth.DoesNotExist:
            ncard=Cardauth(token=ntoken,auth=nauth)
            ncard.save()
            response_data = {
                'valid':'OK'
            }
            return JsonResponse(response_data,safe=False)

    response_data = {
        'valid': 'NO'
    }
    return JsonResponse(response_data,safe=False)



#aqui es donde lo busco desde el mysql
@csrf_exempt
def getCodigoAuth(request):
    if request.method == 'GET':
        valor = request.GET.get("token")
        print(valor)
        if valor!=None:
            cards= Cardauth.objects.get(token=valor)
            return JsonResponse(cards.auth,safe=False)
    return HttpResponse(status=400)

#aqui el codigo es borrado cuando se elimina una tarjeta
@csrf_exempt
def delCodigoAuth(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        ntoken=response["token"]
        print(ntoken)
        try:
            record = Cardauth.objects.filter(token=ntoken)
            record.delete()
            response_data = {
                'valid':'OK'
            }
            return JsonResponse(response_data,safe=False)
        except:
            response_data = {
                'valid':'NO'
            }
            return JsonResponse(response_data,safe=False)

    response_data = {
        'valid':'NO'
    }
    return JsonResponse(response_data,safe=False)
#fin de codigo autenticacion de codigo cvc

@csrf_exempt
def getOferta(request):
    if request.method == 'GET':
        res = []
        ofertas = Oferta.objects.filter(fecha_inicio__lte=datetime.today()).exclude(estado="I").order_by("-cantidad")
        ofertas = ofertas.filter(fecha_fin__gte=datetime.today()).exclude(estado="I").order_by("-cantidad")
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        ofertas = ofertas.filter(id_establecimiento = establecimiento)
        for oferta in ofertas:
            id=oferta.nombre.replace(" ","_")+"_"+str(oferta.id_oferta)
            diccionario = {"id":oferta.id_oferta,"id_unico":id, "nombre":oferta.nombre,"descripcion":oferta.descripcion,
            "precioAntes":oferta.precioAntes, "precio":oferta.precio,"cantidad":oferta.cantidad,"imagen":oferta.photo_url,
            "establecimiento":oferta.id_establecimiento.nombre}
            res.append(diccionario)
            print("Esto es lo que voy a enviar",res)
        return JsonResponse(res,safe=False)
    if request.method == 'POST':
        return addOferta(request)
    return HttpResponse(status=400)

@csrf_exempt
def getProducto(request):
    if request.method == 'GET':
        res = []
        print(request.GET.get("nombre"))
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        if request.GET.get("nombre")!=None:
            res = []
            valor = request.GET.get("nombre")
            print("lo que recibe mi get :v ay diosito que reaccione",valor, str(valor))
            producto= Producto.objects.filter(nombre__icontains=str(valor)).exclude(estado="I").annotate(suma=Sum('establecimiento_producto__stock_disponible')).order_by("-suma")
            for product in producto:
                estab = Establecimiento_Producto.objects.filter(id_producto = product.id_producto, id_establecimiento = establecimiento)
                if estab.count() != 0:
                    id=product.nombre.replace(" ","_")+"_"+str(product.id_producto)
                    diccionario={"id":product.id_producto,"id_unico":id, "nombre":product.nombre,"descripcion":product.descripcion,"precio":product.precio,"estado":product.estado, "imagen":product.photo_url, "suma": product.suma}
                    res.append(diccionario)
            return JsonResponse(res,safe=False)
        else:
            producto = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-suma")
            #producto= Producto.objects.filter().exclude(estado="I").annotate(suma=Sum('establecimiento_producto__stock_disponible')).order_by("-suma")
            for product in producto:
                #estab = Establecimiento_Producto.objects.filter(id_producto = product.id_producto, id_establecimiento = establecimiento)
                #if estab.count() != 0:
                id=product.id_producto.nombre.replace(" ","_")+"_"+str(product.id_producto.id_producto)
                diccionario={"id":product.id_producto.id_producto,"id_unico":id,"nombre":product.id_producto.nombre,"descripcion":product.id_producto.descripcion,"precio":product.id_producto.precio,"estado":product.id_producto.estado, "imagen":product.id_producto.photo_url, "suma": product.suma}
                res.append(diccionario)

            return JsonResponse(res,safe=False)

    if request.method == 'POST':
        return addCarrito(request)

    return HttpResponse(status=400)

@csrf_exempt
def getProductoParcial(request, page):
    if request.method == 'GET':
        res = []
        print(request.GET.get("nombre"))
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        if request.GET.get("nombre")!=None:
            res = []
            valor = request.GET.get("nombre")
            print("lo que recibe mi get :v ay diosito que reaccione",valor, str(valor))
            producto= Producto.objects.filter(nombre__icontains=str(valor)).exclude(estado="I").annotate(suma=Sum('establecimiento_producto__stock_disponible')).order_by("-suma")
            for product in producto:
                estab = Establecimiento_Producto.objects.filter(id_producto = product.id_producto, id_establecimiento = establecimiento)
                if estab.count() != 0:
                    id=product.nombre.replace(" ","_")+"_"+str(product.id_producto)
                    diccionario={"id":product.id_producto.id_producto,"id_unico":id,"nombre":product.id_producto.nombre,"descripcion":product.id_producto.descripcion,"precio":product.id_producto.precio,"estado":product.id_producto.estado, "imagen":product.id_producto.photo_url, "suma": product.suma}
                    res.append(diccionario)
            return JsonResponse(res,safe=False)
        else:
            #arrProducto= Producto.objects.filter(establecimiento_producto__stock_disponible__isnull=False).exclude(estado="I").annotate(suma=Sum('establecimiento_producto__stock_disponible')).order_by("suma", "id_producto")
            arrProducto = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-suma")
            paginator = Paginator(arrProducto, per_page = 10)
            page_object = paginator.get_page(page)

            for product in page_object:
                #estab = Establecimiento_Producto.objects.filter(id_producto = product.id_producto, id_establecimiento = establecimiento)
                #if estab.count() != 0:
                id=product.id_producto.nombre.replace(" ","_")+"_"+str(product.id_producto.id_producto)
                diccionario={"id":product.id_producto.id_producto,"id_unico":id,"nombre":product.id_producto.nombre,"descripcion":product.id_producto.descripcion,"precio":product.id_producto.precio,"estado":product.id_producto.estado, "imagen":product.id_producto.photo_url, "suma": product.suma}
                res.append(diccionario)

            return JsonResponse(res,safe=False)

    if request.method == 'POST':
        return addCarrito(request)

    return HttpResponse(status=400)


def getProductoAaZ(request, page):
    if request.method=='GET':
        res=[]
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        arrProducto = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("id_producto__nombre")
        paginator = Paginator(arrProducto, per_page = 10)
        page_object = paginator.get_page(page)
        for product in page_object:
            #estab = Establecimiento_Producto.objects.filter(id_producto = product.id_producto, id_establecimiento = establecimiento)
            #if estab.count() != 0:
            id=product.id_producto.nombre.replace(" ","_")+"_"+str(product.id_producto.id_producto)
            diccionario={"id":product.id_producto.id_producto,"id_unico":id,"nombre":product.id_producto.nombre,"descripcion":product.id_producto.descripcion,"precio":product.id_producto.precio,"estado":product.id_producto.estado, "imagen":product.id_producto.photo_url, "suma": product.suma}
            res.append(diccionario)

        return JsonResponse(res,safe=False)
    if request.method == 'POST':
        return addCarrito(request)

    return HttpResponse(status=400)


def getProductoZaA(request, page):
    if request.method=='GET':
        res=[]
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        arrProducto = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-id_producto__nombre")
        paginator = Paginator(arrProducto, per_page = 10)
        page_object = paginator.get_page(page)
        for product in page_object:
            id=product.id_producto.nombre.replace(" ","_")+"_"+str(product.id_producto.id_producto)
            diccionario={"id":product.id_producto.id_producto,"id_unico":id,"nombre":product.id_producto.nombre,"descripcion":product.id_producto.descripcion,"precio":product.id_producto.precio,"estado":product.id_producto.estado, "imagen":product.id_producto.photo_url, "suma": product.suma}
            res.append(diccionario)

        return JsonResponse(res,safe=False)
    if request.method == 'POST':
        return addCarrito(request)
    return HttpResponse(status=400)

def getProductoPrecioMenor(request, page):
    if request.method=='GET':
        res=[]
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        arrProducto = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-id_producto__precio")
        paginator = Paginator(arrProducto, per_page = 10)
        page_object = paginator.get_page(page)
        for product in page_object:
            id=product.id_producto.nombre.replace(" ","_")+"_"+str(product.id_producto.id_producto)
            diccionario={"id":product.id_producto.id_producto,"id_unico":id,"nombre":product.id_producto.nombre,"descripcion":product.id_producto.descripcion,"precio":product.id_producto.precio,"estado":product.id_producto.estado, "imagen":product.id_producto.photo_url, "suma": product.suma}
            res.append(diccionario)

        return JsonResponse(res,safe=False)
    if request.method == 'POST':
        return addCarrito(request)
    return HttpResponse(status=400)

def getProductoPrecioMayor(request, page):
    if request.method=='GET':
        res=[]
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        arrProducto = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("id_producto__precio")
        paginator = Paginator(arrProducto, per_page = 10)
        page_object = paginator.get_page(page)
        for product in page_object:
            id=product.id_producto.nombre.replace(" ","_")+"_"+str(product.id_producto.id_producto)
            diccionario={"id":product.id_producto.id_producto,"id_unico":id,"nombre":product.id_producto.nombre,"descripcion":product.id_producto.descripcion,"precio":product.id_producto.precio,"estado":product.id_producto.estado, "imagen":product.id_producto.photo_url, "suma": product.suma}
            res.append(diccionario)

        return JsonResponse(res,safe=False)
    if request.method == 'POST':
        return addCarrito(request)
    return HttpResponse(status=400)

def getEstablecimiento(request):
    if request.method == 'GET':
        res = []
        if request.GET.get("nombre")!=None:
            valor = request.GET.get("nombre")
            establecimientos= Establecimiento.objects.filter(nombre__icontains=str(valor))
            for establecimiento in establecimientos:
                diccionario={"id":establecimiento.id_establecimiento,"nombre":establecimiento.nombre,"direccion":establecimiento.direccion,"telefono":establecimiento.telefono,"longitud":establecimiento.longitud,"latitud":establecimiento.latitud}
                res.append(diccionario)
            return JsonResponse(res,safe=False)
        elif request.GET.get("id")!=None:
            valor = request.GET.get("id")
            establecimiento= Establecimiento.objects.filter(id_establecimiento=valor).values()
            data = list(establecimiento)
            return JsonResponse(data, safe=False)
        else:
            establecimientos= Establecimiento.objects.filter().values()
            data = list(establecimientos)
            return JsonResponse(data, safe=False)
    return HttpResponse(status=400)

def getCategoria(request):
    if request.method== 'GET':
        res= []
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        if request.GET.get("id")!=None:
            valor=request.GET.get("id")
            categoria= Categoria.objects.filter(nombre=valor).first()
            productos=Producto.objects.select_related().filter(id_categoria=categoria).exclude(estado="I")
            for product in productos:
                estab = Establecimiento_Producto.objects.filter(id_producto = product.id_producto, id_establecimiento = establecimiento)
                if estab.count() != 0:
                    id="P"+product.nombre.replace(" ","_")+"_"+str(product.id_producto)
                    diccionario={"id":product.id_producto,"id_unico":id,"nombre":product.nombre,"descripcion":product.descripcion,"precio":product.precio,"estado":product.estado, "imagen":product.photo_url}
                    res.append(diccionario)
            return JsonResponse(res,safe=False)
        categorias= Categoria.objects.values()
        data = list(categorias)
        return JsonResponse(data,safe=False)

def getInicio(request):
    if request.method== 'GET':
        res= []
        if request.GET.get("nombre")!=None:
            valor = request.GET.get("nombre")
            categorias= Categoria.objects.filter(nombre__icontains=str(valor)).values()[:4]
            data = list(categorias)
            productos = Producto.objects.select_related().filter(nombre__icontains=str(valor)).annotate(suma=Sum('establecimiento_producto__stock_disponible')).order_by("-suma").values('nombre', 'image','precio','suma')[:6]
            productos = list(productos)
            ofertas = Oferta.objects.select_related().filter(nombre__icontains=str(valor)).filter(cantidad__gt=0).order_by("-cantidad").values('nombre', 'image','precioAntes','precio','cantidad')[:6]
            ofertas = list(ofertas)
            res = {
                'categorias': data,
                'productos': productos,
                'ofertas': ofertas,
            }
            return JsonResponse(res,safe=False)
        else:
            categorias= Categoria.objects.values()[:4]
            data = list(categorias)
            productos = Producto.objects.select_related().filter().annotate(suma=Sum('establecimiento_producto__stock_disponible')).order_by("-suma").values('nombre', 'image','precio','suma')[:6]
            productos = list(productos)
            ofertas = Oferta.objects.select_related().filter(cantidad__gt=0).order_by("-cantidad").values('nombre', 'image','precioAntes','precio','cantidad')[:6]
            ofertas = list(ofertas)
            res = {
                'categorias': data,
                'productos': productos,
                'ofertas': ofertas,
            }
            return JsonResponse(res,safe=False)

def getInicio2(request, establecimiento):
    if request.method== 'GET':
        res= []
        if request.GET.get("nombre")!=None:
            valor = request.GET.get("nombre")
            categorias= Categoria.objects.filter(nombre__icontains=str(valor)).values()[:4]
            data = list(categorias)
            productos = Establecimiento_Producto.objects.select_related().filter(id_producto__nombre__icontains=str(valor)).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-suma").values('id_producto__nombre', 'id_producto__image','id_producto__precio','suma')
            productos = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-suma").values('id_producto__nombre', 'id_producto__image','id_producto__precio','suma')[:6]
            #productos = productos.filter(id_establecimiento = establecimiento)[:6]
            productos = list(productos)
            ofertas = Oferta.objects.select_related().filter(nombre__icontains=str(valor)).filter(cantidad__gt=0).order_by("-cantidad").values('nombre', 'image','precioAntes','precio','cantidad')
            ofertas = ofertas.filter(id_establecimiento = establecimiento)[:6]
            ofertas = list(ofertas)
            res = {
                'categorias': data,
                'productos': productos,
                'ofertas': ofertas,
            }
            return JsonResponse(res,safe=False)
        else:
            categorias= Categoria.objects.values()[:4]
            data = list(categorias)
            #productos = Producto.objects.select_related().filter().annotate(suma=Sum('establecimiento_producto__stock_disponible')).order_by("-suma").values('nombre', 'image','precio','suma')[:6]
            productos = Establecimiento_Producto.objects.select_related().filter().annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-suma").values('id_producto__nombre', 'id_producto__image','id_producto__precio','suma')
            productos = Establecimiento_Producto.objects.filter(id_establecimiento = establecimiento).annotate(suma=Sum('id_producto__establecimiento_producto__stock_disponible')).order_by("-suma").values('id_producto__nombre', 'id_producto__image','id_producto__precio','suma')[:6]
            #productos = productos.filter(id_establecimiento = establecimiento)[:6]
            productos = list(productos)
            ofertas = Oferta.objects.select_related().filter(cantidad__gt=0).order_by("-cantidad").values('nombre', 'image','precioAntes','precio','cantidad')
            ofertas = ofertas.filter(id_establecimiento = establecimiento)[:6]
            ofertas = list(ofertas)
            res = {
                'categorias': data,
                'productos': productos,
                'ofertas': ofertas,
            }
            return JsonResponse(res,safe=False)

def getHistorial(request):
    if request.method == 'GET':
        res = []
        if request.GET.get("id")!=None:
            valor = request.GET.get("id")
            pedido= Pedido.objects.filter(id_pedido=valor).values()
            data = list(pedido)
            pedido= Pedido.objects.get(id_pedido=valor)
            productos = Producto_Pedido.objects.select_related().filter(pedido=pedido).values('producto__nombre', 'cantidad','precio')
            productos = list(productos)
            ofertas = Oferta_Pedido.objects.select_related().filter(pedido=pedido).values('oferta__nombre', 'cantidad','precio')
            ofertas = list(ofertas)
            combos = Combo_Pedido.objects.select_related().filter(pedido=pedido).values('combo__nombre', 'cantidad','precio')
            combos = list(combos)
            cupones = Cupon_Pedido.objects.select_related().filter(pedido=pedido).values('cupon__nombre', 'cantidad','precio')
            cupones = list(cupones)
            transaccion = TransaccionPedido.objects.filter(pedido=pedido).values('transaccion')
            transaccion = list(transaccion)
            res = {
                'pedido': data,
                'productos': productos,
                'ofertas': ofertas,
                'combos': combos,
                'cupones': cupones,
                'transaccion':transaccion
            }
            print(res);
            return JsonResponse(res,safe=False)
        elif request.GET.get("cliente")!=None:
            valor = request.GET.get("cliente")
            user = Cliente.objects.filter(usuario__id_usuario=valor).first()
            pedidos = Pedido.objects.filter(cliente=user).exclude(estado="Anulado").order_by("-id_pedido").values('id_pedido', 'fecha','total', 'puntos')
            data = list(pedidos)
            return JsonResponse(data, safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def borrarPedido(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        value=response["id"]
        pedido=response["pedido"]
        user=Cliente.objects.get(id_cliente=value)
        pedido=Pedido.objects.filter(id_pedido=pedido).first()
        if pedido.estado == "Recibido":
            total=round(pedido.total,2)
            transaccion = TransaccionPedido.objects.filter(pedido=pedido).first()
            if transaccion != None:
                msj= "Se ha reversado el pago de su pedido con valor de $"+str(total)+"\n"+"Id transacción: "+ str(transaccion.transaccion)
                try:
                    email = EmailMessage('Transacción reversada', msj, to=[user.usuario.correo])
                    email.send()
                    #send_mail('Transacción reversada',msj,'cabutosoftware1@gmail.com',[user.usuario.correo],fail_silently=False,html_message= '<html><body>'+msj+'</body></html>')
                except:
                    print("Error al enviar correo")
            pedido.estado="Anulado"
            pedido.pagado=False
            pedido.save()
            res = {
                'valid': 'ok'
            }
            return JsonResponse(res,safe=False)
        else:
            res = {
                'valid': 'not'
            }
            return JsonResponse(res,safe=False)

@csrf_exempt
def borrarPedido2(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        value=response["id"]
        pedido=response["pedido"]
        user=Cliente.objects.get(id_cliente=value)
        pedido=Pedido.objects.filter(id_pedido=pedido).first()
        if pedido.estado == "Recibido" or pedido.estado == "Regalo":
            total=round(pedido.total,2)
            transaccion = TransaccionPedido.objects.filter(pedido=pedido).first()
            if transaccion != None:
                msj= "Se ha reversado el pago de su pedido con valor de $"+str(total)+"\n"+"Id transacción: "+ str(transaccion.transaccion)
                try:
                    email = EmailMessage('Transacción reversada', msj, to=[user.usuario.correo])
                    email.send()
                    #send_mail('Transacción reversada',msj,'cabutosoftware1@gmail.com',[user.usuario.correo],fail_silently=False,html_message= '<html><body>'+msj+'</body></html>')
                except:
                    print("Error al enviar correo")
            if pedido.estado == "Regalo":
                detalle_tarjeta_monto=Tarjeta_Monto.objects.filter(id_pedido=pedido)
                detalle_tarjeta_producto=Tarjeta_Producto.objects.filter(id_pedido=pedido)

                total_tarjeta_monto = detalle_tarjeta_monto.count()
                total_tarjeta_producto = detalle_tarjeta_producto.count()
                if total_tarjeta_monto > 0:
                    for tarjet in detalle_tarjeta_monto:
                        tarXcliente=Tarjeta_Monto_Cliente.objects.get(id_tarjeta=tarjet.id_tarjeta)
                        tarXcliente.delete()
                        tarjet.delete()
                if total_tarjeta_producto > 0:
                    for tarjet in detalle_tarjeta_monto:
                        tarXcliente=Tarjeta_Producto_Pedido.objects.get(id_tarjeta=tarjet.id_tarjeta)
                        tarXcliente.delete()
                        tarjet.delete()
            pedido.estado="Anulado"
            pedido.pagado=False
            pedido.save()
            res = {
                'valid': 'ok'
            }
            return JsonResponse(res,safe=False)
        else:
            res = {
                'valid': 'not'
            }
            return JsonResponse(res,safe=False)

@csrf_exempt
def pagarPedido(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        pedido=response["pedido"]
        transaccion_id=response["transaccion"]
        autorizacion=response["autorizacion"]
        pedido=Pedido.objects.filter(id_pedido=pedido).first()
        user=pedido.cliente.usuario
        print(user)
        if not pedido.pagado and pedido.tipo_pago == "Tarjeta":
            pedido.pagado=True
            pedido.save()
            total=round(pedido.total,2)
            msj= "Se ha realizado el pago de su pedido con valor de $"+str(total)+"\n"+"Id transacción: "+ str(transaccion_id)+"\n"+"Autorización: "+str(autorizacion)
            transaccion=TransaccionPedido(transaccion=transaccion_id,pedido=pedido)
            transaccion.save()
            try:
                html = render_to_string("Correos/pagoTarjeta.html",{"data":transaccion, "autorizacion":autorizacion}).strip()
                msg = EmailMultiAlternatives('Pedido pagado', html, 'cabutosoftware1@gmail.com', [user.correo])
                msg.content_subtype = 'html'
                msg.mixed_subtype = 'related'
                msg.send()
            except Exception as e:
                print("Error al enviar correo")
                print("type error: " + str(e))
            res = {
                'valid': 'ok'
            }
            return JsonResponse(res,safe=False)

        if not pedido.pagado:
            total=round(pedido.total,2)
            msj= "Se ha realizado la compra de su pedido con valor de $"+str(total)+"\n"
            try:
                html = render_to_string("Correos/pagoEfectivo.html",{"data":pedido}).strip()
                msg = EmailMultiAlternatives('Pedido pagado', html, 'cabutosoftware1@gmail.com', [user.correo])
                msg.content_subtype = 'html'
                msg.mixed_subtype = 'related'
                msg.send()
            except Exception as e:
                print("Error al enviar correo")
                print("type error: " + str(e))
            res = {
                'valid': 'ok'
            }
            return JsonResponse(res,safe=False)

        else:
            res = {
                'valid': 'not'
            }
            return JsonResponse(res,safe=False)

@csrf_exempt
def devolverPedido(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        pedido=response["pedido"]
        observacion=response["justificacion"]
        pedido=Pedido.objects.filter(id_pedido=pedido).first()
        pedido.observacion=observacion
        pedido.estado="Devuelto"
        pedido.save()
        res = {
            'valid': 'ok'
        }
        return JsonResponse(res,safe=False)

@csrf_exempt
def calificarPedido(request):
    if request.method == 'GET':
        if request.GET.get("id")!=None:
            valor = request.GET.get("id")
            pedido=Pedido.objects.filter(id_pedido=valor).first()
            calificacionP=CalificacionPedido.objects.filter(pedido=pedido).values()
            data = list(calificacionP)
            return JsonResponse(data,safe=False)
    if request.method == 'POST':
        response = json.loads(request.body)
        pedido=response["pedido"]
        justificacion=response["justificacion"]
        nota=response["calificacion"]
        pedido=Pedido.objects.filter(id_pedido=pedido).first()
        calificacionP=CalificacionPedido.objects.filter(pedido=pedido).first()
        calificacionP.calificacion=nota
        calificacionP.justificacion=justificacion
        calificacionP.save()
        res = {
            'valid': 'ok'
        }
        return JsonResponse(res,safe=False)

@csrf_exempt
def guardarPedido(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        value=response["id"]
        try:
            carrito=response["carrito"]
        except:
            clienteNuevo = Cliente.objects.get(id_cliente=int(value))
        tipoEntrega=response["tipoEntrega"]
        direccion=response["direccion"]
        tipoPago=response["tipoPago"]
        subtotal=response["subtotal"]
        subtotal2=response["subtotal"]
        envio=response["envio"]
        descuento=response["descuento"]
        estadopedido=response["tarjetaRegalo"]
        nombreTarjeta=response["nombreTarjeta"]
        numeroTarjeta=response["numeroTarjeta"]
        tarjeta=response["tarj"]

        total=(subtotal-descuento+envio)
        subtotal=round(subtotal/1.12,2)
        iva=round(subtotal*0.12,2)
        print(tipoEntrega)
        if tipoEntrega=="Domicilio":
            print(direccion)
            direccion=DireccionEntrega.objects.get(id_direccion=direccion)
            print(direccion)
            establecimiento= Establecimiento.objects.get(id_establecimiento=1)
        else:
            establecimiento= Establecimiento.objects.get(id_establecimiento=direccion)
            direccion=None
        user=Cliente.objects.filter(id_cliente=value).first()
        try:
            pedido=Pedido(tipo_entrega=tipoEntrega,tipo_pago=tipoPago,subtotal=subtotal,iva=iva,descuento=descuento,
            envio=envio,total=total,cliente=user,direccion=direccion,establecimiento=establecimiento,observacion="",fecha=timezone.now(),
            nombreTarjeta=nombreTarjeta,numeroTarjeta=numeroTarjeta)
            if(tarjeta=="monto" or tarjeta=="producto"):
                pedido.estado="Regalo"
            puntos = Puntos.objects.get(id_puntos = 1)
            pedido.puntos=subtotal2 * (puntos.puntosADolar / puntos.dolarAPuntos)
            pedido.save()
            if(tarjeta=="monto"):
                receptor=response["receptor"]
                descripcion=response["descripcion"]
                clienteEmisor = Cliente.objects.get(id_cliente=int(value))
                clienteReceptor = Cliente.objects.get(usuario__correo=receptor)

                tarjetaMonto=Tarjeta_Monto(id_cliente=clienteEmisor, monto=float(total),descripcion=descripcion,id_pedido=pedido)
                tarjetaMonto.save()
                tarjetaMontoCliente=Tarjeta_Monto_Cliente(id_cliente=clienteReceptor, id_tarjeta=tarjetaMonto, fecha=timezone.now())
                tarjetaMontoCliente.save()

                devices=GCMDevice.objects.filter(user=clienteReceptor.usuario)
                mensaje= "¡Alguien te ha enviado un regalo!"

                data = {"title":"Regalo recibido","icon": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png", "titulo": "Nuevo regalo", "mensaje":mensaje,"color":"#ff7c55", "priority":"high","notification_foreground": "true", "image": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png"}
                #devices.send_message(mensaje, extra=data)

                datasend={"to": clienteReceptor.usuario.token,
                        "notification": {
                            "title": "Regalo recibido",
                            "body": mensaje
                        },
                        "data": data
                    }
                response = requests.post(notificacion_URL, headers=notificacion_header, json=datasend)

                autorizacion="SDFGTBHR"
                redes=RedSocial.objects.filter()
                html = render_to_string("Correos/tarjetaDeRegalo.html",{"data":tarjetaMonto, "autorizacion":autorizacion,"usuario": clienteReceptor,"redes":redes}).strip()
                msg = EmailMultiAlternatives('Nueva Tarjeta De Regalo', html, 'cabutosoftware1@gmail.com', to=[clienteReceptor.usuario.correo])
                msg.content_subtype = 'html'  # set the primary content to be text/html
                msg.mixed_subtype = 'related'
                try:
                    msg.send()
                    print("type error: ")
                except Exception as e:
                    print("Error al enviar correo")
                    print("type error: " + str(e))

            elif(tarjeta=="producto"):
                receptor=response["receptor"]
                descripcion=response["descripcion"]
                detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito)
                clienteEmisor = Cliente.objects.get(id_cliente=int(value))
                clienteReceptor = Cliente.objects.get(usuario__correo=receptor)
                tarjetaProducto=Tarjeta_Producto(id_cliente=clienteEmisor, descripcion=descripcion,id_pedido=pedido)
                tarjetaProducto.save()
                tarjetaProductoCliente=Tarjeta_Producto_Cliente(id_cliente=clienteReceptor, id_tarjeta=tarjetaProducto, fecha=timezone.now())
                tarjetaProductoCliente.save()

                devices=GCMDevice.objects.filter(user=clienteReceptor.usuario)
                mensaje= "¡Alguien te ha enviado un regalo!"
                data = {"title":"Regalo recibido","icon": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png", "titulo": "Nuevo regalo", "mensaje":mensaje,"color":"#ff7c55", "priority":"high","notification_foreground": "true", "image": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png"}
                '''devices.send_message(mensaje, extra=data)'''

                datasend={"to": clienteReceptor.usuario.token,
                        "notification": {
                            "title": "Regalo recibido",
                            "body": mensaje
                        },
                        "data": data
                    }

                response = requests.post(notificacion_URL, headers=notificacion_header, json=datasend)

                autorizacion="SDFGTBHR"
                redes=RedSocial.objects.filter()
                html = render_to_string("Correos/tarjetaDeRegalo2.html",{"data":tarjetaProducto, "autorizacion":autorizacion,"usuario": clienteReceptor,"redes":redes, "productos":detalle_producto}).strip()
                msg = EmailMultiAlternatives('Nueva Tarjeta De Regalo', html, 'cabutosoftware1@gmail.com', to=[clienteReceptor.usuario.correo])
                msg.content_subtype = 'html'  # set the primary content to be text/html
                msg.mixed_subtype = 'related'
                try:
                    msg.send()
                    print("type error: ")
                except Exception as e:
                    print("Error al enviar correo")
                    print("type error: " + str(e))

                for producto in detalle_producto:
                    '''pro=Producto.objects.filter(id_producto=producto.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
                    if(pro.suma-producto.cantidad>=0):
                        productoxpedido=Producto_Pedido(cantidad=producto.cantidad,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                        productoxpedido.save()
                        producto.delete()
                    elif(pro.suma>0):
                        productoxpedido=Producto_Pedido(cantidad=pro.suma,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                        productoxpedido.save()
                        producto.delete()'''
                    tarjetaProductoProducto=Tarjeta_Producto_Producto(id_tarjeta=tarjetaProducto, id_producto=producto.id_producto, cantidad=producto.cantidad)
                    tarjetaProductoProducto.save()
                    producto.delete()

            else:
                carrito=Carrito.objects.filter(id_carrito=carrito).first()
                detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito)
                detalle_oferta=Carrito_Oferta.objects.filter(id_carrito=carrito)
                detalle_combo=Carrito_Combo.objects.filter(id_carrito=carrito)
                detalle_cupon=Carrito_Cupones.objects.filter(id_carrito=carrito)
                detalle_tarjeta_monto=Carrito_Tarjeta_Monto.objects.filter(id_carrito=carrito)
                detalle_tarjeta_producto=Carrito_Tarjeta_Producto.objects.filter(id_carrito=carrito)


                #dtm=Carrito_Tarjeta_Monto.objects.get(id_carrito=carrito)
                detallePedido2(pedido,carrito,detalle_producto,detalle_oferta,detalle_combo,detalle_cupon,detalle_tarjeta_monto,detalle_tarjeta_producto)
            res = {
            'valid': 'ok',
            'pedido': pedido.id_pedido
            }
            devices = WebPushDevice.objects.all()
            data = json.dumps({
                "title": f'¡Nuevo pedido!',
                "message": f'Usuario {user.nombre} ha realizado un nuevo pedido.',
                "vibrate": "[200, 100, 200, 100, 200, 100, 200]"
            })
            #datasend={"to": "/topics/CAMBIAR", "notification": {"title": f'¡Nuevo pedido!',"subtitle": f'¡Nuevo pedido!',"body": f'Usuario {user.nombre} ha realizado un nuevo pedido.'},"data":data}
            for device in devices:
                try:
                    device.send_message(message=data)
                    #response = requests.post(notificacion_URL, headers=notificacion_header, json=datasend)
                except WebPushError as e:
                    print(e)
                    device.delete()
            return JsonResponse(res,safe=False)
        except Exception as e:
            print("type error: " + str(e))
            res = {
            'valid': 'not',
            }
            return JsonResponse(res,safe=False)

@csrf_exempt
def guardarPedido2(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        value=response["id"]
        try:
            carrito=response["carrito"]
        except:
            clienteNuevo = Cliente.objects.get(id_cliente=int(value))
        tipoEntrega=response["tipoEntrega"]
        direccion=response["direccion"]
        tipoPago=response["tipoPago"]
        subtotal=response["subtotal"]
        subtotal2=response["subtotal"]
        envio=response["envio"]
        descuento=response["descuento"]
        estadopedido=response["tarjetaRegalo"]

        tarjeta=response["tarj"]

        total=(subtotal-descuento+envio)
        subtotal=round(subtotal/1.12,2)
        iva=round(subtotal*0.12,2)
        print(tipoEntrega)
        if tipoEntrega=="Domicilio":
            print(direccion)
            direccion=DireccionEntrega.objects.get(id_direccion=direccion)
            print(direccion)
            establecimiento= Establecimiento.objects.get(id_establecimiento=1)
        else:
            establecimiento= Establecimiento.objects.get(id_establecimiento=direccion)
            direccion=None
        user=Cliente.objects.filter(id_cliente=value).first()
        try:
            pedido=Pedido(tipo_entrega=tipoEntrega,tipo_pago=tipoPago,subtotal=subtotal,iva=iva,descuento=descuento,
            envio=envio,total=total,cliente=user,direccion=direccion,establecimiento=establecimiento,observacion="",fecha=timezone.now())
            if(tarjeta=="monto" or tarjeta=="producto"):
                pedido.estado="Regalo"
            puntos = Puntos.objects.get(id_puntos = 1)
            pedido.puntos=subtotal2 * (puntos.puntosADolar / puntos.dolarAPuntos)
            pedido.save()
            if(tarjeta=="monto"):
                receptor=response["receptor"]
                descripcion=response["descripcion"]
                clienteEmisor = Cliente.objects.get(id_cliente=int(value))
                clienteReceptor = Cliente.objects.get(usuario__correo=receptor)

                tarjetaMonto=Tarjeta_Monto(id_cliente=clienteEmisor, monto=float(total),descripcion=descripcion,id_pedido=pedido)
                tarjetaMonto.save()
                tarjetaMontoCliente=Tarjeta_Monto_Cliente(id_cliente=clienteReceptor, id_tarjeta=tarjetaMonto, fecha=timezone.now())
                tarjetaMontoCliente.save()

                devices=GCMDevice.objects.filter(user=clienteReceptor.usuario)
                mensaje= "¡Alguien te ha enviado un regalo!"

                data = {"title":"Regalo recibido","icon": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png", "titulo": "Nuevo regalo", "mensaje":mensaje,"color":"#ff7c55", "priority":"high","notification_foreground": "true", "image": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png"}
                #devices.send_message(mensaje, extra=data)

                datasend={"to": clienteReceptor.usuario.token,
                        "notification": {
                            "title": "Regalo recibido",
                            "body": mensaje
                        },
                        "data": data
                    }
                response = requests.post(notificacion_URL, headers=notificacion_header, json=datasend)

                msj = 'Ha recibido un regalo de: '+str(clienteEmisor.nombre)+' '+str(clienteEmisor.apellido)+', abra la app Cabuto`s para reclamarlo.'
                email = EmailMessage('Nuevo regalo recibido: ', msj, to=[clienteReceptor.usuario.correo])
                email.send()

            elif(tarjeta=="producto"):
                receptor=response["receptor"]
                descripcion=response["descripcion"]
                detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito)
                clienteEmisor = Cliente.objects.get(id_cliente=int(value))
                clienteReceptor = Cliente.objects.get(usuario__correo=receptor)
                tarjetaProducto=Tarjeta_Producto(id_cliente=clienteEmisor, descripcion=descripcion,id_pedido=pedido)
                tarjetaProducto.save()
                tarjetaProductoCliente=Tarjeta_Producto_Cliente(id_cliente=clienteReceptor, id_tarjeta=tarjetaProducto, fecha=timezone.now())
                tarjetaProductoCliente.save()

                devices=GCMDevice.objects.filter(user=clienteReceptor.usuario)
                mensaje= "¡Alguien te ha enviado un regalo!"
                data = {"title":"Regalo recibido","icon": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png", "titulo": "Nuevo regalo", "mensaje":mensaje,"color":"#ff7c55", "priority":"high","notification_foreground": "true", "image": "https://cdn.discordapp.com/attachments/1009846868806729738/1014286378298777670/cabuto_IUVHKai2.png"}
                '''devices.send_message(mensaje, extra=data)'''

                datasend={"to": clienteReceptor.usuario.token,
                        "notification": {
                            "title": "Regalo recibido",
                            "body": mensaje
                        },
                        "data": data
                    }

                response = requests.post(notificacion_URL, headers=notificacion_header, json=datasend)
                msj = 'Ha recibido un regalo de: '+str(clienteEmisor.nombre)+' '+str(clienteEmisor.apellido)+', abra la app Cabuto`s para reclamarlo.'
                email = EmailMessage('Nuevo regalo recibido: ', msj, to=[clienteReceptor.usuario.correo])
                email.send()

                for producto in detalle_producto:
                    '''pro=Producto.objects.filter(id_producto=producto.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
                    if(pro.suma-producto.cantidad>=0):
                        productoxpedido=Producto_Pedido(cantidad=producto.cantidad,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                        productoxpedido.save()
                        producto.delete()
                    elif(pro.suma>0):
                        productoxpedido=Producto_Pedido(cantidad=pro.suma,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                        productoxpedido.save()
                        producto.delete()'''
                    tarjetaProductoProducto=Tarjeta_Producto_Producto(id_tarjeta=tarjetaProducto, id_producto=producto.id_producto, cantidad=producto.cantidad)
                    tarjetaProductoProducto.save()
                    producto.delete()

            else:
                carrito=Carrito.objects.filter(id_carrito=carrito).first()
                detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito)
                detalle_oferta=Carrito_Oferta.objects.filter(id_carrito=carrito)
                detalle_combo=Carrito_Combo.objects.filter(id_carrito=carrito)
                detalle_cupon=Carrito_Cupones.objects.filter(id_carrito=carrito)
                detalle_tarjeta_monto=Carrito_Tarjeta_Monto.objects.filter(id_carrito=carrito)
                detalle_tarjeta_producto=Carrito_Tarjeta_Producto.objects.filter(id_carrito=carrito)


                #dtm=Carrito_Tarjeta_Monto.objects.get(id_carrito=carrito)
                detallePedido2(pedido,carrito,detalle_producto,detalle_oferta,detalle_combo,detalle_cupon,detalle_tarjeta_monto,detalle_tarjeta_producto)
            res = {
            'valid': 'ok',
            'pedido': pedido.id_pedido
            }
            devices = WebPushDevice.objects.all()
            data = json.dumps({
                "title": f'¡Nuevo pedido!',
                "message": f'Usuario {user.nombre} ha realizado un nuevo pedido.',
                "vibrate": "[200, 100, 200, 100, 200, 100, 200]"
            })
            #datasend={"to": "/topics/CAMBIAR", "notification": {"title": f'¡Nuevo pedido!',"subtitle": f'¡Nuevo pedido!',"body": f'Usuario {user.nombre} ha realizado un nuevo pedido.'},"data":data}
            for device in devices:
                try:
                    device.send_message(message=data)
                    #response = requests.post(notificacion_URL, headers=notificacion_header, json=datasend)
                except WebPushError as e:
                    print(e)
                    device.delete()
            return JsonResponse(res,safe=False)
        except Exception as e:
            print("type error: " + str(e))
            res = {
            'valid': 'not',
            }
            return JsonResponse(res,safe=False)

def getCobertura(request):
    if request.method == 'GET':
        zona = ZonaEnvio.objects.filter(estado='A').values('zona', 'envio')
        data = list(zona)
        return JsonResponse(data, safe=False)
    return HttpResponse(status=400)

def getDireccion(request):
    if request.method == 'GET':
        if request.GET.get("id")!=None:
            valor = request.GET.get("id")
            pedido= DireccionEntrega.objects.filter(id_direccion=valor).values()
            data = list(pedido)
            return JsonResponse(data,safe=False)
        elif request.GET.get("cliente")!=None:
            valor = request.GET.get("cliente")
            print(valor)
            user=Cliente.objects.filter(usuario__id_usuario=valor).first()
            zona = DireccionEntrega.objects.filter(cliente=user).values('direccion', 'id_direccion')
            data = list(zona)
            return JsonResponse(data, safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def guardarDireccion(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        id=response["id"]
        descripcion= response["descripcion"]
        direccion=response["direccion"]
        latitud=response["latitud"]
        longitud=response["longitud"]
        envio=response["envio"]
        if id!=-1:
            user=Cliente.objects.filter(usuario__id_usuario=id).first()
        else:
            user=None
        try:

            direccion=DireccionEntrega(direccion=direccion,descripcion=descripcion,latitud=latitud,longitud=longitud,cliente=user,envio=envio)
            direccion.save()
            res = {
            'id': direccion.id_direccion,
            'valid': 'ok'
            }
            return JsonResponse(res,safe=False)
        except:
            res = {
            'valid': 'not'
            }
            return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

def getNotificacion(request):
    if request.method == 'GET':
        res = []
        notificacions= Notificacion.objects.order_by('-registro')
        for notificacion in notificacions:
            diccionario={"id":notificacion.id_notificacion,"asunto":notificacion.asunto,"mensaje":notificacion.mensaje,
            "fecha":notificacion.registro,"imagen":notificacion.photo_url}
            res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

def getContacto(request):
    if request.method == 'GET':
        res = []
        notificacions= RedSocial.objects.filter().order_by("nombre")
        for notificacion in notificacions:
            diccionario={"id":notificacion.id_red,"nombre":notificacion.nombre,"link":notificacion.enlace,"imagen":notificacion.photo_url}
            res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def modCliente(request):
    if request.method == 'POST':
        id=request.POST.get('id', None)
        nombre= request.POST.get("nombre",None)
        apellido=request.POST.get("apellido",None)
        cedula=request.POST.get("cedula", None)
        telefono=request.POST.get("telefono",None)
        direccion=request.POST.get("direccion",None)
        fechaNac=request.POST.get("fechaNac",None)
        imagen = request.FILES.get("url",None)
        fechaNac = datetime.strptime(fechaNac, "%Y-%m-%d").date()
        user=Cliente.objects.get(id_cliente=id)
        try:
            user.nombre=nombre
            user.apellido=apellido
            user.telefono=telefono
            user.fecha_Nac=fechaNac
            user.direccion=direccion
            user.usuario.cedula=cedula
            if(imagen!=None):
                user.usuario.foto.delete()
                user.usuario.foto=imagen
            user.usuario.save()
            user.save()
            res = {

            'valid': 'ok'
            }
            return JsonResponse(res,safe=False)
        except:
            res = {
            'valid': 'not'
            }
            return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

def getCliente(request):
    if request.method == 'GET':
        res = []
        #if request.GET.get("correo") == "gregorylopezjordan80@gmail.com":
            #return HttpResponse(status=400)
        if request.GET.get("correo")!=None:
            correo=request.GET.get("correo")
            #if correo == "gregorylopezjordan80@gmail.com":
                #return HttpResponse(status=400)
            user = Cliente.objects.select_related("usuario").filter(usuario__correo=correo).first()
            #if user.id_cliente == 165:
                #return HttpResponse(status=400)
            try:
                id_usuario=user.usuario.id_usuario
                cedula=user.usuario.cedula
                imagen=user.usuario.photo_url
            except:
                id_usuario=""
                cedula=""
                imagen=""
            if id_usuario!="":
                #if user.id_cliente == 165:
                    #return HttpResponse(status=400)
                diccionario={"id":user.id_cliente,"nombre":user.nombre,"apellido":user.apellido,"telefono":user.telefono,
                "correo":correo,"direccion":user.direccion,"fechaNac":user.fecha_Nac,"cedula":cedula,"imagen":imagen}
                res.append(diccionario)
            return JsonResponse(res,safe=False)
        else:
            users = Cliente.objects.select_related("usuario")
            for user in users:
                try:
                    id_usuario=user.usuario.id_usuario
                    if id_usuario == 167:
                        return HttpResponse(status=400)
                    cedula=user.usuario.cedula
                    imagen=user.usuario.photo_url
                    correo=user.usuario.correo
                except:
                    id_usuario=""
                    cedula=""
                    imagen=""
                    correo=""
                if id_usuario!="":
                    #if correo == "gregorylopezjordan80@gmail.com":
                        #return HttpResponse(status=400)
                    #if user.id_cliente == 165:
                        #return HttpResponse(status=400)
                    diccionario={"id":user.id_cliente,"id_usuario":id_usuario,"nombre":user.nombre,"apellido":user.apellido,
                    "telefono":user.telefono,"direccion":user.direccion,"fechaNac":user.fecha_Nac,"cedula":cedula,"imagen":imagen,"correo":correo}
                    res.append(diccionario)
            return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

def getCliente2(request):
    if request.method == 'GET':
        res = []
        if request.GET.get("correo")!=None:
            correo=request.GET.get("correo")
            user = Cliente.objects.select_related("usuario").filter(usuario__correo=correo).first()
            #if user.id_cliente == 165:
                #return HttpResponse(status=400)
            codigoUser=user.usuario.codigo_unico
            try:
                id_usuario=user.usuario.id_usuario
                cedula=user.usuario.cedula
                imagen=user.usuario.photo_url
                codigoUser=user.usuario.codigo_unico
            except:
                id_usuario=""
                cedula=""
                imagen=""
                codigoUser=""
            if id_usuario!="":
                #if user.id_cliente == 165:
                    #return HttpResponse(status=400)
                diccionario={"id":user.id_cliente,"nombre":user.nombre,"apellido":user.apellido,"telefono":user.telefono,
                "correo":correo,"direccion":user.direccion,"fechaNac":user.fecha_Nac,"cedula":cedula,"imagen":imagen,"codigo_unico":codigoUser}
                res.append(diccionario)
            return JsonResponse(res,safe=False)
        else:
            users = Cliente.objects.select_related("usuario")
            for user in users:
                try:
                    id_usuario=user.usuario.id_usuario
                    cedula=user.usuario.cedula
                    imagen=user.usuario.photo_url
                    codigoUser=user.usuario.codigo_unico
                    correo=user.usuario.correo
                except:
                    id_usuario=""
                    cedula=""
                    imagen=""
                    codigoUser=""
                    correo=""
                if id_usuario!="":
                    diccionario={"id":user.id_cliente,"id_usuario":id_usuario,"nombre":user.nombre,"apellido":user.apellido,
                    "telefono":user.telefono,"direccion":user.direccion,"fechaNac":user.fecha_Nac,"cedula":cedula,"imagen":imagen,"codigo_unico":codigoUser,"correo":correo}
                    res.append(diccionario)
            return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def getClienteCorreo(request):
    if request.method == "POST":
        response = json.loads(request.body)
        correo = response["correo"]

        clientefilter = Cliente.objects.filter(usuario__correo=correo)
        if clientefilter:
            cliente = Cliente.objects.get(usuario__correo=correo)
            stringi=cliente.nombre+" "+cliente.apellido
            response_data = {'valid': 'OK', 'valor':str(correo), 'receptor':stringi}
            return JsonResponse(response_data,safe=False)
        response_data = {'valid': 'NO', 'valor':str(correo)}
        return JsonResponse(response_data,safe=False)

@csrf_exempt
def getCodigo(request):
    if request.method == 'GET':
        if request.GET.get("id")!=None:
            id_cliente = request.GET.get("id")
            cliente=Cliente.objects.select_related().filter(id_cliente=id_cliente).first()
            usuario_id=cliente.usuario_id

            usuario=Usuario.objects.select_related().filter(id_usuario=usuario_id).first()
            codigo=usuario.codigo_unico

            #codigo_unico=Usuario.objects.filter(id_usuario=id_usuario)
            #print(codigo)

            return JsonResponse(codigo,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def registro(request):
    if request.method == 'POST':
        print("estoy en django, metodo registro ")
        print(request.body)
        response = json.loads(request.body)
        print(response)
        cedula = response["cedula"]
        email = response['email']
        contra =response['contrasena']
        nombre = response['nombre']
        apellido = response['apellido']
        #Creamos el codigo UNico
        def crear_codigo():
            claves=""
            num=random.randint(100,999)
            while len(claves)<4:
                letra=random.choice(string.ascii_letters)
                claves+=letra
            prefijo= claves.upper()[:2]
            sufijo= claves.upper()[2:]
            codigo=prefijo+str(num)+sufijo
            try:
                usuario=Usuario.objects.get(codigo_unico=str(codigo))
            except Usuario.DoesNotExist:
                usuario = None
            if((usuario) is None):
                return codigo
            else:
                crear_codigo()
        codigo=crear_codigo()
        #Fin crear codigo unico
        users=Usuario.objects.filter()
        for u2 in users :
            cr = u2.correo
            cn = u2.contrasena
            cd = u2.cedula
            if cr == email:
                response_data = {
                'valid': 'EMAIL'
                }
                return JsonResponse(response_data,safe=False)
            '''if cedula!=" " and cedula == cd:
                print("cedula repetida")
                response = {
                    'valid': 'CED'
                    }
                return JsonResponse(response,safe=False)'''
        msj2 = 'Bienvenido a Cabutos, es un placer que se una a nosotros'
        u =Usuario(cedula=cedula,correo=email,contrasena=contra)
        u =Usuario(cedula=cedula,correo=email,contrasena=contra,codigo_unico=codigo)
        print("usuario ",u)
        u.save()
        c = Cliente(nombre=nombre,apellido=apellido,usuario=u)
        c.save()
        try:
            oferta=Oferta.objects.filter().order_by("-cantidad").first()
            redes=RedSocial.objects.filter()
            html = render_to_string("Correos/bienvenido.html",{"data":c, "oferta":oferta,"redes":redes})
            msg = EmailMultiAlternatives('Bienvenido a Cabutos', html, 'cabutosoftware1@gmail.com', [email])
            msg.content_subtype = 'html'
            msg.mixed_subtype = 'related'
            msg.send()
        except:
            print("Error al enviar correo")
        response_data = {
                'valid': 'OK',
                #'foto': foto,
                'id': u.id_usuario,
                'nombre': nombre,
                'apellido': apellido
                }
        return JsonResponse(response_data,safe=False)

@csrf_exempt
def registro2(request):
    if request.method == 'POST':
        print("estoy en django, metodo registro ")
        print(request.body)
        response = json.loads(request.body)
        print(response)
        cedula = response["cedula"]
        email = response['email']
        contra =response['contrasena']
        nombre = response['nombre']
        apellido = response['apellido']
        telefono = response['telefono']
        #Creamos el codigo UNico
        def crear_codigo():
            claves=""
            num=random.randint(100,999)
            while len(claves)<4:
                letra=random.choice(string.ascii_letters)
                claves+=letra
            prefijo= claves.upper()[:2]
            sufijo= claves.upper()[2:]
            codigo=prefijo+str(num)+sufijo
            try:
                usuario=Usuario.objects.get(codigo_unico=str(codigo))
            except Usuario.DoesNotExist:
                usuario = None
            if((usuario) is None):
                return codigo
            else:
                crear_codigo()
        codigo=crear_codigo()
        #Fin crear codigo unico
        users=Usuario.objects.filter()
        for u2 in users :
            cr = u2.correo
            cn = u2.contrasena
            cd = u2.cedula
            if cr == email:
                response_data = {
                'valid': 'EMAIL'
                }
                return JsonResponse(response_data,safe=False)
            if cedula!=" " and cedula == cd:
                print("cedula repetida")
                response = {
                    'valid': 'CED'
                    }
                return JsonResponse(response,safe=False)
        msj2 = 'Bienvenido a Cabutos, es un placer que se una a nosotros'
        u =Usuario(cedula=cedula,correo=email,contrasena=contra)
        u =Usuario(cedula=cedula,correo=email,contrasena=contra,codigo_unico=codigo)
        print("usuario ",u)
        u.save()
        c = Cliente(nombre=nombre,apellido=apellido,usuario=u,telefono=telefono)
        c.save()
        try:
            oferta=Oferta.objects.filter().order_by("-cantidad").first()
            redes=RedSocial.objects.filter()
            html = render_to_string("Correos/bienvenido.html",{"data":c, "oferta":oferta,"redes":redes})
            msg = EmailMultiAlternatives('Bienvenido a Cabutos', html, 'cabutosoftware1@gmail.com', [email])
            msg.content_subtype = 'html'
            msg.mixed_subtype = 'related'
            msg.send()
        except:
            print("Error al enviar correo")
        response_data = {
                'valid': 'OK',
                #'foto': foto,
                'id': u.id_usuario,
                'nombre': nombre,
                'apellido': apellido
                }
        return JsonResponse(response_data,safe=False)

def imagenesCoded():
    bienvenido = base64.b64encode(open(settings.STATICFILES_DIRS[0] + '/img/correo/bienvenido.png', "rb").read()).decode()
    fb = base64.b64encode(open(settings.STATICFILES_DIRS[0] + '/img/correo/fb.png', "rb").read()).decode()
    ig = base64.b64encode(open(settings.STATICFILES_DIRS[0] + '/img/correo/ig.png', "rb").read()).decode()
    tk = base64.b64encode(open(settings.STATICFILES_DIRS[0] + '/img/correo/tk.png', "rb").read()).decode()
    tw = base64.b64encode(open(settings.STATICFILES_DIRS[0] + '/img/correo/tw.png', "rb").read()).decode()
    response_data = {
        'bienvenido': bienvenido,
        'fb':fb,
        'ig':ig,
        'tk':tk,
        'tw':tw,
        }
    return response_data

@csrf_exempt
def registrarDispositivo(request):
    if request.method == 'POST':
        print("estoy en django, metodo registro ")
        response = json.loads(request.body)
        print(response)
        registration_id = response["token"]
        usuario_id = response['usuario']
        user = Usuario.objects.filter(id_usuario=usuario_id).first()
        if usuario_id == 167:
            return HttpResponse(status=400)
        device = GCMDevice.objects.filter(registration_id =registration_id).first()
        if device != None:
            print(user)
            print(device)
            if (user == None or device.user == user):
                response_data = {
                'valid': 'usuarioRegistrado'
                }
            else:
                device.user = user
                device.save()
                response_data = {
                'valid': 'Dispositivo pertenece a otro usuario'
                }
        else:
            device = GCMDevice.objects.create(registration_id=registration_id,user=user,cloud_message_type="FCM")
            device.save()
            response_data = {
                'valid': 'OK'
                }
        return JsonResponse(response_data,safe=False)
    response_data = {
        'valid': 'NOT'
        }
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def login(request):

    if request.method == 'POST':
        print("estoy en django, metodo registro ")
        response = json.loads(request.body)
        print(response)
        email = response['correo']
        contra =response['contrasena']
        users = Usuario.objects.filter()
        print(users)
        for u in users :

            c = u.correo
            cn = u.contrasena
            nombre = obtener_nombre(email)
            apellido = obtener_apellido(email)
            if c == email and cn == contra:
                response_data = {
                'valid': 'OK',
                'id': u.id_usuario,
                'nombre': nombre,
                'apellido': apellido
                }
                return JsonResponse(response_data,safe=False)
    response_data = {
        'valid': 'NOT'
        }
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def envioReclamo(request):
    if request.method == 'POST':
        msj=request.POST.get("descripcion",None)
        imagen = request.FILES.get("url",None)
        correo="cabutosoftware1@gmail.com"
        reclamo=Reclamo(descripcion=msj,image=imagen)
        reclamo.save()
        try:
            print(reclamo.photo_url)
            email = EmailMessage('Nueva Sugerencia/Reclamo', msj, to=['cabutosoftware1@gmail.com'])
            email.send()
            #send_mail('Nueva Sugerencia/Reclamo',msj,'cabutosoftware1@gmail.com',['cabutosoftware1@gmail.com'],fail_silently=True,html_message= '<html><body><img src="'+reclamo.photo_url+'"></img><p>'+msj+'</p></body></html>')
        except e:
            print("Error al enviar correo")
            print(e)
        response_data = {
            'valid': 'ok'
            }
        return JsonResponse(response_data,safe=False)

@csrf_exempt
def cambioContra(request):
    n = random.randint(1999,2999)
    msj = 'Este es su nueva contraseña '+str(n)+', no se olvide cambiarla apenas pueda'

    if request.method == 'POST':
        response = json.loads(request.body)
        #correo = response['correo']
        print(json.loads(request.body))
        users = Usuario.objects.filter()
        for user in users:
            if user.correo == response:
                print("Si existe el correo")
                print(n)
                email = EmailMessage('Correo enviado: Cambio de contraseña', msj, to=[user.correo])
                email.send()
                #send_mail('Correo enviado: Cambio de contraseña',msj,'cabutosoftware1@gmail.com',[user.correo],fail_silently=False,html_message= '<html><body>'+msj+'</body></html>')
                user.contrasena = n
                print(user.contrasena)
                user.save()
                response_data ={
                    'valid': 'OK'
                    }
                return JsonResponse(response_data,safe=False)

    response_data = {
        'valid': 'NOT'
        }
    return JsonResponse(response_data,safe=False)

def es_correo_valido(correo):
    expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, correo) is not None

def contar(cedula):
    contador = contador = len(str(cedula))
    return contador

def obtener_nombre(pk):
    clientes = Cliente.objects.filter()
    nombre = ""
    for c in clientes:
        u_id = c.usuario
        cedula = str(u_id)
        if(cedula == pk):
            print("lo encontre")
            nombre = nombre + c.nombre
            nombre = c.nombre
            return nombre
    print(nombre)

def obtener_apellido(pk):

    clientes = Cliente.objects.filter()
    for c in clientes:
        u_id = c.usuario
        cedula =str(u_id)
        if(cedula == pk):
            print("lo encontre")
            apellido = c.apellido
            return apellido

@csrf_exempt
def addCarrito(request):
    if request.method == "POST":
        response = json.loads(request.body)
        print("Response del addCarrito",response)
        print("Nombre del producto", response["nombre"])
        producto=Producto.objects.get(nombre=response["nombre"])
        cantidad = int(response["cantidad"])
        mail = response["correo"]
        print(mail)
        cliente=Cliente.objects.select_related("usuario").filter(usuario__correo=mail).first()
        try:
            carrito=Carrito.objects.get(id_cliente=cliente)
            try:
                carritoDetalle = Detalle_Carrito.objects.filter(id_carrito=carrito)
                total = carritoDetalle.count()
                print("Esta es la cantidad qie tiene el query",total)
                if total == 0:
                    print("No existe Carrito detalle")
                    subtotal=producto.precio*int(cantidad)
                    print("Esta es la cantidad que estoy enviando: ",cantidad)
                    detalle_producto = Detalle_Carrito(id_carrito=carrito,id_producto=producto,cantidad=cantidad,precio=subtotal)
                    print(detalle_producto)
                    detalle_producto.save()
                    response_data = {
                        'valid':'OK'
                    }
                    return JsonResponse(response_data,safe=False)
                else:
                    if lecturaProducto(str(producto.nombre),carritoDetalle) == True:
                        if cambiarCantidadProducto(producto.nombre,cantidad,carritoDetalle) == True:
                            response_data = {
                                'valid': 'OK'
                            }
                            return JsonResponse(response_data,safe=False)
                    else:
                        subtotal = producto.precio*int(cantidad)
                        detalle_carrito = Detalle_Carrito(id_carrito=carrito,id_producto=producto,cantidad=cantidad,precio=subtotal)
                        detalle_carrito.save()
                        response_data={
                            'valid':'OK'
                        }
                        return JsonResponse(response_data,safe=False)
            except Detalle_Carrito.DoesNotExist:
                subtotal=producto.precio*int(cantidad)
                detalle_carrito=Detalle_Carrito(id_carrito=carrito,id_producto=producto,cantidad=cantidad,precio=subtotal)
                detalle_carrito.save()
                response_data = {
                  'valid': 'OK'
                }
                return JsonResponse(response_data,safe=False)
        except Carrito.DoesNotExist:
            carrito_new=Carrito(id_cliente=cliente)
            carrito_new.save()
            subtotal=producto.precio*int(cantidad)
            detalle_carrito_new=Detalle_Carrito(id_carrito=carrito_new,id_producto=producto,cantidad=cantidad,precio=subtotal)
            detalle_carrito_new.save()
            response_data = {
              'valid': 'OK'
            }
            return JsonResponse(response_data,safe=False)

    response_data = {
        'valid': 'NOT'
    }
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def addCombo(request):
    if request.method == "POST":
        response_data=[]
        combo=Combo.objects.get(id_combo=reponse["id"])
        response = json.loads(request.body)
        cantidad = response["cantidad"]
        tiene_combo=response["tiene_combo"]
        carrito=Carrito.objects.filter()
        usuario=Usuario.objects.get(correo=response["correo"])
        cliente=Cliente.objects.get(usuario=usuario)
        detalle_combo=Detalle_Combo.objects.get(id_carrito=carrito.id_carrito)
        if tiene_combo:
            carrito.tiene_combo=tiene_combo
            carrito.save()
            if detalle_combo.id_combo == combo:
                detalle_combo.cantidad=detalle_combo.cantidad+int(cantidad)
                detalle_combo.save()
                response_data = {
                'valid': 'OK'
                }
                return JsonResponse(response_data,safe=False)
            else:
                detalle_combo=Detalle_Combo(id_carrito=carrito, id_combo=combo,cantidad=cantidad)
                detalle_combo.save()
                response_data ={
                    'valid': 'OK'
                }
                return JsonResponse(response_data,safe=False)
        else:
            return JsonResponse(response_data,safe=False)
    response_data = {
        'valid': 'NOT'
        }
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def addOferta(request):

    if request.method == "POST":
        response = json.loads(request.body)
        print("Response del add oferta",response)
        cantidad = int(response["cantidad"])
        oferta=Oferta.objects.get(nombre=response["nombre"])
        usuario=Usuario.objects.get(correo=response["correo"])
        cliente=Cliente.objects.get(usuario=usuario)
        try:
            carrito=Carrito.objects.get(id_cliente=cliente)
            print("Este es el carrito del cliente",carrito)
            print("este es el id del carrito",carrito.id_carrito)
            try:
                detalle_oferta = Carrito_Oferta.objects.filter(id_carrito=carrito)
                total = detalle_oferta.count()
                print("Esta es la cantidad qie tiene el query",total)
                if total == 0:
                    print("No existe Carrito Oferta")
                    subtotal=oferta.precio*int(cantidad)
                    detalle_oferta = Carrito_Oferta(id_carrito=carrito,id_oferta=oferta,precio=subtotal,cantidad=cantidad)
                    print(detalle_oferta)
                    detalle_oferta.save()
                    response_data = {
                        'valid': 'OK'
                    }
                    return JsonResponse(response_data,safe=False)
                    print("Este es el detalle_oferta de mi funcion verificar",detalle_oferta)
                else:
                    if lecturaOferta(str(oferta.nombre),detalle_oferta) == True:
                        if cambiarCantidad(oferta.nombre,cantidad,detalle_oferta) == True:
                            response_data = {
                                'valid': 'OK'
                            }
                            return JsonResponse(response_data,safe=False)
                    else:
                        subtotal = oferta.precio*int(cantidad)
                        detalle = Carrito_Oferta(id_carrito=carrito,id_oferta=oferta,precio=subtotal,cantidad=cantidad)
                        print("aqui no existe el esta oferta",detalle)
                        detalle.save()
                        response_data = {
                            'valid':'OK'
                        }
                        return JsonResponse(response_data,safe=False)
            except Carrito_Oferta.DoesNotExist:
            #else:
                print("No existe Carrito Oferta")
                subtotal=oferta.precio*int(cantidad)
                detalle_oferta=Detalle_Oferta(id_carrito=carrito,id_oferta=oferta,precio=subtotal,cantidad=cantidad)
                print(detalle_oferta)
                detalle_oferta.save()
                response_data = {
                  'valid': 'OK'
                }
                return JsonResponse(response_data,safe=False)
        except Carrito.DoesNotExist:
        #else:
            print("No existe Carrito")
            carrito_new=Carrito(id_cliente=cliente)
            carrito_new.save()
            detalle_oferta_new=Carrito_Oferta(id_carrito=carrito_new,id_oferta=oferta)
            detalle_oferta_new.save()
            response_data = {
              'valid': 'OK'
            }
            return JsonResponse(response_data,safe=False)

    response_data = {
        'valid': 'NOT'
    }
    return JsonResponse(response_data,safe=False)

def getHorario(request):
    if request.method == "GET":
        id_establecimiento=request.GET.get("id")
        dia=request.GET.get("dia")
        establecimiento=Establecimiento.objects.filter(id_establecimiento=id_establecimiento).first()
        horario=Horario.objects.filter(establecimiento=establecimiento).filter(dia=str(dia)).values()
        data = list(horario)
        res = {'horario': data,}
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def getCarrito(request):
    response={}
    if request.method == "POST":
        res = json.loads(request.body)
        response=res
        print("Response del Get Carrito")
        print(res)
        usuario=Usuario.objects.get(correo=response["correo"])
        cliente=Cliente.objects.get(usuario=usuario)
        try:
            carrito=Carrito.objects.get(id_cliente=cliente)
            try:
                detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito)
                detalle_oferta=Carrito_Oferta.objects.filter(id_carrito=carrito)
                detalle_combo=Carrito_Combo.objects.filter(id_carrito=carrito)
                detalle_cupon=Carrito_Cupones.objects.filter(id_carrito=carrito)
                detalle_tarjeta_monto=Carrito_Tarjeta_Monto.objects.filter(id_carrito=carrito)
                detalle_tarjeta_producto=Carrito_Tarjeta_Producto.objects.filter(id_carrito=carrito)
                total_oferta = detalle_oferta.count()
                total_producto = detalle_producto.count()
                total_cupon = detalle_cupon.count()
                total_tarjeta_monto = detalle_tarjeta_monto.count()
                total_tarjeta_producto = detalle_tarjeta_producto.count()
                total_combo = detalle_combo.count()
                total=total_oferta+0+total_cupon+total_combo+total_tarjeta_monto+total_tarjeta_producto
                productoNecesario = False
                esValidoProducto= True
                totalNecesarioMonto=0.0
                restaMonto=0.0
                if total_cupon > 0:
                    for cup in detalle_cupon:
                        if cup.id_cupon.tipo =='P':
                            if total_producto > 0:
                                estaEnCarrito=False
                                cuponesProductos= Cupones_Producto.objects.get(id_cupon=cup.id_cupon.id_cupon)
                                productoTemp = Producto.objects.get(id_producto = cuponesProductos.id_producto.id_producto)
                                #productoNecesario = productoTemp.nombre
                                for prod in detalle_producto:
                                    if productoTemp.id_producto == prod.id_producto.id_producto:
                                        if prod.cantidad >= cuponesProductos.cantidad:
                                            estaEnCarrito=True
                                #if not estaEnCarrito:
                                productoNecesario = productoTemp.id_producto
                                esValidoProducto= "Se necesita " + str(cuponesProductos.cantidad) + " " + str(productoTemp.nombre) + " para canjear el cupón"
                                #else:
                                #esValidoProducto= True
                            else:
                                esValidoProducto=total_producto
                        if cup.id_cupon.tipo =='M':
                            cuponesMonto= Cupones_Monto.objects.get(id_cupon=cup.id_cupon.id_cupon)
                            if cuponesMonto.monto > totalNecesarioMonto:
                                totalNecesarioMonto = cuponesMonto.monto

                        #cuponesMonto= Cupones.objects.filter(id_cupon=e.id_cupon,tipo='M')
                if total_tarjeta_monto > 0:
                    for tarjeta in detalle_tarjeta_monto:
                        tarjeta_monto= Tarjeta_Monto.objects.get(id_tarjeta=tarjeta.id_tarjeta.id_tarjeta)
                        restaMonto=restaMonto+tarjeta_monto.monto

                if total_tarjeta_producto > 0:
                    for tarjeta in detalle_tarjeta_producto:
                        tarjeta_producto= Tarjeta_Producto.objects.get(id_tarjeta=tarjeta.id_tarjeta.id_tarjeta)

                res=[{"total":total,"productos":getProductoxCarrito(detalle_producto),"ofertas":getOfertaxCarrito(detalle_oferta),
                "combos":getComboxCarrito(detalle_combo),"cupon":getCuponxCarrito(detalle_cupon),
                "tarjeta":getTarjetaMontoxCarrito(detalle_tarjeta_monto),"tarjeta2":getTarjetaProductoxCarrito(detalle_tarjeta_producto),
                "id":carrito.id_carrito,"esValidoProducto":esValidoProducto,"totalNecesarioMonto":totalNecesarioMonto,
                "productoNecesario":productoNecesario, "restaMonto":restaMonto}]
                print(res)
                return JsonResponse(res,safe=False)
            except Detalle_Carrito.DoesNotExist or Carrito_Oferta.DoesNotExist or Carrito_Combo.DoesNotExist:
                print("No hay productos ni ofertas ni combos")
                total_oferta = detalle_oferta.count()
                total_producto = detalle_producto.count()
                total_cupon = detalle_cupon.count()
                total_combo = detalle_combo.count()
                total=total_oferta+total_producto+total_cupon+total_combo
                res=[{"total":total,"productos":getProductoxCarrito(detalle_producto),"ofertas":getOfertaxCarrito(detalle_oferta),
                "combos":getComboxCarrito(detalle_combo),"cupon":getCuponxCarrito(detalle_cupon),"id":carrito.id_carrito}]
                return JsonResponse(res,safe=False)
        except Carrito.DoesNotExist:
            print("Carrito Nuevo creado")
            carrito=Carrito(id_cliente=cliente)
            carrito.save()
            response_data = {
              'valid': 'OK',
              'id':carrito.id_carrito,
              'total': 0
            }
            return JsonResponse(response_data,safe=False)

    return HttpResponse(status=400)

@csrf_exempt
def checkCupones(request):
    if request.method == "POST":
        response = json.loads(request.body)

        id_cupon = response["id_cupon"]
        id_cliente = response["id_cliente"]
        codigos= Codigo.objects.filter(codigo=str(code)).exclude(estado='I')
        if codigos:
            codigo = Codigo.objects.get(codigo=str(code))
            cliente = Cliente.objects.get(id_cliente=id_cliente)
            codigosclientes= Codigo_Cliente.objects.filter(id_codigo=codigo, id_cliente=cliente)
            if codigosclientes:
                response_data = {'valid': 'talvez',}
                return JsonResponse(response_data,safe=False)
            codigoXusuario=Codigo_Cliente(id_codigo=codigo,id_cliente=cliente)
            codigoXusuario.save()
            response_data = {'valid': 'OK',}
            return JsonResponse(response_data,safe=False)
        response_data = {'valid': 'NO', 'valor':str(code)}
        return JsonResponse(response_data,safe=False)

@csrf_exempt
def modCantidades(request):
    response={}
    if request.method == "POST":
        response = json.loads(request.body)
        carrito = Carrito.objects.get(id_carrito=response["carrito"])
        articulos =response["productos"]
        for articulo in articulos:
            tipo=articulo["id"].split("_")[0]
            id_articulo=articulo["id"].split("_")[1]
            cantidad=int(articulo["cantidad"])
            if(tipo == "Producto"):
                detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito).filter(id_producto__id_producto=id_articulo).first()
                if(detalle_producto!=None):
                    if(cantidad==0):
                        detalle_producto.delete()
                    else:
                        detalle_producto.cantidad=cantidad
                        detalle_producto.precio=detalle_producto.id_producto.precio*cantidad
                        detalle_producto.save()
            elif(tipo == "Oferta"):
                detalle_oferta=Carrito_Oferta.objects.filter(id_carrito=carrito).filter(id_oferta__id_oferta=id_articulo).first()
                if(detalle_oferta!=None):
                    if(cantidad==0):
                        detalle_oferta.delete()
                    else:
                        detalle_oferta.cantidad=cantidad
                        detalle_oferta.precio=detalle_oferta.id_oferta.precio*cantidad
                        detalle_oferta.save()
            elif(tipo == "Combo"):
                detalle_combo=Carrito_Combo.objects.filter(id_carrito=carrito).filter(id_combo__id_combo=id_articulo).first()
                if(detalle_combo!=None):
                    if(cantidad==0):
                        detalle_combo.delete()
                    else:
                        detalle_combo.cantidad=cantidad
                        detalle_combo.precio=detalle_combo.id_combo.precio*cantidad
                        detalle_combo.save()
            elif(tipo == "Cupon"):
                detalle_cupon=Carrito_Cupones.objects.filter(id_carrito=carrito).filter(id_cupon__id_cupon=id_articulo).first()
                if(detalle_cupon!=None):
                    if(cantidad==0):
                        detalle_cupon.delete()
                    else:
                        detalle_cupon.cantidad=cantidad
                        detalle_cupon.precio=detalle_cupon.id_cupon.precio*cantidad
                        detalle_cupon.save()
        response_data = {
              'valid': 'OK',
        }
        return JsonResponse(response_data,safe=False)

def getProductoxCarrito(detalle_producto):
    res=[]
    try:
        for product in detalle_producto:
            print("Son los producto",product)
            if product.id_producto != None:
                id="Producto_"+str(product.id_producto.id_producto)
                pro=Producto.objects.filter(id_producto=product.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
                if(pro.suma == None or pro.suma<=0):
                    product.delete()
                elif(pro.suma!= None and pro.suma-product.cantidad<0 and pro.suma>0):
                    product.cantidad=pro.suma
                    product.save()
                    diccionario={"id_producto":product.id_producto.id_producto,"id_unico":id,"nombre_producto":product.id_producto.nombre,
                                "precio_producto":product.id_producto.precio, "estado_producto":product.id_producto.estado,
                                "imagen_producto":product.id_producto.photo_url,"cantidad":product.cantidad, "subtotal":product.precio, "suma":pro.suma}
                    res.append(diccionario)
                else:
                    diccionario={"id_producto":product.id_producto.id_producto,"id_unico":id,"nombre_producto":product.id_producto.nombre,
                                "precio_producto":product.id_producto.precio, "estado_producto":product.id_producto.estado,
                                "imagen_producto":product.id_producto.photo_url,"cantidad":product.cantidad, "subtotal":product.precio, "suma":pro.suma}
                    res.append(diccionario)
            else:
                product.delete()
        return res
    except Detalle_Carrito.DoesNotExist:
    #else:
        print("No existe carrito productos")
        dicc={}
        res.append(dicc)
        return res

def getOfertaxCarrito(detalle_oferta):
    res=[]
    try:
        for oferta in detalle_oferta:
            if oferta.id_oferta != None:
                id="Oferta_"+str(oferta.id_oferta.id_oferta)
                if(oferta.id_oferta.cantidad<=0):
                    oferta.delete()
                elif(oferta.id_oferta.cantidad-oferta.cantidad<0 and oferta.id_oferta.cantidad>0):
                    oferta.cantidad=oferta.id_oferta.cantidad
                    oferta.save()
                    diccionario={"id_oferta":oferta.id_oferta.id_oferta,"id_unico":id,"nombre_oferta":oferta.id_oferta.nombre,
                                "precio_oferta":oferta.id_oferta.precio, "imagen_oferta":oferta.id_oferta.photo_url, "cantidad_oferta":oferta.cantidad,
                                "subtotal_oferta":oferta.precio,"cantidad":oferta.id_oferta.cantidad}
                    res.append(diccionario)
                else:
                    diccionario={"id_oferta":oferta.id_oferta.id_oferta,"id_unico":id,"nombre_oferta":oferta.id_oferta.nombre,
                                "precio_oferta":oferta.id_oferta.precio, "imagen_oferta":oferta.id_oferta.photo_url, "cantidad_oferta":oferta.cantidad,
                                "subtotal_oferta":oferta.precio,"cantidad":oferta.id_oferta.cantidad}
                    res.append(diccionario)
            else:
                oferta.delete()
        return res
    except Carrito_Oferta.DoesNotExist:
    #else:
        print("No existe carrito oferta")
        dicc={}
        res.append(dicc)
        return dicc

def getComboxCarrito(detalle_combo):
    res=[]
    try:
        for combo in detalle_combo:
            if combo.id_combo != None:
                id="Combo_"+str(combo.id_combo.id_combo)
                diccionario={"id_combo":combo.id_combo.id_combo,"id_unico":id,"nombre":combo.id_combo.nombre,
                "precio":combo.id_combo.precio, "estado":combo.id_combo.estado, "imagen":combo.id_combo.photo_url,
                "cantidad":combo.cantidad, "subtotal_combo":combo.precio,"cantidad":combo.id_combo.cantidad_disponible}
                res.append(diccionario)
            else:
                combo.delete()
        return res
    except Carrito_Combo.DoesNotExist:
    #else:
        print("No existe carrito combo")
        dicc={}
        res.append(dicc)
        return dicc

def getCuponxCarrito(detalle_cupon):
    res=[]
    try:
        for cupon in detalle_cupon:
            if cupon.id_cupon != None:
                id="Cupon_"+str(cupon.id_cupon.id_cupon)
                if(cupon.id_cupon.cantidad<=0):
                    cupon.delete()
                else:
                    diccionario={"id_cupon":cupon.id_cupon.id_cupon,"id_unico":id,"nombre_cupon":cupon.id_cupon.nombre,
                                "precio_cupon":cupon.id_cupon.precio, "imagen_cupon":cupon.id_cupon.photo_url, "cantidad_cupon":cupon.cantidad,"cantidad":cupon.id_cupon.cantidad,
                                "subtotal_cupon":cupon.precio}
                    res.append(diccionario)
            else:
                cupon.delete()
        return res
    except Carrito_Oferta.DoesNotExist:
    #else:
        print("No existe carrito Cupon")
        dicc={}
        res.append(dicc)
        return dicc

def getTarjetaMontoxCarrito(detalle_tarjeta_monto):
    res=[]
    try:
        for tarjeta in detalle_tarjeta_monto:
            if tarjeta.id_tarjeta != None:
                id="Tarjeta_Monto_"+str(tarjeta.id_tarjeta.id_tarjeta)
                diccionario={"id_tarjeta":tarjeta.id_tarjeta.id_tarjeta,"id_unico":id,"imagen_tarjeta":"https://cdn-icons-png.flaticon.com/512/3663/3663716.png","cantidad_tarjeta":"1",
                            "monto_tarjeta":tarjeta.id_tarjeta.monto,
                            "subtotal_tarjeta":tarjeta.precio}
                res.append(diccionario)
            else:
                tarjeta.delete()
        return res
    except Carrito_Oferta.DoesNotExist:
    #else:
        print("No existe carrito Tarjeta")
        dicc={}
        res.append(dicc)
        return dicc

def getTarjetaProductoxCarrito(detalle_tarjeta_producto):
    res=[]
    try:
        for tarjeta in detalle_tarjeta_producto:
            if tarjeta.id_tarjeta != None:
                id="Tarjeta_Monto_"+str(tarjeta.id_tarjeta.id_tarjeta)
                diccionario={"id_tarjeta":tarjeta.id_tarjeta.id_tarjeta,"id_unico":id,"imagen_tarjeta":"https://cdn-icons-png.flaticon.com/512/3663/3663716.png","cantidad_tarjeta":"1",
                            "monto_tarjeta":0,
                            "subtotal_tarjeta":0}
                res.append(diccionario)
            else:
                tarjeta.delete()
        return res
    except Carrito_Oferta.DoesNotExist:
    #else:
        print("No existe carrito Tarjeta")
        dicc={}
        res.append(dicc)
        return dicc

def lecturaOferta(nombre,oxfs):
    for oxf in oxfs:
        if str(oxf.id_oferta.nombre) == nombre:
            return True
    return False

def cambiarCantidad(nombre,cantidad,oxfs):
    for oxf in oxfs:
        if str(oxf.id_oferta.nombre) == nombre:
            oxf.cantidad=oxf.cantidad+int(cantidad)
            oxf.precio=oxf.id_oferta.precio*oxf.cantidad
            oxf.save()
            return True
    return False

#def verificar(carrito,oferta,cantidad):
#    print("este es el id del carrito",id)
#    carritoOferta = Carrito_Oferta.objects.filter(id_carrito=carrito)
#    total = carritoOferta.count()
#    print("Esta es la cantidad qie tiene el query",total)
#    if total == 0:
#        print("No existe Carrito Oferta")
#        subtotal=oferta.precio*int(cantidad)
#        detalle_oferta = Carrito_Oferta(id_carrito=carrito,id_oferta=oferta,precio=subtotal,cantidad=cantidad)
#        print(detalle_oferta)
#        detalle_oferta.save()
#        oferta_detalle=Carrito_Oferta.objects.filter(id_carrito=carrito)
#        return oferta_detalle
#    return carritoOferta

#def verificarProducto(carrito,producto,cantidad):
#    print("este es el id del carrito",id)
#    carritoDetalle = Detalle_Carrito.objects.filter(id_carrito=carrito)
#    total = carritoDetalle.count()
#    print("Esta es la cantidad qie tiene el query",total)
#    if total == 0:
#        print("No existe Carrito detalle")
#        subtotal=producto.precio*int(cantidad)
#        print("Esta es la cantidad que estoy enviando: ",cantidad)
#        detalle_producto = Detalle_Carrito(id_carrito=carrito,id_producto=producto,cantidad=cantidad,precio=subtotal)
#        print(detalle_producto)
#
#        return detalle_producto
#    return carritoDetalle

def lecturaProducto(nombre,oxfs):
    print(oxfs)
    for oxf in oxfs:
        print(oxf.id_producto.nombre)
        if str(oxf.id_producto.nombre) == nombre:
            return True
    return False

def cambiarCantidadProducto(nombre,cantidad,oxfs):
    for oxf in oxfs:
        print(oxf.id_producto.nombre)
        if str(oxf.id_producto.nombre) == nombre:
            print("Esta es la cantidad",cantidad)
            oxf.cantidad=oxf.cantidad+int(cantidad)
            oxf.precio=oxf.id_producto.precio*oxf.cantidad
            oxf.save()
            return True
    return False

def politica(request):
    res = []
    if request.method=="GET":
        pol = Politica.objects.last()
        print(pol)
        if pol != None:
            print(pol.detalle)
            diccionario = {'id': pol.id_politica,'detalle':pol.detalle}
            print(diccionario)
            res.append(diccionario)
            print(res)
            return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def quitar(request):
    if request.method == "POST":
        res = json.loads(request.body)
        nombre = res["nombre"]
        correo = res["correo"]
        usuario=Usuario.objects.get(correo=correo)
        cliente=Cliente.objects.get(usuario=usuario)
        carrito=Carrito.objects.get(id_cliente=cliente)
        detalle_oferta= Carrito_Oferta.objects.filter(id_carrito=carrito.id_carrito)
        #detalle_combo = Detalle_Combo.objects.get(id_carrito=carrito.id_carrito)
        detalle_carrito = Detalle_Carrito.objects.filter(id_carrito=carrito)
        detalle_cupon = Carrito_Cupones.objects.filter(id_carrito=carrito)
        detalle_tarjeta_monto=Carrito_Tarjeta_Monto.objects.filter(id_carrito=carrito)
        detalle_tarjeta_producto=Carrito_Tarjeta_Producto.objects.filter(id_carrito=carrito)
        total_oferta = detalle_oferta.count()
        total_producto = detalle_carrito.count()
        total_cupon = detalle_cupon.count()
        total_tarjeta_monto = detalle_tarjeta_monto.count()
        total_tarjeta_producto = detalle_tarjeta_producto.count()
        print("Este es mi usuario",usuario)
        print("Este es mi cliente",cliente)
        print("Este es mi carrito",carrito)
        print("Este es mi detalle oferta",detalle_oferta,"contiene un total de",total_oferta)
        #print(detalle_combo)
        print("Este es mi detalle carrito",detalle_carrito,"contiene un total de",total_producto)
        if total_producto !=0:
            for producto in detalle_carrito:
                if str(producto.id_producto.nombre) == str(nombre):
                    print("lo que necesito es un producto")
                    producto.delete()
                    response_data = {
                        'valid': 'OK'
                        }
                    return JsonResponse(response_data,safe=False)
        if total_oferta != 0:
            for oferta in detalle_oferta:
                if str(oferta.id_oferta.nombre) == str(nombre):
                    print("lo que necesito es una oferta")
                    oferta.delete()
                    response_data = {
                        'valid': 'OK'
                        }
                    return JsonResponse(response_data,safe=False)
        if total_cupon != 0:
            for cupons in detalle_cupon:
                if str(cupons.id_cupon.nombre) == str(nombre):
                    print("lo que necesito es un cupon")
                    cupons.delete()
                    response_data = {
                        'valid':'OK'
                        }
                    return JsonResponse(response_data,safe=False)
        if total_tarjeta_monto != 0:
            for tarjeta in detalle_tarjeta_monto:
                if str(tarjeta.id_tarjeta.id_tarjeta) == str(nombre):
                    print("lo que necesito es una tarjeta de monto")
                    tarjeta.delete()
                    response_data = {
                        'valid':'OK'
                        }
                    return JsonResponse(response_data,safe=False)
        if total_tarjeta_producto != 0:
            for tarjeta in detalle_tarjeta_producto:
                if str(tarjeta.id_tarjeta.id_tarjeta) == str(nombre):
                    print("lo que necesito es una tarjeta de monto")
                    tarjeta.delete()
                    response_data = {
                        'valid':'OK'
                        }
                    return JsonResponse(response_data,safe=False)
        else:
            response_data = {
                'valid': 'NOT', "nombre":nombre
                }
            return JsonResponse(response_data,safe=False)
    return HttpResponse(status=400)


@csrf_exempt
def getCupones(request):
    if request.method == 'GET':
        print("estoy dentro del getCupones")
        res = []
        cupones = Cupones.objects.filter(cantidad__gt=0, estado="A")
        cupones = cupones.filter(fecha_inicio__lte=datetime.today())
        cupones = cupones.filter(fecha_fin__gte=datetime.today())
        for cupon in cupones:
            print(cupon.photo_url)
            diccionario = {"id":cupon.id_cupon,"nombre":cupon.nombre,"descripcion":cupon.descripcion,"cantidad":cupon.cantidad,
            "imagen":cupon.photo_url}
            res.append(diccionario)
            print("Esto es lo que voy a enviar",res)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)
    #if request.method == 'POST':
        #return addCupon(request)
    #return HttpResponse(status=400)


@csrf_exempt
def getDatosCupon(request, name):
    if request.method == 'GET':
        cupon = Cupones.objects.get(nombre=name)
        if cupon.tipo =="M":
            cuponMonto = Cupones_Monto.objects.get(nombre=name)
            res = {"nombre": cuponMonto.nombre, "monto": cuponMonto.monto, "tipo": "M"}
        if cupon.tipo == "P":
            cuponProducto = Cupones_Producto.objects.get(nombre=name)
            res = {"nombre": cuponProducto.nombre, "cantidad": cuponProducto.cantidad, "nombreProducto":cuponProducto.id_producto.nombre, "tipo": "P"}
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def getCuponesPersonales(request, id):
    if request.method == 'GET':
        print("estoy dentro del getCupones")
        res = []
        cupones = Cupones.objects.filter(cantidad__gt=0, estado="A")
        cupones = cupones.filter(fecha_inicio__lte=datetime.today())
        cupones = cupones.filter(fecha_fin__gte=datetime.today())
        establecimiento = 1
        if request.GET.get("establecimiento")!= None:
            establecimiento = request.GET.get("establecimiento")
        cupones = cupones.filter(id_establecimiento = establecimiento)
        for cupon in cupones:
            print(cupon.photo_url)
            diccionario = {"id":cupon.id_cupon,"nombre":cupon.nombre,"descripcion":cupon.descripcion,"cantidad":cupon.cantidad,
            "imagen":cupon.photo_url}
            res.append(diccionario)
            print("Esto es lo que voy a enviar",res)
        cuponesCodigo = Codigo_Cliente.objects.filter(id_cliente = id).exclude(estado='I')
        for cupon in cuponesCodigo:
            diccionario = {"id":cupon.id_codigo.id_codigo,"nombre":cupon.id_codigo.codigo,"descripcion":cupon.id_codigo.descripcion,"cantidad":cupon.id_codigo.cantidad,"imagen":cupon.id_codigo.photo_url}
            res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def getCuponesHistorial(request, id):
    if request.method == 'GET':
        print("estoy dentro del historial")
        res = []
        pedidos = Pedido.objects.filter(cliente=id)
        for pedidoo in pedidos:
            cuponP = Cupon_Pedido.objects.filter(pedido=pedidoo)
            if len(cuponP)!=0:
                for cupon in cuponP:
                    diccionario = {"id":cupon.cupon.id_cupon,"nombre":cupon.cupon.nombre,"descripcion":cupon.cupon.descripcion, "fecha": cupon.pedido.fecha, "imagen": cupon.cupon.photo_url}
                    res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)


@csrf_exempt
def getNotificaciones(request):
    if request.method == 'GET':
        res = []
        notificaciones = Notificacion.objects.filter()
        for noti in notificaciones:
            diccionario = {"id":noti.id_notificacion,"asunto":noti.asunto,"mensaje":noti.mensaje,"imagen":noti.photo_url,
            "fecha":noti.registro,"tipo":noti.tipo,"estado":noti.estado}
            res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def getNotificacionUnica(request, titulo):
    if request.method == 'GET':
        res = []
        notificacions= Notificacion.objects.filter(asunto = titulo)
        for notificacion in notificacions:
            diccionario={"id":notificacion.id_notificacion,"asunto":notificacion.asunto,"mensaje":notificacion.mensaje,
            "fecha":notificacion.registro,"imagen":notificacion.photo_url}
            res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)


@csrf_exempt
def actualizarNotificacion(request):
    if request.method == "POST":
        res = json.loads(request.body)
        print("Esto es me envia el movil",res)
        data_noti = buscarNoti(res)
        print("esto obtengo al buscar la notificacion por id",data_noti)
        if data_noti != False:
            print("voy a actulizar el estado")
            data_noti.estado = 'OK'
            data_noti.save()
            response_data = {
                'valid':'OK'
                }
            print("estado actualizado")
            return JsonResponse(response_data,safe=False)
        response_data ={
            'valid':'NOT'
            }
        return JsonResponse(response_data,safe=False)
    return HttpResponse(status=400)
    #response ={
    #    'valid':'NOT'
    #    }
    #return JsonResponse(response,safe=False)

def buscarNoti(id):
    response=False
    notificaciones = Notificacion.objects.filter()
    for noti in notificaciones:
        if str(noti.id_notificacion) == str(id):
            return noti
    return response


#def carrito_cupo:
@csrf_exempt
def addCupon(request):
    print("estoy en add cupon")
    if request.method == "POST":
        response = json.loads(request.body)
        print("Response del addCupon",response)
        print("Nombre ", response["nombre"])
        cupon=Cupones.objects.get(nombre=response["nombre"])
        cantidad = int(response["cantidad"])
        mail = response["correo"]
        print(mail)
        cliente=Cliente.objects.select_related("usuario").filter(usuario__correo=mail).first()
        try:
            carrito=Carrito.objects.get(id_cliente=cliente)
            try:
                carritoDetalle = Carrito_Cupones.objects.filter(id_carrito=carrito)
                total = carritoDetalle.count()
                print("Esta es la cantidad qie tiene el query",total)
                if total == 0:
                    print("No existe Carrito cupon")
                    subtotal=cupon.precio*int(cantidad)
                    print("Esta es la cantidad que estoy enviando: ",cantidad)
                    detalle_cupon = Carrito_Cupones(id_carrito=carrito,id_cupon=cupon,cantidad=cantidad,precio=subtotal)
                    print(detalle_cupon)
                    detalle_cupon.save()
                    response_data = {
                        'valid':'OK'
                    }
                    return JsonResponse(response_data,safe=False)
                else:
                    if lecturaCupon(str(cupon.nombre),carritoDetalle) == True:
                        response_data = {
                                'valid': 'IN'
                        }
                        return JsonResponse(response_data,safe=False)
                    else:
                        subtotal = cupon.precio*int(cantidad)
                        detalle_cupon = Carrito_Cupones(id_carrito=carrito,id_cupon=cupon,cantidad=cantidad,precio=subtotal)
                        detalle_cupon.save()
                        response_data={
                            'valid':'OK'
                        }
                        return JsonResponse(response_data,safe=False)
            except Detalle_Carrito.DoesNotExist:
                subtotal=cupon.precio*int(cantidad)
                detalle_cupon = Carrito_Cupones(id_carrito=carrito,id_cupon=cupon,cantidad=cantidad,precio=subtotal)
                detalle_cupon.save()
                response_data = {
                  'valid': 'OK'
                }
                return JsonResponse(response_data,safe=False)
        except Carrito.DoesNotExist:
            carrito_new=Carrito(id_cliente=cliente)
            carrito_new.save()
            subtotal=cupon.precio*int(cantidad)
            detalle_cupon_new=Carrito_Cupones(id_carrito=carrito_new,id_cupon=cupon,cantidad=cantidad,precio=subtotal)
            detalle_cupon_new.save()
            response_data = {
              'valid': 'OK'
            }
            return JsonResponse(response_data,safe=False)

    response_data = {
        'valid': 'NOT'
    }
    return JsonResponse(response_data,safe=False)

def lecturaCupon(nombre,oxfs):
    print(oxfs)
    for oxf in oxfs:
        print(oxf.id_cupon.nombre)
        if str(oxf.id_cupon.nombre) == nombre:
            return True
    return False

def lecturaTarjeta(id_tarjeta,oxfs):
    print(oxfs)
    for oxf in oxfs:
        if oxf.id_tarjeta.id_tarjeta == id_tarjeta:
            return True
    return False

def cambiarCantidadCupon(nombre,cantidad,oxfs):
    for oxf in oxfs:
        print(oxf.id_cupon.nombre)
        if str(oxf.id_cupon.nombre) == nombre:
            print("Esta es la cantidad",cantidad)
            oxf.cantidad=oxf.cantidad+int(cantidad)
            oxf.precio=oxf.id_cupon.precio*oxf.cantidad
            oxf.save()
            return True
    return False

def detallePedido(pedido,carrito,detalle_producto,detalle_oferta,detalle_combo,detalle_cupon,detalle_tarjeta_monto,detalle_tarjeta_producto):
    total_oferta = detalle_oferta.count()
    total_producto = detalle_producto.count()
    total_cupon = detalle_cupon.count()
    total_tarjeta_monto = detalle_tarjeta_monto.count()
    total_tarjeta_producto = detalle_tarjeta_producto.count()
    total_combo = detalle_combo.count()
    if total_producto > 0:
        for producto in detalle_producto:
            pro=Producto.objects.filter(id_producto=producto.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
            if(pro.suma-producto.cantidad>=0):
                productoxpedido=Producto_Pedido(cantidad=producto.cantidad,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                productoxpedido.save()
                producto.delete()
            elif(pro.suma>0):
                productoxpedido=Producto_Pedido(cantidad=pro.suma,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                productoxpedido.save()
                producto.delete()
    if total_oferta > 0:
        for oferta in detalle_oferta:
            ofer=oferta.id_oferta
            if(ofer.cantidad-oferta.cantidad>=0):
                ofer.cantidad=ofer.cantidad-oferta.cantidad
                ofer.save()
                ofertaxpedido=Oferta_Pedido(cantidad=oferta.cantidad,precio=oferta.precio,oferta=oferta.id_oferta,pedido=pedido)
                ofertaxpedido.save()
                oferta.delete()
            elif(ofer.cantidad>0):
                ofer.cantidad=0
                ofer.save()
                ofertaxpedido=Oferta_Pedido(cantidad=ofer.cantidad,precio=oferta.precio,oferta=oferta.id_oferta,pedido=pedido)
                ofertaxpedido.save()
                oferta.delete()

    if total_cupon > 0:
        for cupons in detalle_cupon:
            cu=cupons.id_cupon
            if(cu.cantidad-cupons.cantidad>=0):
                cu.cantidad=cu.cantidad-cupons.cantidad
                cu.save()
                cuponxpedido=Cupon_Pedido(cantidad=cupons.cantidad,precio=cupons.precio,cupon=cupons.id_cupon,pedido=pedido)
                codigo=Codigo.objects.filter(id_cupon=cu)
                if codigo:
                    code=Codigo.objects.get(id_cupon=cu)
                    codigoXcliente=Codigo_Cliente.objects.get(id_codigo=code, id_cliente=pedido.cliente_id)
                    codigoXcliente.estado='I'
                    codigoXcliente.save()
                cuponxpedido.save()
                cupons.delete()
            elif(cu.cantidad>0):
                cu.cantidad=0
                cu.save()
                cuponxpedido=Cupon_Pedido(cantidad=cu.cantidad,precio=cupons.precio,cupon=cupons.id_cupon,pedido=pedido)
                cuponxpedido.save()
                cupons.delete()

    if total_tarjeta_monto > 0:
        for tarjet in detalle_tarjeta_monto:
            #tarjetaxpedido=Tarjeta_Monto_Pedido(precio=tarjet.id_tarjeta.monto,tarjeta=tarjet.id_tarjeta,pedido=pedido)
            #tarjetaxpedido.save()
            tarXcliente=Tarjeta_Monto_Cliente.objects.get(id_tarjeta=tarjet.id_tarjeta.id_tarjeta, id_cliente=pedido.cliente_id)
            tarXcliente.estado='I'
            tarXcliente.save()
            tarjet.delete()

    if total_tarjeta_producto > 0:
        for tarjet in detalle_tarjeta_producto:
            detalle_tarjeta_producto_producto=Tarjeta_Producto_Producto.objects.filter(id_tarjeta=tarjet.id_tarjeta)
            for tarproducto in detalle_tarjeta_producto_producto:
                pro=Producto.objects.filter(id_producto=tarproducto.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
                if(pro.suma-producto.cantidad>=0):
                    productoxpedido=Producto_Pedido(cantidad=producto.cantidad,precio=producto.precio,producto=tarproducto.id_producto,pedido=pedido)
                    productoxpedido.save()
                    tarproducto.delete()
                elif(pro.suma>0):
                    productoxpedido=Producto_Pedido(cantidad=pro.suma,precio=producto.precio,producto=tarproducto.id_producto,pedido=pedido)
                    productoxpedido.save()
                    tarproducto.delete()
            #tarjetaxpedido=Tarjeta_Monto_Pedido(precio=tarjet.id_tarjeta.monto,tarjeta=tarjet.id_tarjeta,pedido=pedido)
            #tarjetaxpedido.save()
            tarXcliente=Tarjeta_Producto_Cliente.objects.get(id_tarjeta=tarjet.id_tarjeta.id_tarjeta, id_cliente=pedido.cliente_id)
            tarXcliente.estado='I'
            tarXcliente.save()
            tarjet.delete()

    if total_combo > 0:
        for combo in detalle_combo:
            com=combo.id_combo
            if(com.cantidad-combo.cantidad>=0):
                com.cantidad=com.cantidad-combo.cantidad
                com.save()
                comboxpedido=Combo_Pedido(cantidad=combo.cantidad,precio=combo.precio,combo=combo.id_combo,pedido=pedido)
                comboxpedido.save()
                combo.delete()
            elif(cu.cantidad>0):
                com.cantidad=0
                com.save()
                comboxpedido=Combo_Pedido(cantidad=combo.cantidad,precio=combo.precio,combo=combo.id_combo,pedido=pedido)
                comboxpedido.save()
                combo.delete()

def detallePedido2(pedido,carrito,detalle_producto,detalle_oferta,detalle_combo,detalle_cupon,detalle_tarjeta_monto,detalle_tarjeta_producto):
    total_oferta = detalle_oferta.count()
    total_producto = detalle_producto.count()
    total_cupon = detalle_cupon.count()
    total_tarjeta_monto = detalle_tarjeta_monto.count()
    total_tarjeta_producto = detalle_tarjeta_producto.count()
    total_combo = detalle_combo.count()
    if total_producto > 0:
        for producto in detalle_producto:
            pro=Producto.objects.filter(id_producto=producto.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
            productoop=Producto.objects.get(id_producto=producto.id_producto.id_producto)
            pedido.puntos=pedido.puntos + (productoop.puntos * producto.cantidad)
            pedido.save()
            if(pro.suma-producto.cantidad>=0):
                productoxpedido=Producto_Pedido(cantidad=producto.cantidad,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                productoxpedido.save()
                producto.delete()
            elif(pro.suma>0):
                productoxpedido=Producto_Pedido(cantidad=pro.suma,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                productoxpedido.save()
                producto.delete()
    if total_oferta > 0:
        for oferta in detalle_oferta:
            ofer=oferta.id_oferta
            if(ofer.cantidad-oferta.cantidad>=0):
                ofer.cantidad=ofer.cantidad-oferta.cantidad
                ofer.save()
                ofertaxpedido=Oferta_Pedido(cantidad=oferta.cantidad,precio=oferta.precio,oferta=oferta.id_oferta,pedido=pedido)
                ofertaxpedido.save()
                oferta.delete()
            elif(ofer.cantidad>0):
                ofer.cantidad=0
                ofer.save()
                ofertaxpedido=Oferta_Pedido(cantidad=ofer.cantidad,precio=oferta.precio,oferta=oferta.id_oferta,pedido=pedido)
                ofertaxpedido.save()
                oferta.delete()
    if total_cupon > 0:
        for cupons in detalle_cupon:
            cu=cupons.id_cupon
            if(cu.cantidad-cupons.cantidad>=0):
                cu.cantidad=cu.cantidad-cupons.cantidad
                cu.save()
                cuponxpedido=Cupon_Pedido(cantidad=cupons.cantidad,precio=cupons.precio,cupon=cupons.id_cupon,pedido=pedido)
                codigo=Codigo.objects.filter(id_cupon=cu)
                if codigo:
                    code=Codigo.objects.get(id_cupon=cu)
                    codigoXcliente=Codigo_Cliente.objects.get(id_codigo=code, id_cliente=pedido.cliente_id)
                    codigoXcliente.estado='I'
                    codigoXcliente.save()
                cuponxpedido.save()
                cupons.delete()
            elif(cu.cantidad>0):
                cu.cantidad=0
                cu.save()
                cuponxpedido=Cupon_Pedido(cantidad=cu.cantidad,precio=cupons.precio,cupon=cupons.id_cupon,pedido=pedido)
                cuponxpedido.save()
                cupons.delete()
    if total_tarjeta_monto > 0:
        for tarjet in detalle_tarjeta_monto:
            tarXcliente=Tarjeta_Monto_Cliente.objects.get(id_tarjeta=tarjet.id_tarjeta.id_tarjeta, id_cliente=pedido.cliente_id)
            tarXcliente.estado='I'
            tarXcliente.save()
            tarjetaxpedido=Tarjeta_Monto.objects.get(id_tarjeta=tarjet.id_tarjeta.id_tarjeta)
            pedidoDeTarjeta= Pedido.objects.get(id_pedido=tarjetaxpedido.id_pedido.id_pedido)
            pedidoDeTarjeta.estado='Reclamado'
            pedidoDeTarjeta.save()
            tarjet.delete()
    if total_tarjeta_producto > 0:
        for tarjet in detalle_tarjeta_producto:
            detalle_tarjeta_producto_producto=Tarjeta_Producto_Producto.objects.filter(id_tarjeta=tarjet.id_tarjeta)
            for tarproducto in detalle_tarjeta_producto_producto:
                pro=Producto.objects.filter(id_producto=tarproducto.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
                if(pro.suma-producto.cantidad>=0):
                    productoxpedido=Producto_Pedido(cantidad=producto.cantidad,precio=producto.precio,producto=tarproducto.id_producto,pedido=pedido)
                    productoxpedido.save()
                    tarproducto.delete()
                elif(pro.suma>0):
                    productoxpedido=Producto_Pedido(cantidad=pro.suma,precio=producto.precio,producto=tarproducto.id_producto,pedido=pedido)
                    productoxpedido.save()
                    tarproducto.delete()
            tarXcliente=Tarjeta_Producto_Cliente.objects.get(id_tarjeta=tarjet.id_tarjeta.id_tarjeta, id_cliente=pedido.cliente_id)
            tarXcliente.estado='I'
            tarXcliente.save()

            tarjetaxpedido=Tarjeta_Producto.objects.get(id_tarjeta=tarjet.id_tarjeta.id_tarjeta)
            pedidoDeTarjeta= Pedido.objects.get(id_pedido=tarjetaxpedido.id_pedido.id_pedido)
            pedidoDeTarjeta.estado='Reclamado'
            pedidoDeTarjeta.save()
            tarjet.delete()
    if total_combo > 0:
        for combo in detalle_combo:
            com=combo.id_combo
            if(com.cantidad-combo.cantidad>=0):
                com.cantidad=com.cantidad-combo.cantidad
                com.save()
                comboxpedido=Combo_Pedido(cantidad=combo.cantidad,precio=combo.precio,combo=combo.id_combo,pedido=pedido)
                comboxpedido.save()
                combo.delete()
            elif(cu.cantidad>0):
                com.cantidad=0
                com.save()
                comboxpedido=Combo_Pedido(cantidad=combo.cantidad,precio=combo.precio,combo=combo.id_combo,pedido=pedido)
                comboxpedido.save()
                combo.delete()

@csrf_exempt
def quitar_usuario(request):
    print(request)
    if request.method == "POST":
        res = json.loads(request.body)
        correo = res["correo"]


        usuario=Usuario.objects.get(correo=correo)
        cliente=Cliente.objects.get(usuario=usuario)

        carrito=Carrito.objects.get(id_cliente=cliente)

        detalle_oferta= Carrito_Oferta.objects.filter(id_carrito=carrito.id_carrito)
        detalle_carrito = Detalle_Carrito.objects.filter(id_carrito=carrito)
        detalle_cupon = Carrito_Cupones.objects.filter(id_carrito=carrito)

        total_oferta = detalle_oferta.count()
        total_producto = detalle_carrito.count()
        total_cupon = detalle_cupon.count()

        if total_producto !=0:
            for producto in detalle_carrito:
                producto.delete()

        if total_oferta != 0:
            for oferta in detalle_oferta:
                oferta.delete()

        if total_cupon != 0:
            for cupons in detalle_cupon:
                cupons.delete()

        try:
            carrito.delete()
            cliente.delete()
            usuario.delete()
        except:
            response_data = {'valid': 'NO',}
            return JsonResponse(response_data,safe=False)
        else:
            response_data = {'valid': 'OK',}
            return JsonResponse(response_data,safe=False)

    response_data = {'valid': 'NO',}
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def getCodigos(request):
    if request.method == "POST":
        response = json.loads(request.body)
        code = response["codigo"]
        id_cliente = response["id_cliente"]
        codigos= Codigo.objects.filter(codigo=str(code)).exclude(estado='I')
        if codigos:
            codigo = Codigo.objects.get(codigo=str(code))
            cliente = Cliente.objects.get(id_cliente=id_cliente)
            codigosclientes= Codigo_Cliente.objects.filter(id_codigo=codigo, id_cliente=cliente)
            if codigosclientes:
                response_data = {'valid': 'talvez',}
                return JsonResponse(response_data,safe=False)
            codigoXusuario=Codigo_Cliente(id_codigo=codigo,id_cliente=cliente)
            codigoXusuario.save()
            response_data = {'valid': 'OK',}
            return JsonResponse(response_data,safe=False)
        response_data = {'valid': 'NO', 'valor':str(code)}
        return JsonResponse(response_data,safe=False)
    codigos= Codigo.objects.all().exclude(estado='I')
    res=[]
    for codigo in codigos:
        id=codigo.codigo.replace(" ","_")+"_"+str(codigo.id_codigo)

        diccionario={"id":codigo.id_codigo,"codigo":codigo.codigo,"descripcion":codigo.descripcion,
        "tipo":codigo.tipo,"fecha_inicio":codigo.fecha_inicio,"fecha_fin":codigo.fecha_fin}
        res.append(diccionario)
    return JsonResponse(res,safe=False)

@csrf_exempt
def getCodigosString(request,codigostr):
        codigos= Codigo.objects.filter(codigo=codigostr).exclude(estado='I')
        if codigos:
            response_data = {'valid': 'OK',}
            return JsonResponse(response_data,safe=False)
        response_data = {'valid': 'NO',}
        return JsonResponse(response_data,safe=False)

@csrf_exempt
def getTarjetasRegalo(request, id):
    if request.method == 'GET':
        print("estoy dentro del getTarjetasRegalo")
        res = []
        tarjetas = Tarjeta_Monto_Cliente.objects.filter(id_cliente = id).exclude(estado="I")
        for tarjeta in tarjetas:
            diccionario = {"id":tarjeta.id_tarjeta.id_tarjeta,"emisor":tarjeta.id_tarjeta.id_cliente.nombre,"descripcion":tarjeta.id_tarjeta.descripcion,"monto":tarjeta.id_tarjeta.monto, "fecha":tarjeta.fecha}
            res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def getTarjetasRegaloP(request, id):
    if request.method == 'GET':
        print("estoy dentro del getTarjetasRegaloP")
        res = []
        tarjetas = Tarjeta_Producto_Cliente.objects.filter(id_cliente = id).exclude(estado="I")
        for tarjeta in tarjetas:
            tarjetaprod=Tarjeta_Producto.objects.get(id_tarjeta = tarjeta.id_tarjeta.id_tarjeta)
            productos=Tarjeta_Producto_Producto.objects.filter(id_tarjeta = tarjetaprod)
            listaprod=""
            for producto in productos:
                listaprod=listaprod+producto.id_producto.nombre+" x"+str(producto.cantidad)+" - "
            diccionario = {"id":tarjeta.id_tarjeta.id_tarjeta,"emisor":tarjeta.id_tarjeta.id_cliente.nombre,"descripcion":tarjeta.id_tarjeta.descripcion,"listaprod":listaprod, "fecha":tarjeta.fecha}
            res.append(diccionario)
        return JsonResponse(res,safe=False)
    return HttpResponse(status=400)

@csrf_exempt
def crearTarjetaRegaloMonto(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        total=response["total"]
        emisor=response["id_cliente"]
        receptor=response["receptor"]
        descripcion=response["descripcion"]

        clienteEmisor = Cliente.objects.get(id_cliente=int(emisor))
        clienteReceptor = Cliente.objects.get(usuario__correo=receptor)

        tarjetaMonto=Tarjeta_Monto(id_cliente=clienteEmisor, monto=float(total),descripcion=descripcion)
        tarjetaMonto.save()
        tarjetaMontoCliente=Tarjeta_Monto_Cliente(id_cliente=clienteReceptor, id_tarjeta=tarjetaMonto, fecha=timezone.now())
        tarjetaMontoCliente.save()
        response_data = {'valid': 'OK',}
        return JsonResponse(response_data,safe=False)
    response_data = {'valid': 'NO',}
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def crearTarjetaRegaloproducto(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        emisor=response["id_cliente"]
        receptor=response["receptor"]
        descripcion=response["descripcion"]
        carrito=response["carrito"]

        detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito)

        clienteEmisor = Cliente.objects.get(id_cliente=int(emisor))
        clienteReceptor = Cliente.objects.get(usuario__correo=receptor)
        tarjetaProducto=Tarjeta_Producto(id_cliente=clienteEmisor, descripcion=descripcion)
        tarjetaProducto.save()
        tarjetaProductoCliente=Tarjeta_Producto_Cliente(id_cliente=clienteReceptor, id_tarjeta=tarjetaProducto)
        tarjetaProductoCliente.save()

        for producto in detalle_producto:
            '''pro=Producto.objects.filter(id_producto=producto.id_producto.id_producto).annotate(suma=Sum('establecimiento_producto__stock_disponible')).first()
            if(pro.suma-producto.cantidad>=0):
                productoxpedido=Producto_Pedido(cantidad=producto.cantidad,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                productoxpedido.save()
                producto.delete()
            elif(pro.suma>0):
                productoxpedido=Producto_Pedido(cantidad=pro.suma,precio=producto.precio,producto=producto.id_producto,pedido=pedido)
                productoxpedido.save()
                producto.delete()'''
            tarjetaProductoProducto=Tarjeta_Producto_Producto(id_tarjeta=tarjetaProducto, id_producto=producto.id_producto, cantidad=producto.cantidad)
            tarjetaProductoProducto.save()
            producto.delete()

        response_data = {'valid': 'OK',}
        return JsonResponse(response_data,safe=False)
    response_data = {'valid': 'NO',}
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def addTarjetaRegaloMonto(request):
    if request.method == "POST":
        response = json.loads(request.body)
        tarjeta=Tarjeta_Monto.objects.get(id_tarjeta=response["id_tarjeta"])
        cantidad = int(response["cantidad"])
        mail = response["correo"]
        id_tarjeta = response["id_tarjeta"]
        cliente=Cliente.objects.select_related("usuario").filter(usuario__correo=mail).first()
        try:
            carrito=Carrito.objects.get(id_cliente=cliente)
            try:
                carritoDetalle = Carrito_Tarjeta_Monto.objects.filter(id_carrito=carrito)
                total = carritoDetalle.count()
                if total == 0:
                    subtotal=tarjeta.monto*int(cantidad)
                    detalle_tarjeta = Carrito_Tarjeta_Monto(id_carrito=carrito,id_tarjeta=tarjeta,precio=-subtotal)
                    detalle_tarjeta.save()
                    response_data = {
                        'valid':'OK'
                    }
                    return JsonResponse(response_data,safe=False)
                else:
                    if lecturaTarjeta(tarjeta.id_tarjeta,carritoDetalle) == True:
                        response_data = {
                                'valid': 'IN'
                        }
                        return JsonResponse(response_data,safe=False)
                    else:
                        subtotal = tarjeta.monto*int(cantidad)
                        detalle_tarjeta = Carrito_Tarjeta_Monto(id_carrito=carrito,id_tarjeta=tarjeta,precio=-subtotal)
                        detalle_tarjeta.save()
                        response_data={
                            'valid':'OK'
                        }
                        return JsonResponse(response_data,safe=False)
            except Detalle_Carrito.DoesNotExist:
                subtotal=tarjeta.monto*int(cantidad)
                detalle_tarjeta = Carrito_Tarjeta_Monto(id_carrito=carrito,id_tarjeta=tarjeta,precios=-subtotal)
                detalle_tarjeta.save()
                response_data = {
                  'valid': 'OK'
                }
                return JsonResponse(response_data,safe=False)
        except Carrito.DoesNotExist:
            carrito_new=Carrito(id_cliente=cliente)
            carrito_new.save()
            subtotal=tarjeta.monto*int(cantidad)
            detalle_tarjeta_new=Carrito_Tarjeta_Monto(id_carrito=carrito_new,id_tarjeta=tarjeta,precio=-subtotal)
            detalle_tarjeta_new.save()
            response_data = {
              'valid': 'OK'
            }
            return JsonResponse(response_data,safe=False)

    response_data = {
        'valid': 'NOT'
    }
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def addTarjetaRegaloproducto(request):
    if request.method == "POST":
        response = json.loads(request.body)
        tarjeta=Tarjeta_Producto.objects.get(id_tarjeta=response["id_tarjeta"])
        cantidad = int(response["cantidad"])
        mail = response["correo"]
        id_tarjeta = response["id_tarjeta"]
        cliente=Cliente.objects.select_related("usuario").filter(usuario__correo=mail).first()
        try:
            carrito=Carrito.objects.get(id_cliente=cliente)
            try:
                carritoDetalle = Carrito_Tarjeta_Producto.objects.filter(id_carrito=carrito)
                total = carritoDetalle.count()
                if total == 0:
                    detalle_tarjeta = Carrito_Tarjeta_Producto(id_carrito=carrito,id_tarjeta=tarjeta)
                    detalle_tarjeta.save()
                    response_data = {
                        'valid':'OK'
                    }
                    return JsonResponse(response_data,safe=False)
                else:
                    if lecturaTarjeta(tarjeta.id_tarjeta,carritoDetalle) == True:
                        response_data = {
                                'valid': 'IN'
                        }
                        return JsonResponse(response_data,safe=False)
                    else:
                        detalle_tarjeta = Carrito_Tarjeta_Producto(id_carrito=carrito,id_tarjeta=tarjeta)
                        detalle_tarjeta.save()
                        response_data={
                            'valid':'OK'
                        }
                        return JsonResponse(response_data,safe=False)
            except Detalle_Carrito.DoesNotExist:
                detalle_tarjeta = Carrito_Tarjeta_Producto(id_carrito=carrito,id_tarjeta=tarjeta)
                detalle_tarjeta.save()
                response_data = {
                  'valid': 'OK'
                }
                return JsonResponse(response_data,safe=False)
        except Carrito.DoesNotExist:
            carrito_new=Carrito(id_cliente=cliente)
            carrito_new.save()
            detalle_tarjeta_new=Carrito_Tarjeta_Producto(id_carrito=carrito_new,id_tarjeta=tarjeta)
            detalle_tarjeta_new.save()
            response_data = {
              'valid': 'OK'
            }
            return JsonResponse(response_data,safe=False)

    response_data = {
        'valid': 'NOT'
    }
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def eliminarCarrito(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        carT=response["carrito"]
        try:
            carrito=Carrito.objects.filter(id_carrito=carT).first()
            detalle_producto=Detalle_Carrito.objects.filter(id_carrito=carrito)
            detalle_oferta=Carrito_Oferta.objects.filter(id_carrito=carrito)
            detalle_combo=Carrito_Combo.objects.filter(id_carrito=carrito)
            detalle_cupon=Carrito_Cupones.objects.filter(id_carrito=carrito)
            detalle_tarjeta_monto=Carrito_Tarjeta_Monto.objects.filter(id_carrito=carrito)
            eliminarCarrito2(carrito,detalle_producto,detalle_oferta,detalle_combo,detalle_cupon,detalle_tarjeta_monto)
            res = {
            'valid': 'ok',
            'LAlIFE': carrito.id_carrito
            }

            return JsonResponse(res,safe=False)
        except Exception as e:
            print("type error: " + str(e))
            res = {
            'valid': 'not',
            'LAlIFE': a
            }
            return JsonResponse(res,safe=False)

def eliminarCarrito2(carrito,detalle_producto,detalle_oferta,detalle_combo,detalle_cupon,detalle_tarjeta_monto):
    total_oferta = detalle_oferta.count()
    total_producto = detalle_producto.count()
    total_cupon = detalle_cupon.count()
    total_tarjeta_monto = detalle_tarjeta_monto.count()
    total_combo = detalle_combo.count()
    if total_producto > 0:
        for producto in detalle_producto:
            producto.delete()
    if total_oferta > 0:
        for oferta in detalle_oferta:
            oferta.delete()
    if total_cupon > 0:
        for cupons in detalle_cupon:
            cupons.delete()
    if total_tarjeta_monto > 0:
        for tarjet in detalle_tarjeta_monto:
            tarjet.delete()
    if total_combo > 0:
        for combo in detalle_combo:
            combo.delete()

@csrf_exempt
def addToken(request):
    try:
        response = json.loads(request.body)
        id_usuario=response["id"]
        token  = response["token"]
        usuario=Usuario.objects.get(id_usuario=id_usuario)
        usuario.token=token
        usuario.save()
        response_data = {
            'valid':'Ok'
            }
        return JsonResponse(response_data,safe=False)
    except:
        response_data = {
            'valid':'NO'
            }
        return JsonResponse(response_data,safe=False)


@csrf_exempt
def getPublicidadSuperior(request):
    if request.method == 'GET':
        res = []
        publicidades = Publicidad.objects.filter(tipo = 'Superior')
        publicidades = publicidades.filter(fecha_inicio__lte=datetime.today())
        publicidades = publicidades.filter(fecha_fin__gte=datetime.today())
        for publicidad in publicidades:
            dic = {"nombre": publicidad.nombre, "img": publicidad.photo_url, "link": publicidad.url}
            res.append(dic)

        return JsonResponse(res, safe = False)
    return HttpResponse(status = 400)


@csrf_exempt
def getPublicidadInferior(request):
    if request.method == 'GET':
        res = []
        publicidades = Publicidad.objects.filter(tipo = 'Inferior')
        publicidades = publicidades.filter(fecha_inicio__lte=datetime.today())
        publicidades = publicidades.filter(fecha_fin__gte=datetime.today())
        for publicidad in publicidades:
            dic = {"nombre": publicidad.nombre, "img": publicidad.photo_url, "link": publicidad.url}
            res.append(dic)

        return JsonResponse(res, safe = False)
    return HttpResponse(status = 400)


@csrf_exempt
def getPremios(request):
    if request.method == 'GET':
        res = []
        premios = Premios.objects.filter(fecha_inicio__lte=datetime.today())
        premios = premios.filter(fecha_fin__gte=datetime.today())
        for premio in premios:
            dic = {"nombre": premio.nombre, "img": premio.photo_url, "descripcion": premio.descripcion, "cantidad": premio.cantidad, "puntos": premio.puntos, "fecha_fin": premio.fecha_fin}
            res.append(dic)

        return JsonResponse(res, safe = False)
    return HttpResponse(status = 400)

@csrf_exempt
def getPuntosPersonales(request, id):
    if request.method == 'GET':
        cliente = Cliente.objects.get(id_cliente = id)
        puntos = Puntos.objects.get(id_puntos = 1)
        dic = {"puntosATarjeta":puntos.puntosATarjeta,"tarjetaAPuntos": puntos.tarjetaAPuntos , "puntos":cliente.puntos}
        return JsonResponse(dic, safe = False)
    return HttpResponse(status = 400)

@csrf_exempt
def getPremiosPersonales(request, id):
    if request.method == 'GET':
        res = []
        premios = Premios_Cliente.objects.filter(id_cliente = id)
        for premiop in premios:
            if not premiop.fecha_entrega:
                dic = {"nombre": premiop.id_premio.nombre, "img": premiop.id_premio.photo_url, "descripcion": premiop.id_premio.descripcion, "puntos": premiop.id_premio.puntos, "fecha_canje": premiop.fecha_canje, "fecha_entrega": premiop.fecha_entrega}
                res.append(dic)

        return JsonResponse(res, safe = False)

    return HttpResponse(status = 400)


@csrf_exempt
def getPremiosUtlizados(request, id):
    if request.method == 'GET':
        res = []
        premios = Premios_Cliente.objects.filter(id_cliente = id)
        for premiop in premios:
            if premiop.fecha_entrega:
                dic = {"nombre": premiop.id_premio.nombre, "img": premiop.id_premio.photo_url, "descripcion": premiop.id_premio.descripcion, "puntos": premiop.id_premio.puntos, "fecha_canje": premiop.fecha_canje, "fecha_entrega": premiop.fecha_entrega}
                res.append(dic)

        return JsonResponse(res, safe = False)

    JsonResponse(response_data,safe=False)


@csrf_exempt
def recalmarPremio(request):
    response_data = {'valid':'NO'}
    if request.method == 'POST':
        response = json.loads(request.body)
        clienteId=response["id"]
        nombrePremio=response["premio"]
        cliente = Cliente.objects.get(id_cliente = clienteId)
        premio = Premios.objects.get(nombre = nombrePremio)
        if cliente.puntos >= premio.puntos:
            if premio.cantidad != 0:
                premCLi=Premios_Cliente.objects.filter(id_premio=premio, id_cliente=cliente, estado='Recibido').first()
                if premCLi != None:
                    response_data = {'valid':'existe'}
                    return JsonResponse(response_data,safe=False)
                premio.cantidad = premio.cantidad - 1
                premio.save()
                cliente.puntos = cliente.puntos - premio.puntos
                cliente.save()
                premioCliente=Premios_Cliente(fecha_canje=datetime.now().replace(hour=0,minute=0,second=0),id_premio=premio,id_cliente=cliente)
                premioCliente.save()
                response_data = {'valid':'OK', 'cant':premio.cantidad, 'pnts': cliente.puntos}
            else:
                response_data = {'valid':'cantidad', 'cant':premio.cantidad, 'pnts': cliente.puntos}
                return JsonResponse(response_data,safe=False)
        else:
            response_data = {'valid':'puntos', 'cant':premio.cantidad, 'pnts': cliente.puntos}
            return JsonResponse(response_data,safe=False)

    return JsonResponse(response_data,safe=False)

@csrf_exempt
def restarPuntos(request):
    response_data = {'valid':'NO'}
    if request.method == 'POST':
        response = json.loads(request.body)
        clienteId=response["id"]
        puntos=response["puntos"]
        cliente = Cliente.objects.get(id_cliente = clienteId)
        cliente.puntos = puntos
        cliente.save()
        response_data = {'valid':'OK'}
        return JsonResponse(response_data,safe=False)
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def revisarBan(request, id):
    if request.method == 'GET':
        cliente = Cliente.objects.get(id_cliente = id)
        if cliente.ban == 0:
            response_data = {'valid':'OK'}
        else:
            response_data = {'valid':'NO'}
        return JsonResponse(response_data,safe=False)
    JsonResponse(response_data,safe=False)

@csrf_exempt
def modContra(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        id=response["id"]
        usuario=Usuario.objects.select_related().filter(id_usuario=id).first()
        vContra = response["vContra"]
        nContra = response["nContra"]
        try:
            if usuario.contrasena == vContra:
                usuario.contrasena = nContra
                usuario.save()
                response_data = {'valid':'OK'}

            else:
                response_data = {'valid':'contra'}

            return JsonResponse(response_data,safe=False)
        except:
            response_data = {'valid':'NO'}
            return JsonResponse(response_data,safe=False)

    return HttpResponse(status=400)


#@login_required(login_url='/login/')
@csrf_exempt
def verificar_y_crear_canal(request,cliente,admin):


    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        canal_ = body['canal']
        esAdmin_=body['esAdmin']
        check_leido_=body['check_leido']
        texto_=body['texto']
        usuario_admin_=body['usuario_admin']
        usuario_cliente_=body['usuario_cliente']


        print(body)

        canal_c=Canal.objects.get(id=canal_)
        usuario_cliente,usuario_admin=None,None

        #if(esAdmin_==True):
        usuario_admin=Empleado.objects.get(cedula=usuario_admin_)
        #else:
        usuario_cliente=Cliente.objects.get(usuario__cedula=usuario_cliente_)

        nuevo_mensaje=CanalMensaje(
            canal=canal_c,
            usuario_cliente=usuario_cliente,
            usuario_admin=usuario_admin,
            texto=texto_,
            check_leido=check_leido_,
            esAdmin=esAdmin_

        )
        nuevo_mensaje.save()
        return JsonResponse(body)

    elif request.method == 'GET':


        canal,_= Canal.objects.obtener_o_crear_canal_ms(cliente,admin)
        if canal == None:
            return JsonResponse({'mensaje':'Canal no creado','status':'Error'})

        if admin == cliente:
            return JsonResponse({"mensaje":"Canal consigo mismo no puede crearse"})


        perfil_usuario_actual={}
        perfil_admin={}

        mensajes=CanalMensaje.obtener_data_mensaje_usuarios(canal.id)

        return JsonResponse({
            'canal':canal.id,
            'receptor':admin,
            'usuario_logeado':cliente,
            'mensajes':mensajes

            })

def actualizar_sms_leido(request,id_mensaje):
    if request.method == 'GET':
        qs = CanalMensaje.verificar_leido(id_mensaje)
        print(qs)
        print("===============")
        return JsonResponse({
            'data':qs,
            },safe=False)

def obtener_data_empleado_admin(request):
    if request.method == 'GET':
        qs=Empleado.objects.all().values()
        if(qs):
            return JsonResponse({'data':list(qs)})
    pass