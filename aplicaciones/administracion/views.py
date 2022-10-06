from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from push_notifications.webpush import WebPushError
from push_notifications.models import WebPushDevice
from push_notifications.models import GCMDevice
from push_notifications.gcm import send_message
from django.shortcuts import redirect
from django.db.models import Count, Sum, Avg
from django.contrib.auth.models import User
from datetime import datetime
import requests
import pytz
import json
import re
from django.core import serializers
from .models import *
# Create your views here.
#sesion = False
def principal(request):
    if request.method == 'GET':
        try:
            correo = request.session['correo']
            contra = request.session['contrasena']
            usuario = Empleado.objects.filter(usuario__username=correo).first()
            print("Usuario",usuario)
            if usuario.rol == "superadmin":
                print("vamos a cargar al superadmin")
                #sesion = not sesion
                return redirect("/principalSuperAdmin")
            elif usuario.rol == "administrador":
                print("vamos a cargar al admin")
                #sesion = not sesion
                return redirect("/principalAdmin")
        except:
            return redirect("/login")
    return render(request, 'Login/login.html')

@csrf_exempt
def inicio(request):
    if request.method == "POST":
        print("Request",request)
        email = request.POST.get('correo', None)
        contra = request.POST.get('contrasena', None)
        user = authenticate(username=email, password=contra)
        print("User",user)
        if user is not None:
            login(request, user)
            request.session['correo'] = email
            request.session['contrasena'] = contra
            usuario = Empleado.objects.filter(usuario__username=email).first()
            print("Usuario",usuario)
            next=request.GET.get("next")
            if next is not None:
                return redirect(next)
            if usuario.rol == "superadmin":
                print("vamos a cargar al superadmin")
                #sesion = not sesion
                return redirect("/principalSuperAdmin")
            elif usuario.rol == "administrador":
                print("vamos a cargar al admin")
                #sesion = not sesion
                return redirect("/principalAdmin")
        else:
            return redirect("/login")
    return render(request, 'Login/login.html')

@login_required(login_url='/login/')
def register_wp_notifications(request):
    result= False
    if not WebPushDevice.objects.filter(registration_id=request.GET.get('registration_id')).exists():
        WebPushDevice.objects.create(
            registration_id=request.GET.get('registration_id'),
            p256dh=request.GET.get('p256dh'),
            auth=request.GET.get('auth'),
            browser=request.GET.get('browser'),
        )
        result= True
    data = {
        'result': result
    }
    return JsonResponse(data)

def cerrar(request):
    try:
        logout(request)
        del request.session['correo']
        del request.session['contrasena']
        return redirect("/login")
    except:
        print("Error")
        return redirect("/login")

@login_required(login_url='/login/')
def principalSuperAdmin(request):
	return render(request,'Principal/SuperAdmin_Principal.html')

@login_required(login_url='/login/')
def principalAdmin(request):
	return render(request,'Principal/Admin_Principal.html')

@login_required(login_url='/login/')
def empresas(request):
	return render(request,'Empresa/index.html')

@login_required(login_url='/login/')
def tc(request):
    autorizacion="SDFGTBHR"
    transaccion=TransaccionPedido.objects.exclude(pedido=None).first()
    html = render_to_string("Correos/pagoTarjeta.html",{"data":transaccion, "autorizacion":autorizacion}).strip()
    msg = EmailMultiAlternatives('Pedido pagado', html, 'cabutosoftware1@gmail.com', ['sarahi199819@hotmail.com'])
    msg.content_subtype = 'html'  # set the primary content to be text/html
    msg.mixed_subtype = 'related'
    try:
        msg.send()
        print("type error: ")
    except Exception as e:
        print("Error al enviar correo")
        print("type error: " + str(e))
    return render(request,"Correos/pagoTarjeta.html",{"data":transaccion, "autorizacion":autorizacion})

@login_required(login_url='/login/')
def getEmpresas(request):
	if request.method=='GET':
		res=[]

		empresas=Empresa.objects.all()
		for emp in empresas:
			dicc={"id":emp.id_empresa,"nombre":emp.nombre,"descripcion":emp.descripcion,"razon_social":emp.razon_social,"ruc_cedula":emp.ruc_cedula}
			res.append(dicc)
		return JsonResponse(res,safe=False)
	return HttpResponse(status=400)

@login_required(login_url='/login/')
def admin_rol(request):
	paquete = []
	return render(request, "roles/admin_rol.html", paquete)

@login_required(login_url='/login/')
def producto_page(request):
    data_productsxestab = Establecimiento_Producto.objects.select_related("id_producto")
    data_productsxestab =data_productsxestab.order_by("id_producto__estado","-id_producto")
    data_category = Categoria.objects.all()
    if request.method == 'GET':
        busqueda=request.GET.get("busqueda")
        if busqueda!=None:
            data_productsxestab=data_productsxestab.filter(id_producto__nombre__icontains=busqueda)
        print(str(data_productsxestab.query))
        page = request.GET.get('page', 1)
        paginator = Paginator(data_productsxestab, 15)
        try:
            productosxestablecimiento = paginator.page(page)
        except PageNotAnInteger:
            productosxestablecimiento = paginator.page(1)
        except EmptyPage:
            productosxestablecimiento = paginator.page(paginator.num_pages)
        return render(request, "Productos/productos.html", {"datos": productosxestablecimiento, "data": data_category,"buscar":busqueda})
    elif request.method == 'POST':
        agregar_producto(request)
        return redirect("/productos")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def agregar_producto(request):
    data_establecimeinto = Establecimiento.objects.get(pk=1)
    res = []
    if request.method == 'POST':
        name = request.POST.get('nombre', None)
        description = request.POST.get('descripcion', None)
        price = request.POST.get('precio', None)
        imagen = request.FILES.get('image', None)
        category = request.POST.get('id_categoria', None)
        print(category)
        cantidad = request.POST.get('stock_disponible', None)
        for producto in Producto.objects.filter():
            n = producto.nombre
            if name == n:
                return render(request, "Productos/productos.html")
        categoria = Categoria.objects.get(nombre=category)
        data = Producto(nombre=name, descripcion=description, precio=price, image=imagen, id_categoria=categoria)
        data.save()
        data_estabxprod = Establecimiento_Producto(id_producto=data, stock_disponible=cantidad,
                                                   id_establecimiento=data_establecimeinto, stock_despacho=100)

        data_estabxprod.save()

