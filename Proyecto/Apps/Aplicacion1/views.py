from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario, Rol, Producto, Servicio, Carrito, ItemCarrito, Cotizacion
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
from django.utils.dateparse import parse_date
from datetime import datetime, time
from django.utils.dateparse import parse_date

def home(request):
    return render(request, 'home.html')

def authenticate_user(correo, password):
    """Autenticación personalizada de usuario."""
    try:
        usuario = Usuario.objects.get(correo=correo)
        if check_password(password, usuario.contraseña):
            return usuario
        return None
    except Usuario.DoesNotExist:
        return None

def login_empleados(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        usuario = authenticate_user(email, password)

        if usuario is not None and usuario.rol.nombre == 'Empleado':
            request.session['usuario_id'] = usuario.id 
            return redirect('') 
        else:
            messages.error(request, "Credenciales inválidas o no eres un empleado")

    return render(request, 'login_empleados.html')

def login_clientes(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        usuario = authenticate_user(email, password)

        if usuario is not None:
            request.session['usuario_id'] = usuario.id
            request.session['cedula_cliente'] = usuario.cedula  
            return redirect('inicio') 
        else:
            messages.error(request, "Credenciales inválidas")

    return render(request, 'login_clientes.html')  

def reg_clientes(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cedula = request.POST.get('cedula')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        email = request.POST.get('email')
        password = request.POST.get('password')
        aceptar_condiciones = request.POST.get('terminos') is not None

        foto_url = None
        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            fs = FileSystemStorage()
            filename = fs.save(foto.name, foto)
            foto_url = fs.url(filename)

        errores = []

        if '@' not in email:
            errores.append("El correo electrónico debe contener un '@'.")
        if Usuario.objects.filter(correo=email).exists():
            errores.append("El correo ya está registrado. Por favor, elige otro.")

        fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
        fecha_nacimiento = parse_date(fecha_nacimiento_str) if fecha_nacimiento_str else None
        if fecha_nacimiento:
            fecha_actual = datetime.now().date()
            if fecha_nacimiento >= fecha_actual:
                errores.append("La fecha de nacimiento no puede ser la fecha actual ni una fecha futura.")

        if not aceptar_condiciones:
            errores.append("Debes aceptar los términos y condiciones.")

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('reg_clientes')

        nuevo_usuario = Usuario(
            nombre=nombre,
            cedula=cedula,
            telefono=telefono,
            direccion=direccion,
            correo=email,
            contraseña=make_password(password),
            foto_perfil=foto_url,
            fecha_nacimiento=fecha_nacimiento,
            aceptar_condiciones=aceptar_condiciones,
            rol=Rol.objects.get(nombre='Clientes')
        )
        nuevo_usuario.save()

        messages.success(request, 'Usuario registrado exitosamente.')
        return redirect('login_clientes')

    return render(request, 'reg_clientes.html')

def inicio(request):

    if not request.session.get('usuario_id'):
        return redirect('login_clientes')
    
    productos = Producto.objects.all()
    servicios = Servicio.objects.all()
    
    context = {
        'productos': productos,
        'servicios': servicios,
    }
    return render(request, 'inicio.html', context)

def reg_productos(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cant_producto = request.POST.get('cant_producto')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        
        errores = []
        
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not cant_producto:
            errores.append("La cantidad es obligatoria.")
        else:
            try:
                cant_producto = int(cant_producto)
                if cant_producto < 0:
                    errores.append("La cantidad no puede ser negativa.")
            except ValueError:
                errores.append("La cantidad debe ser un número entero.")
        if not descripcion:
            errores.append("La descripción es obligatoria.")
        if not precio:
            errores.append("El precio es obligatorio.")
        else:
            try:
                precio = float(precio)
                if precio < 0:
                    errores.append("El precio no puede ser negativo.")
            except ValueError:
                errores.append("El precio debe ser un número válido.")
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('reg_productos')
        
        nuevo_producto = Producto(
            nombre=nombre,
            cant_producto=cant_producto,
            descripcion=descripcion,
            precio=precio
        )
        nuevo_producto.save()
        messages.success(request, 'Producto registrado exitosamente.')
        return redirect('inicio') 
    
    return render(request, 'reg_productos.html')

def reg_servicios(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')        
        errores = []
        
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not descripcion:
            errores.append("La descripción es obligatoria.")
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('reg_servicios')
        
        nuevo_servicio = Servicio(
            nombre=nombre,
            descripcion=descripcion,
        )
        nuevo_servicio.save()
        messages.success(request, 'Servicio registrado exitosamente.')
        return redirect('inicio') 
    
    return render(request, 'reg_servicios.html')

def agregar_al_carrito(request, id_producto):
    if request.method == 'POST':
        if not request.session.get('usuario_id'):
            messages.error(request, "Debes iniciar sesión para agregar productos al carrito.")
            return redirect('login_clientes')
        
        try:
            producto = Producto.objects.get(id_producto=id_producto)
        except Producto.DoesNotExist:
            messages.error(request, "El producto no existe.")
            return redirect('inicio')
        
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            messages.error(request, "Cantidad inválida.")
            return redirect('inicio')
        
        if cantidad < 1:
            messages.error(request, "La cantidad debe ser al menos 1.")
            return redirect('inicio')
        
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        carrito, created = Carrito.objects.get_or_create(usuario=usuario)
        
        item, created_item = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto, defaults={'cantidad': cantidad})
        if not created_item:
            item.cantidad += cantidad
            item.save()
        
        messages.success(request, "Producto añadido al carrito.")
        return redirect('inicio')
    else:
        return redirect('inicio')
    
def ver_carrito(request):
    if not request.session.get('usuario_id'):
        messages.error(request, "Debes iniciar sesión para ver el carrito.")
        return redirect('login_clientes')
    
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)
    total_items = sum(item.cantidad for item in carrito.items.all())
    
    context = {
        'carrito': carrito,
        'total_items': total_items,
    }
    return render(request, 'carrito.html', context)

def eliminar_item_carrito(request, item_id):
    if request.method == 'POST':
        try:
            item = ItemCarrito.objects.get(id=item_id)
            item.delete()
            messages.success(request, "Producto eliminado del carrito.")
        except ItemCarrito.DoesNotExist:
            messages.error(request, "El producto no existe en el carrito.")
    else:
        messages.error(request, "Acción no permitida.")
    return redirect('carrito')

def cotizaciones_view(request):
    if request.method == "POST":
        departamento = request.POST.get("departamento")
        ciudad = request.POST.get("ciudad")
        fecha_servicio = request.POST.get("fecha_servicio")
        hora_servicio = request.POST.get("hora_servicio")
        direccion_servicio = request.POST.get("direccion_servicio")
        especificaciones = request.POST.get("especificaciones", "")
        fecha_servicio_date = parse_date(fecha_servicio)
        current_date = datetime.now().date()
        if not fecha_servicio_date or fecha_servicio_date < current_date:
            messages.error(request, "La fecha del servicio no puede ser anterior a la fecha actual.")
            return redirect("cotizaciones")
        if (fecha_servicio_date - current_date).days < 4:
            messages.error(request, "Debe seleccionar una fecha que permita al menos 3 días de preparación para alistar los materiales.")
            return redirect("cotizaciones")

        try:
            hora_servicio_obj = datetime.strptime(hora_servicio, "%H:%M").time()
        except ValueError:
            messages.error(request, "Formato de hora inválido.")
            return redirect("cotizaciones")
        if hora_servicio_obj < time(8, 0) or hora_servicio_obj > time(19, 0):
            messages.error(request, "La hora del servicio debe estar entre las 8:00 AM y las 7:00 PM.")
            return redirect("cotizaciones")

        service_id = request.POST.get("service_id")
        if not service_id:
            messages.error(request, "No se ha seleccionado un servicio.")
            return redirect("inicio")
        try:
            servicio = Servicio.objects.get(pk=service_id)
        except Servicio.DoesNotExist:
            messages.error(request, "El servicio seleccionado no existe.")
            return redirect("inicio")
        
        if not request.session.get("usuario_id"):
            messages.error(request, "Debes iniciar sesión para solicitar una cotización.")
            return redirect("login_clientes")
        usuario = Usuario.objects.get(id=request.session["usuario_id"])

        nueva_cotizacion = Cotizacion(
            servicio=servicio,
            usuario=usuario,
            fecha_servicio=fecha_servicio,
            hora_servicio=hora_servicio,
            direccion_servicio=direccion_servicio,
            departamento=departamento,
            ciudad=ciudad,
            especificaciones=especificaciones
        )
        nueva_cotizacion.save()
        messages.success(request, "Su solicitud de cotización ha sido registrada exitosamente.")
        return redirect("inicio")
    else:
        return render(request, "cotizaciones.html")