@login_required(login_url='/login/')
@csrf_exempt
def editar_producto(request,id_producto):
    if request.method == 'GET':
        data_productsxestab = Establecimiento_Producto.objects.get(id_producto=id_producto)
        data_category = Categoria.objects.all()
        print(data_productsxestab)
        return render(request, "Productos/editar_producto.html", {"datos_mostrar": data_productsxestab, "data": data_category})
    elif request.method == 'POST':
        update_producto(request,id_producto)
        page = request.GET.get('page', 1)
        return redirect("/productos/?page="+page)
    return HttpResponse(status=400)


@login_required(login_url='/login/')
@csrf_exempt
def update_producto(request,id_producto):
    if request.method == 'POST':
        data_productsxestab = Establecimiento_Producto.objects.get(id_producto=id_producto)
        data_producto=Producto.objects.get(id_producto=id_producto)
        nombre = request.POST.get('nombre1', None)
        data_producto.nombre = request.POST.get('nombre1', None)
        data_producto.descripcion = request.POST.get('descripcion1', None)
        data_producto.precio = request.POST.get('precio1', None)
        category = request.POST.get('id_categoria1', None)
        categoria = Categoria.objects.get(id_categoria=category)
        if request.FILES.get('image1', None) != None:
            data_producto.image.delete()
            data_producto.image = request.FILES.get('image1', None)
        data_producto.id_categoria = categoria
        data_productsxestab.stock_disponible = request.POST.get('stock_disponible1', None)
        data_producto.save()
        data_productsxestab.save()


@login_required(login_url='/login/')
def eliminar_producto(request,id_producto):
    try:
        data_producto=Producto.objects.get(id_producto=id_producto)
        print(data_producto)
        if(data_producto.estado == "A"):
            data_producto.estado="I"
        else:
            data_producto.estado="A"
        data_producto.save()
        print(data_producto)
        response_data= 'El producto ha cambiado su estado'
        html = render_to_string("Avisos/correcto.html",{"data":response_data})
        return JsonResponse({'html': html, 'result': "ok"})
    except:
        response_data= 'Ha ocurrido un error, intente de nuevo'
        html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
        return JsonResponse({'html': html, 'result': "error"})

@login_required(login_url='/login/')
def usuario_page(request):
    if request.method=='GET':
	    data_empleados=Empleado.objects.select_related().filter()
	    valor = request.GET.get("busqueda")
	    if request.GET.get("busqueda")!=None:
	        data_empleados= data_empleados.filter(nombre__icontains=str(valor))|data_empleados.filter(apellido__icontains=str(valor))
	    data_empleados=data_empleados.order_by("-id_empleado")
	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_empleados, 5)
	    try:
	    	clientes = paginator.page(page)
	    except PageNotAnInteger:
	    	clientes = paginator.page(1)
	    except EmptyPage:
	    	clientes = paginator.page(paginator.num_pages)
	    return render(request, "Usuarios/usuarios.html",{"datos":clientes,"buscar":valor})
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def agregar_usuario(request):
    res=[]
    if request.method=='POST':
        try:
            nombre=request.POST.get('nombre',None)
            apellido = request.POST.get('apellido',None)
            cedula = request.POST.get('cedula',None)
            rol = request.POST.get('rol',None)
            telefono=request.POST.get('telefono',None)
            usuario=request.POST.get('usuario',None)
            correo=request.POST.get('correo',None)
            password=request.POST.get('password',None)
            u_cedula=Empleado.objects.select_related().filter(cedula=cedula).first()
            u_usuario=Empleado.objects.select_related().filter(usuario__username=usuario).first()
            u_correo=Empleado.objects.select_related().filter(usuario__email=correo).first()
            if u_cedula is not None or u_usuario is not None or u_correo is not None:
                response_data= 'Ya existe un usuario con estos datos, intenta de nuevo.'
                html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
                return JsonResponse({'html': html, 'result': "error"})
            user = User.objects.create_user(usuario, correo, password)
            user.save()
            empleado = Empleado(nombre=nombre,apellido = apellido,cedula=cedula,rol = rol, telefono= telefono, usuario=user)
            empleado.save()
            response_data= '!El usuario ha sido creado con éxito!'
            html = render_to_string("Avisos/correcto.html",{"data":response_data})
            return JsonResponse({'html': html, 'result': "ok"})
        except Exception as e:
            print(e)
            response_data= '!Ha ocurrido un error, intente de nuevo!'
            html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
            return JsonResponse({'html': html, 'result': "error"})
    if request.method=='GET':
    	return render(request, "Usuarios/add-usuario.html")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def editar_usuario(request,id_usuario):
    res=[]
    empleado=Empleado.objects.select_related().filter(id_empleado=id_usuario).first()
    if request.method=='POST':
        try:
            nombre=request.POST.get('nombre',None)
            apellido = request.POST.get('apellido',None)
            rol = request.POST.get('rol',None)
            telefono=request.POST.get('telefono',None)
            usuario=request.POST.get('usuario',None)
            correo=request.POST.get('correo',None)
            password=request.POST.get('password',None)
            empleado.nombre=nombre
            empleado.apellido = apellido
            empleado.rol = rol
            empleado.telefono= telefono
            empleado.save()
            return redirect("/usuarios")
        except:
            response_data= '!Ha ocurrido un error, intente de nuevo!'
            html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
            return JsonResponse({'html': html, 'result': "error"})
    if request.method=='GET':
    	return render(request, "Usuarios/edit-usuario.html",{"data":empleado})
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def pedido_page(request):
    if request.method=='GET':
        orden=request.GET.get("filtro")
        print(orden)
        desde=request.GET.get("from")
        hasta=request.GET.get("to")
        data_clientes=Pedido.objects.all().order_by("id_pedido")
        
        '''if request.GET.get("from")!=None and request.GET.get("to")!=None:
            data_clientes=data_clientes.filter(fecha__range=[desde, hasta]).order_by("id_pedido")
        elif request.GET.get("from")!=None:
            data_clientes= data_clientes.filter(fecha__gte=desde).order_by("id_pedido")
        elif request.GET.get("to")!=None:
            data_clientes= data_clientes.filter(fecha__lte=hasta).order_by("id_pedido")
        else:
            data_clientes= data_clientes.filter(fecha__gte = datetime.now().replace(hour=0,minute=0,second=0))'''

        if orden != None:
            if orden == 'fecha':
                data_clientes=data_clientes.order_by('fecha',"id_pedido")
            elif orden == 'total':
                data_clientes=data_clientes.order_by('-total',"id_pedido")
            elif orden == 'cliente':
                data_clientes=data_clientes.order_by('cliente__nombre','cliente__apellido',"id_pedido")
        todos=data_clientes.select_related()

        print('hola')
        print(Pedido.objects.all())
        print(todos)
        print(data_clientes)
        print('mundo')
        if(todos.count()!=0):
            total=round(todos.aggregate(suma=Sum('total'))["suma"],2)
        else:
            total=0
        espera=data_clientes.select_related().filter(estado__in=['Enviado','Recibido'])
        
        if orden != None:
            if orden == 'fecha':
                espera=espera.order_by("-estado",'fecha',"id_pedido")
            elif orden == 'total':
                espera=espera.order_by("-estado",'-total',"id_pedido")
            elif orden == 'cliente':
                espera=espera.order_by("-estado",'cliente__nombre','cliente__apellido',"id_pedido")
        else:
            espera=espera.order_by("-estado","-id_pedido")
        
        if(espera.count()!=0):
            total0=round(espera.aggregate(suma=Sum('total'))["suma"],2)
        else:
           total0=0
        recibidos=data_clientes.select_related().filter(estado="Recibido")
        if(recibidos.count()!=0):
            total1=round(recibidos.aggregate(suma=Sum('total'))["suma"],2)
        else:
           total1=0
        enviados=data_clientes.select_related().filter(estado="Enviado")
        if(enviados.count()!=0):
            total2=round(enviados.aggregate(suma=Sum('total'))["suma"],2)
        else:
           total2=0
        entregados=data_clientes.select_related().filter(estado="Entregado")
        if(entregados.count()!=0):
            total3=round(entregados.aggregate(suma=Sum('total'))["suma"],2)
        else:
           total3=0
        devueltos=data_clientes.select_related().filter(estado="Anulado")
        if(devueltos.count()!=0):
            total4=round(devueltos.aggregate(suma=Sum('total'))["suma"],2)
        else:
           total4=0
        pagina="THome"
        page = request.GET.get('page', 1)
        page0 = request.GET.get('page0', 1)
        if request.GET.get('page0') != None:
            pagina="tMenu0"
        page1 = request.GET.get('page1', 1)
        if request.GET.get('page1') != None:
            pagina="tMenu1"
        page2 = request.GET.get('page2', 1)
        if request.GET.get('page2') != None:
            pagina="tMenu2"
        page3 = request.GET.get('page3', 1)
        if request.GET.get('page3') != None:
            pagina="tMenu3"
        page4 = request.GET.get('page4', 1)
        if request.GET.get('page4') != None:
            pagina="tMenu4"
        paginator = Paginator(todos, 15)
        paginator0 = Paginator(espera, 1000000)
        paginator1 = Paginator(recibidos, 15)
        paginator2 = Paginator(enviados, 15)
        paginator3 = Paginator(entregados, 15)
        paginator4 = Paginator(devueltos, 15)
        try:
            pedidos = paginator.page(page)
            espera = paginator0.page(page0)
            recibidos = paginator1.page(page1)
            enviados = paginator2.page(page2)
            entregados = paginator3.page(page3)
            devueltos = paginator4.page(page4)
        except PageNotAnInteger:
            pedidos = paginator.page(1)
            espera = paginator0.page(1)
            recibidos = paginator1.page(1)
            enviados = paginator2.page(1)
            entregados = paginator3.page(1)
            devueltos = paginator4.page(1)
        except EmptyPage:
            pedidos = paginator.page(paginator.num_pages)
            espera = paginator0.page(paginator0.num_pages)
            recibidos = paginator1.page(paginator1.num_pages)
            enviados = paginator2.page(paginator2.num_pages)
            entregados = paginator3.page(paginator3.num_pages)
            devueltos = paginator4.page(paginator4.num_pages)
        diccionario={
           "datos":pedidos, "espera":espera, "recibidos":recibidos,
           "enviados":enviados,"entregados":entregados,
           "devueltos":devueltos,"filtro":orden,
           "desde":desde,"hasta":hasta,
           "tab":pagina,"total":total,
           "total0":total0,"total1":total1,"total2":total2,"total3":total3,"total4":total4}
        return render(request, "Pedidos/pedidos.html",diccionario)
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def pedidosEspera_page(request):
    if request.method=='GET':
        data_empleados=Pedido.objects.select_related("cliente").filter(estado__in=['Enviado','Espera','Recibido'])
        data_empleados=data_empleados.order_by("-estado","-id_pedido")
        return render(request, "Pedidos/pedidos-espera.html",{"datos":data_empleados})
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def devueltos_page(request):
    if request.method=='GET':
        data_empleados=Pedido.objects.select_related("cliente").filter(estado='Devuelto')
        data_empleados=data_empleados.order_by("-estado")
        return render(request, "Pedidos/pedidos-devueltos.html",{"datos":data_empleados})
    return HttpResponse(status=400)


@login_required(login_url='/login/')
def get_pedido(request,id_pedido):
	pedido=Pedido.objects.select_related().filter(id_pedido=id_pedido).first()
	producto_pedido=Producto_Pedido.objects.select_related().filter(pedido=pedido)
	oferta_pedido=Oferta_Pedido.objects.select_related().filter(pedido=pedido)
	combo_pedido=Combo_Pedido.objects.select_related().filter(pedido=pedido)
	cupon_pedido=Cupon_Pedido.objects.select_related().filter(pedido=pedido)
	context={"data": pedido,"productos":producto_pedido,"ofertas":oferta_pedido,"combos":combo_pedido,"cupones":cupon_pedido}
	return render(request, "Pedidos/modal-pedido.html",context)

@login_required(login_url='/login/')
def detalle_pedido(request,id_pedido):
	pedido=Pedido.objects.select_related().filter(id_pedido=id_pedido).first()
	producto_pedido=Producto_Pedido.objects.select_related().filter(pedido=pedido)
	oferta_pedido=Oferta_Pedido.objects.select_related().filter(pedido=pedido)
	combo_pedido=Combo_Pedido.objects.select_related().filter(pedido=pedido)
	cupon_pedido=Cupon_Pedido.objects.select_related().filter(pedido=pedido)
	context={"data": pedido,"productos":producto_pedido,"ofertas":oferta_pedido,"combos":combo_pedido,"cupones":cupon_pedido}
	return render(request, "Pedidos/detalle-pedido.html",context)

@login_required(login_url='/login/')
def get_calificacion(request,id_pedido):
	pedido=Pedido.objects.select_related().filter(id_pedido=id_pedido).first()
	calificacion=CalificacionPedido.objects.select_related().filter(pedido=pedido).first()
	context={"data": calificacion,"usuario": pedido.cliente}
	return render(request, "Reportes/calificacion.html",context)

@login_required(login_url='/login/')
def get_entregas(request):
    if request.method=='GET':
	    orden=request.GET.get("filtro")
	    print(orden)
	    desde=request.GET.get("from")
	    hasta=request.GET.get("to")
	    data_clientes=Pedido.objects.select_related()
	    if desde!=None and hasta!=None:
	        data_clientes=data_clientes.filter(fecha__range=[desde, hasta])
	    elif desde!=None:
	        data_clientes= data_clientes.filter(fecha__gte=desde)
	    elif hasta!=None:
	        data_clientes= data_clientes.filter(fecha__lte=hasta)
	    else:
	        data_clientes= data_clientes.filter(fecha__gte = datetime.now().replace(hour=0,minute=0,second=0))
	    data_clientes=data_clientes.order_by("-id_pedido")
	    if orden != None:
	        if orden == 'fecha':
	            data_clientes=data_clientes.order_by('-fecha',"-id_pedido")
	        elif orden == 'vCompra':
	            data_clientes=data_clientes.order_by('-total',"-id_pedido")
	        elif orden == 'estado':
	            data_clientes=data_clientes.order_by('estado',"-id_pedido")

	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_clientes, 5)
	    try:
	    	clientes = paginator.page(page)
	    except PageNotAnInteger:
	    	clientes = paginator.page(1)
	    except EmptyPage:
	    	clientes = paginator.page(paginator.num_pages)
	    return render(request, "Reportes/entregas.html",{"datos":clientes,"filtro":orden,"desde":desde,"hasta":hasta})
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def get_ventas(request):
    if request.method=='GET':
	    orden=request.GET.get("filtro")
	    print(orden)
	    desde=request.GET.get("from")
	    hasta=request.GET.get("to")
	    data_clientes=Pedido.objects.select_related().filter(pagado=True)
	    if desde!=None and hasta!=None:
	        data_clientes=data_clientes.filter(fecha__range=[desde, hasta])
	    elif desde!=None:
	        data_clientes= data_clientes.filter(fecha__gte=desde)
	    elif hasta!=None:
	        data_clientes= data_clientes.filter(fecha__lte=hasta)
	    else:
	        data_clientes= data_clientes.filter(fecha__gte = datetime.now().replace(hour=0,minute=0,second=0))
	    data_clientes=data_clientes.order_by("-id_pedido")
	    ventas=data_clientes.aggregate(ventas=Sum('total'))
	    if orden != None:
	        if orden == 'fecha':
	            data_clientes=data_clientes.order_by('-fecha',"-id_pedido")
	        elif orden == 'vCompra':
	            data_clientes=data_clientes.order_by('-total',"-id_pedido")
	        elif orden == 'estado':
	            data_clientes=data_clientes.order_by('estado',"-id_pedido")

	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_clientes, 5)
	    try:
	    	clientes = paginator.page(page)
	    except PageNotAnInteger:
	    	clientes = paginator.page(1)
	    except EmptyPage:
	    	clientes = paginator.page(paginator.num_pages)
	    return render(request, "Reportes/ventas.html",{"datos":clientes,"ventas":ventas,"filtro":orden,"desde":desde,"hasta":hasta})
    return HttpResponse(status=400)


@login_required(login_url='/login/')
def confirmar_pedido(request, id_pedido):
	pedido=Pedido.objects.select_related().filter(id_pedido=id_pedido).first()
	if pedido.estado == "Recibido":
	    pedido.estado="Enviado"
	else:
	    pedido.estado="Entregado"
	    pedido.pagado=True
	    calificacion=CalificacionPedido(calificacion=0,pedido=pedido,justificacion="")
	    calificacion.save()
	    devices=GCMDevice.objects.filter(user=pedido.cliente.usuario)
	    ec=pytz.timezone("America/Guayaquil")
	    fecha=pedido.fecha.astimezone(ec)
	    print(fecha)
	    print(fecha.strftime("%d/%m/%Y"))
	    mensaje= "Su pedido con fecha "+fecha.strftime("%d/%m/%Y")+" ha sido entregado, en la ventana historial de compras puede calificar su compra, esto nos ayudará a brindarle un mejor servicio."
	    data = {"title":"Pedido entregado","titulo": "Pedido entregado","id":pedido.id_pedido, "mensaje":mensaje,"color":"#ff7c55", "priority":"high","notification_foreground": "true"}
	    devices.send_message(mensaje, extra=data)
	pedido.save()
	pedido.save()
	return redirect("/pedidos")

@login_required(login_url='/login/')
def pagosPedido_page(request):
    if request.method=='GET':
	    filtro=request.GET.get("filtro")
	    busqueda=request.GET.get("busqueda")
	    desde=request.GET.get("from")
	    hasta=request.GET.get("to")
	    data_pagos=CalificacionPedido.objects
	    if desde!=None and hasta!=None:
	        data_pagos=data_pagos.filter(pedido__fecha__range=[desde, hasta])
	    elif desde!=None:
	        data_pagos= data_pagos.filter(pedido__fecha__gte=desde)
	    elif hasta!=None:
	        data_pagos= data_pagos.filter(pedido__fecha__lte=hasta)
	    else:
	        data_pagos= data_pagos.filter(pedido__fecha__gte = datetime.now().replace(hour=0,minute=0,second=0))
	    if request.GET.get("busqueda")!=None:
	        if filtro == "tPago":
	            data_pagos=data_pagos.filter(pedido__tipo_pago__icontains=busqueda)
	        elif filtro == "cliente":
	            data_pagos=data_pagos.filter(pedido__cliente__nombre__icontains=busqueda)
	    data_pagos=data_pagos.select_related().order_by("-pedido__id_pedido")
	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_pagos, 5)
	    try:
	    	pagos = paginator.page(page)
	    except PageNotAnInteger:
	    	pagos = paginator.page(1)
	    except EmptyPage:
	    	pagos = paginator.page(paginator.num_pages)
	    return render(request, "Reportes/pagos.html",{"datos":pagos,"filtro":filtro,"buscar":busqueda,"desde":desde,"hasta":hasta})
    return HttpResponse(status=400)


@login_required(login_url='/login/')
@csrf_exempt
def agregar_politica(request):
	if request.method == 'POST':
		name = request.POST.get('nombre', None)
		description = request.POST.get('descripcion', None)
		data_politica = Politica(nombre=name, detalle=description)
		data_politica.save()
		return render(request,"Politicas/politica.html",{"detalle": data_politica.detalle})
	if request.method=="GET":
	    pol = Politica.objects.last()
	    print(pol)
	    if pol != None:
	        print(pol.detalle)
	        return render(request, "Politicas/politica.html", {"detalle": pol.detalle})
	    ##print(pol.detalle)
	    return render(request, "Politicas/politica.html")

@login_required(login_url='/login/')
def cliente_page(request):
	if request.method=='GET':
	    orden=request.GET.get("filtro")
	    print(orden)
	    desde=request.GET.get("from")
	    hasta=request.GET.get("to")
	    data_clientes=Cliente.objects.select_related()
	    if desde!=None and hasta!=None:
	        data_clientes=data_clientes.filter(usuario__registro__range=[desde, hasta])
	    elif desde!=None:
	        data_clientes= data_clientes.filter(usuario__registro__gte=desde)
	    elif hasta!=None:
	        data_clientes= data_clientes.filter(usuario__registro__lte=hasta)
	    data_clientes=data_clientes.annotate(tot=Count('pedido'),suma=Sum('pedido__total')).order_by("id_cliente")
	    print("Data clientes",data_clientes)
	    if orden != None:
	        if orden == 'fecha':
	            data_clientes=data_clientes.order_by('-usuario__registro','id_cliente')
	        elif orden == 'nCompra':
	            data_clientes=data_clientes.order_by('-tot','id_cliente')
	        elif orden == 'vCompra':
	            data_clientes=data_clientes.order_by('-suma','id_cliente')

	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_clientes, 5)
	    try:
	    	clientes = paginator.page(page)
	    except PageNotAnInteger:
	    	clientes = paginator.page(1)
	    except EmptyPage:
	    	clientes = paginator.page(paginator.num_pages)

	    return render(request, "Reportes/clientes.html",{"datos":clientes,"filtro":orden,"desde":desde,"hasta":hasta})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
def notificacion_page(request):
	if request.method=='GET':
	    data_notificaciones=Notificacion.objects
	    valor = request.GET.get("busqueda")
	    if request.GET.get("busqueda")!=None:
	        data_notificaciones= data_notificaciones.filter(mensaje__icontains=str(valor))
	    data_notificaciones=data_notificaciones.order_by("-registro")
	    print(data_notificaciones)
	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_notificaciones, 5)
	    try:
	    	notificaciones = paginator.page(page)
	    except PageNotAnInteger:
	    	notificaciones = paginator.page(1)
	    except EmptyPage:
	    	notificaciones = paginator.page(paginator.num_pages)

	    return render(request, "Notificaciones/notificaciones.html",{"datos":notificaciones,"buscar":valor})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def agregar_notificacion(request):
    res=[]
    if request.method=='POST':
        try:
            name=request.POST.get('asunto',None)
            description = request.POST.get('mensaje',None)+"                        "
            imagen = request.FILES.get('image',None)
            tipo = request.POST.get('tipo',None)
            response_data = {}
            noti=Notificacion.objects.filter(asunto=name).first()
            if noti != None:
                response_data= 'Ya existe una notificación con este asunto'
                html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
                return JsonResponse({'html': html, 'result': "error"})
            notificacion = Notificacion(asunto=name, mensaje=description, image=imagen, tipo=tipo)
            notificacion.save()
            devices=GCMDevice.objects.all()
            if notificacion.photo_url != "":
                data = {"title":name,"color":"#ff7c55", "titulo": name, "mensaje": description, "priority":"high", "image": notificacion.photo_url,"notification_foreground": "true"}
            else:
                data = {"titulo": name, "title":name, "mensaje": description,"color":"#ff7c55", "priority":"high","notification_foreground": "true"}
            devices.send_message(description, extra=data)
            response_data= '!La notificación ha sido creada y enviada con éxito!'
            html = render_to_string("Avisos/correcto.html",{"data":response_data})
            return JsonResponse({'html': html, 'result': "ok"})
        except:
            response_data= '!Ha ocurrido un error, intente de nuevo!'
            html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
            return JsonResponse({'html': html, 'result': "error"})
    if request.method=='GET':
    	return render(request, "Notificaciones/add-notificaciones.html")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def enviar_notificacion(request,id_notificacion):
    res=[]
    if request.method=='GET':
	    notificacion=Notificacion.objects.get(id_notificacion=id_notificacion)
	    devices=GCMDevice.objects.all()
	    if notificacion.photo_url != "":
	        data = {"title":notificacion.asunto,"icon": "http://cabutoshop.pythonanywhere.com"+notificacion.photo_url,"color":"#ff7c55", "titulo": notificacion.asunto, "mensaje": notificacion.mensaje, "priority":"high", "image": notificacion.photo_url}
	    else:
	        data = {"title":notificacion.asunto,"titulo": notificacion.asunto, "mensaje": notificacion.mensaje,"color":"#ff7c55", "priority":"high"}
	    devices.send_message(notificacion.mensaje, extra=data)
	    response_data= '!La notificación ha sido creada y enviada con éxito!'
	    print(response_data)
	    html = render_to_string("Avisos/correcto.html",{"data":response_data})
	    return JsonResponse({'result': "ok"})
	    print("okay")
    print("okaay")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def editar_notificacion(request,id_notificacion):
	res=[]
	if request.method=='POST':
		name=request.POST.get('asunto',None)
		description = request.POST.get('mensaje',None)+"                        "
		imagen = request.FILES.get('image',None)
		tipo = request.POST.get('tipo',None)
		notificacion=Notificacion.objects.get(id_notificacion=id_notificacion)
		notificacion.asunto=name
		notificacion.mensaje=description
		if(imagen != None):
		    notificacion.image.delete()
		    notificacion.image=imagen
		notificacion.tipo=tipo
		notificacion.save()
		return redirect("/notificaciones")
	if request.method=='GET':
	    notificacion=Notificacion.objects.get(id_notificacion=id_notificacion)
	    return render(request, "Notificaciones/edit-notificaciones.html",{"data":notificacion})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
def ver_notificacion(request,id_notificacion):
	res=[]
	if request.method=='GET':
	    notificacion=Notificacion.objects.get(id_notificacion=id_notificacion)
	    return render(request, "Notificaciones/view-notificaciones.html",{"data":notificacion})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
def eliminar_notificacion(request,id_notificacion):
	data_producto=Notificacion.objects.get(id_notificacion=id_notificacion)
	if data_producto.image:
	    data_producto.image.delete()
	data_producto.delete()
	return redirect("/notificaciones")

@login_required(login_url='/login/')
def empleado_page(request):
    if request.method=='GET':
        data_empleados=Cliente.objects.select_related("usuario")
        valor = request.GET.get("busqueda")
        if request.GET.get("busqueda")!=None:
            data_empleados= data_empleados.filter(nombre__icontains=str(valor))
        data_empleados=data_empleados.order_by("nombre")
        return render(request, "Reportes/empleados.html",{"datos":data_empleados})
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def establecimiento_page(request):
	if request.method=='GET':
	    data_establecimientos=Establecimiento.objects
	    valor = request.GET.get("busqueda")
	    if request.GET.get("busqueda")!=None:
	        data_establecimientos= data_establecimientos.filter(nombre__icontains=str(valor))
	    data_establecimientos=data_establecimientos.order_by("id_establecimiento")
	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_establecimientos, 6)
	    try:
	    	establecimientos = paginator.page(page)
	    except PageNotAnInteger:
	    	establecimientos = paginator.page(1)
	    except EmptyPage:
	    	establecimientos = paginator.page(paginator.num_pages)

	    return render(request, "Establecimientos/establecimientos.html",{"datos":establecimientos,"buscar":valor})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def agregar_establecimiento(request):
	res=[]
	if request.method=='POST':
		name=request.POST.get('nombre',None)
		direccion = request.POST.get('direccion',None)
		telefono = request.POST.get('telefono',None)
		imagen = request.FILES.get('image',None)
		encargado = request.POST.get('encargado',None)
		latitud=request.POST.get('latitud',None)
		longitud=request.POST.get('longitud',None)
		for establecimiento in Establecimiento.objects.filter():
			n=establecimiento.nombre
			if name==n:
				return redirect("/establecimientos")
		data = Establecimiento(nombre=name, direccion=direccion, telefono=telefono,encargado=encargado,latitud=latitud,longitud=longitud, image=imagen, estado="1")
		data.save()
		return redirect("/establecimientos")
	if request.method=='GET':
		return render(request, "Establecimientos/add-establecimientos.html")
	return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def horario_page(request,id_establecimiento):
    print(request)
    if request.method=='POST':
        establecimiento=Establecimiento.objects.filter(id_establecimiento=id_establecimiento).first()
        horario=Horario.objects.filter(establecimiento=establecimiento)
        horario.delete()
        print(request.POST)
        dias=request.POST.getlist('day',None)
        print(dias)
        desde=request.POST.getlist('from',None)
        hasta=request.POST.getlist('to',None)
        for i in range(len(dias)):
            print(dias[i],desde[i],hasta[i])
            horario=Horario(dia=dias[i],hora_inicio=desde[i],hora_fin=hasta[i],establecimiento=establecimiento)
            horario.save()
        response_data= '!Horario de atención ha sido modificado con éxito!'
        html = render_to_string("Avisos/correcto.html",{"data":response_data})
        return JsonResponse({'html': html, 'result': "ok"})
    if request.method=='GET':
	    establecimiento=Establecimiento.objects.filter(id_establecimiento=id_establecimiento).first()
	    horario=Horario.objects.filter(establecimiento=establecimiento)
	    return render(request, "Establecimientos/horario.html",{"data":horario,"id":id_establecimiento})
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def redes_page(request):
    if request.method=="GET":
        data_redes=RedSocial.objects
        valor = request.GET.get("busqueda")
        if request.GET.get("busqueda")!=None:
            data_redes= data_redes.filter(nombre__icontains=str(valor))
        data_redes=data_redes.order_by("nombre")
        page = request.GET.get('page', 1)
        paginator = Paginator(data_redes, 6)
        try:
        	redes = paginator.page(page)
        except PageNotAnInteger:
        	redes = paginator.page(1)
        except EmptyPage:
        	redes = paginator.page(paginator.num_pages)
        return render(request, "RedesSociales/redesSociales.html",{"datos":redes,"buscar":valor})

    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def agregar_red(request):
    res=[]
    if request.method=='POST':
        try:
            name=request.POST.get('nombre',None)
            link = request.POST.get('enlace',None)
            imagen = request.FILES.get('image',None)
            response_data = {}
            red=RedSocial.objects.filter(nombre=name).first()
            if red != None:
                response_data= 'Ya se ha creado esta red'
                html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
                return JsonResponse({'html': html, 'result': "error"})
            data = RedSocial(nombre=name, enlace=link, icono=imagen)
            data.save()
            response_data= '!La red ha sido añadida con éxito!'
            html = render_to_string("Avisos/correcto.html",{"data":response_data})
            return JsonResponse({'html': html, 'result': "ok"})
        except:
            response_data= '!Ha ocurrido un error, intente de nuevo!'
            html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
            return JsonResponse({'html': html, 'result': "error"})
    if request.method=='GET':
        return render(request, "RedesSociales/add-redes.html")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def ver_red(request,id_red):
	res=[]
	if request.method=='GET':
		data=RedSocial.objects.get(id_red=id_red)
		return render(request, "RedesSociales/view-redes.html",{"data":data})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def editar_red(request,id_red):
	res=[]
	if request.method=='POST':
		name=request.POST.get('nombre',None)
		link = request.POST.get('enlace',None)
		imagen = request.FILES.get('image',None)
		data = RedSocial.objects.get(id_red=id_red)
		data.nombre=name
		data.enlace=link
		if(imagen != None):
		    data.icono.delete()
		    data.icono=imagen
		data.save()
		return redirect("/redesSociales")
	if request.method=='GET':
		data=RedSocial.objects.get(id_red=id_red)
		return render(request, "RedesSociales/edit-redes.html",{"data":data})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
def eliminar_red(request,id_red):
	data_producto=RedSocial.objects.get(id_red=id_red)
	if data_producto.icono:
	    data_producto.icono.delete()
	data_producto.delete()
	return redirect("/redesSociales")

@login_required(login_url='/login/')
def cobertura_page(request):
    if request.method=="GET":
        data_cobertura=ZonaEnvio.objects
        valor = request.GET.get("busqueda")
        if request.GET.get("busqueda")!=None:
            data_cobertura= data_cobertura.filter(nombre__icontains=str(valor))
        data_cobertura=data_cobertura.order_by("nombre")
        page = request.GET.get('page', 1)
        paginator = Paginator(data_cobertura, 6)
        try:
        	cobertura = paginator.page(page)
        except PageNotAnInteger:
        	cobertura = paginator.page(1)
        except EmptyPage:
        	cobertura = paginator.page(paginator.num_pages)
        return render(request, "Cobertura/cobertura.html",{"datos":cobertura,"buscar":valor})

    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def agregar_cobertura(request):
	res=[]
	if request.method=='POST':
		name=request.POST.get('nombre',None)
		color = request.POST.get('color',None)
		zona = request.POST.get('zona',None)
		envio = request.POST.get('envio',None)
		for cobertura in ZonaEnvio.objects.filter():
			n=cobertura.nombre
			if name==n:
				return redirect("/coberturaEnvio")
		data = ZonaEnvio(nombre=name, color=color, zona=zona, envio=envio)
		data.save()
		return redirect("/coberturaEnvio")
	if request.method=='GET':
	    data_cobertura=ZonaEnvio.objects.filter(estado='A').values("color","zona")
	    data_cobertura = list(data_cobertura)
	    return render(request, "Cobertura/add-cobertura.html",{"datos":data_cobertura})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def editar_cobertura(request,id_zona):
	res=[]
	if request.method=='POST':
	    data=ZonaEnvio.objects.get(id_zona=id_zona)
	    name=request.POST.get('nombre',None)
	    color = request.POST.get('color',None)
	    zona = request.POST.get('zona',None)
	    envio = request.POST.get('envio',None)
	    data.nombre=name
	    data.color=color
	    data.zona=zona
	    data.envio=envio
	    data.save()
	    return redirect("/coberturaEnvio")
	if request.method=='GET':
	    data=ZonaEnvio.objects.get(id_zona=id_zona)
	    data_cobertura=ZonaEnvio.objects.values("color","zona")
	    data_cobertura = list(data_cobertura)
	    return render(request, "Cobertura/edit-cobertura.html",{"datos":data_cobertura,"data":data})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
def ver_cobertura(request,id_zona):
	res=[]
	if request.method=='GET':
	    data=ZonaEnvio.objects.get(id_zona=id_zona)
	    return render(request, "Cobertura/view-cobertura.html",{"data":data})
	return HttpResponse(status=400)

@login_required(login_url='/login/')
def estado_cobertura(request,id_zona):
	data_zona=ZonaEnvio.objects.get(id_zona=id_zona)
	if data_zona.estado == "I":
	    data_zona.estado='A'
	else:
	    data_zona.estado='I'
	data_zona.save()
	return redirect("/coberturaEnvio")

@login_required(login_url='/login/')
def eliminar_cobertura(request,id_zona):
	data_zona=ZonaEnvio.objects.get(id_zona=id_zona)
	data_zona.delete()
	return redirect("/coberturaEnvio")

@login_required(login_url='/login/')
@csrf_exempt
def oferta_page(request):
    if request.method=='GET':
	    data_ofertas=Oferta.objects.exclude(estado="I")
	    valor = request.GET.get("busqueda")
	    if request.GET.get("busqueda")!=None:
	        data_ofertas= data_ofertas.filter(nombre__icontains=str(valor))
	    data_ofertas=data_ofertas.order_by("-id_oferta")
	    print(data_ofertas)
	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_ofertas, 5)
	    try:
	    	ofertas = paginator.page(page)
	    except PageNotAnInteger:
	    	ofertas = paginator.page(1)
	    except EmptyPage:
	    	ofertas = paginator.page(paginator.num_pages)

	    return render(request, "Ofertas/ofertas.html",{"datos":ofertas,"buscar":valor})
    elif request.method == 'POST':
	      agregar_ofertas(request)
	      return redirect("/ofertas")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def agregar_ofertas(request):
    data_establecimeinto = Establecimiento.objects.get(pk=1)
    res = []
    if request.method == 'POST':
        name = request.POST.get('nombre', None)
        description = request.POST.get('descripcion', None)
        priceA = request.POST.get('precioAntes', None)
        price = request.POST.get('precio', None)
        imagen = request.FILES.get('image', None)

        stock = request.POST.get('stock', None)
        for oferta in Oferta.objects.filter():
            n = oferta.nombre
            if name == n:
                return render(request, "Ofertas/ofertas.html")
        data = Oferta(nombre=name,descripcion=description,precioAntes=priceA,precio=price,cantidad=stock,image=imagen,id_establecimiento=data_establecimeinto)
        data.save()
        return  redirect("/ofertas")
    if request.method=='GET':
        return render(request,"Ofertas/añadir_ofertas.html")
    return HttpResponse(status=400)
        #return render(request, "Ofertas/añadir_ofertas.html")

@login_required(login_url='/login/')
@csrf_exempt
def editar_ofertas(request,id_oferta):
    print("voy a editar ofertas")
    if request.method == 'GET':
        data_oferta = Oferta.objects.get(id_oferta=id_oferta)
        print(data_oferta)
        return render(request, "Ofertas/edit_ofert.html", {"datos_mostrar": data_oferta})
    elif request.method == 'POST':
        update_ofertas(request,id_oferta)
        return redirect("/ofertas")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def update_ofertas(request,id_oferta):
    if request.method == 'POST':
        data_oferta = Oferta.objects.get(id_oferta=id_oferta)
        data_oferta.nombre = request.POST.get('nombre', None)
        data_oferta.descripcion = request.POST.get('descripcion', None)
        data_oferta.precioAntes = request.POST.get('precioAntes', None)
        data_oferta.precio = request.POST.get('precio', None)
        if request.FILES.get('image', None) != None:
            data_oferta.image.delete()
            data_oferta.image = request.FILES.get('image', None)
        data_oferta.cantidad = request.POST.get('stock', None)
        data_oferta.save()

@login_required(login_url='/login/')
def eliminar_ofertas(request,id_oferta):
    try:
        data_oferta = Oferta.objects.get(id_oferta=id_oferta)
        if(data_oferta.estado == "A"):
            data_oferta.estado="I"
        else:
            data_oferta.estado="A"
        data_oferta.save()
        response_data= 'La oferta ha cambiado su estado'
        html = render_to_string("Avisos/correcto.html",{"data":response_data})
        return JsonResponse({'html': html, 'result': "ok"})
    except:
        response_data= 'Ha ocurrido un error, intente de nuevo'
        html = render_to_string("Avisos/incorrecto.html",{"data":response_data})
        return JsonResponse({'html': html, 'result': "error"})

@login_required(login_url='/login/')
@csrf_exempt
def cupon_page(request):
    if request.method=='GET':
	    data_cupon=Cupones.objects.exclude(estado="I")
	    valor = request.GET.get("busqueda")
	    if request.GET.get("busqueda")!=None:
	        data_cupon= data_cupon.filter(nombre__icontains=str(valor))
	    data_cupon=data_cupon.order_by("-id_cupon")
	    print(data_cupon)
	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_cupon, 5)
	    try:
	    	cupones = paginator.page(page)
	    except PageNotAnInteger:
	    	cupones = paginator.page(1)
	    except EmptyPage:
	    	cupones = paginator.page(paginator.num_pages)
	    return render(request, "Cupones/Cupones.html",{"datos":cupones,"buscar":valor})
    elif request.method == 'POST':
	    return render(request, "Cupones/add-cupones.html")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def add_cupon(request):
    if request.method=='GET':
	    return render(request, "Cupones/add-cupones.html")
    elif request.method == 'POST':
        data_establecimiento = Establecimiento.objects.get(pk=1)
        inicio=request.POST.get("from", None)
        fin=request.POST.get("to", None)
        name = request.POST.get('nombre', None)
        description = request.POST.get('descripcion', None)
        price = request.POST.get('precio', 0)
        imagen = request.FILES.get('image', None)
        stock = request.POST.get('cantidad', None)
        data = Cupones(nombre=name,descripcion=description,precio=price,cantidad=stock,fecha_inicio=inicio,fecha_fin=fin,image=imagen,id_establecimiento=data_establecimiento)
        data.save()
        return  redirect("/cupones")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
@csrf_exempt
def editar_cupon(request, id_cupon):
    if request.method=='GET':
        data_cupon= Cupones.objects.get(id_cupon=id_cupon)
        return render(request, "Cupones/edit-cupon.html",{"data":data_cupon})
    elif request.method == 'POST':
        inicio=request.POST.get("from", None)
        fin=request.POST.get("to", None)
        name = request.POST.get('nombre', None)
        description = request.POST.get('descripcion', None)
        imagen = request.FILES.get('image', None)
        stock = request.POST.get('cantidad', None)
        data= Cupones.objects.get(id_cupon=id_cupon)
        data.nombre=name
        data.descripcion=description
        data.cantidad=stock
        data.fecha_inicio=inicio
        data.fecha_fin=fin
        if(imagen != None):
            data.image.delete()
            data.image=imagen
        data.save()
        return  redirect("/cupones")
    return HttpResponse(status=400)

@login_required(login_url='/login/')
def eliminar_cupon(request,id_cupon):
    data_cupon= Cupones.objects.get(id_cupon=id_cupon)
    data_cupon.estado="I"
    data_cupon.save()
    return redirect("/cupones")

@login_required(login_url='/login/')
@csrf_exempt
def combo_page(request):
    if request.method=='GET':
	    data_combos=Combo.objects
	    valor = request.GET.get("busqueda")
	    if request.GET.get("busqueda")!=None:
	        data_combos= data_combos.filter(nombre__icontains=str(valor))
	    data_combos=data_combos.order_by("-id_combo")
	    print(data_combos)
	    page = request.GET.get('page', 1)
	    paginator = Paginator(data_combos, 5)
	    try:
	    	combos = paginator.page(page)
	    except PageNotAnInteger:
	    	combos = paginator.page(1)
	    except EmptyPage:
	    	combos = paginator.page(paginator.num_pages)
	    return render(request, "Combos/Combo.html",{"datos":combos,"buscar":valor})
    elif request.method == 'POST':
	      #agregar_ofertas(request)
	      return redirect("/combos")
    return HttpResponse(status=400)