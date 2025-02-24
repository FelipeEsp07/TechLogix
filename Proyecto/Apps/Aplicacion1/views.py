from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario, Rol, Producto, Servicio, Carrito, ItemCarrito, Cotizacion, EvaluacionCotizacion
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
from django.utils.dateparse import parse_date
from datetime import datetime, time, timedelta
from django.utils.dateparse import parse_date
from decimal import Decimal
from django.core.exceptions import ValidationError


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

def crear_rol(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        
        if not nombre:
            messages.error(request, "El nombre del rol es obligatorio.")
            return redirect('crear_rol')
        
        if Rol.objects.filter(nombre=nombre).exists():
            messages.error(request, "El rol ya existe.")
            return redirect('crear_rol')
        
        nuevo_rol = Rol(nombre=nombre)
        nuevo_rol.save()
        
        messages.success(request, "Rol creado exitosamente.")
        return redirect('dashboard_admin')
    
    return render(request, 'crear_rol.html')

def login_clientes(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        usuario = authenticate_user(email, password)

        if usuario is not None:
            request.session['usuario_id'] = usuario.id
            request.session['cedula_cliente'] = usuario.cedula  

            if usuario.rol.nombre == 'Administrador':
                return redirect('dashboard_admin')
            elif usuario.rol.nombre == 'Analista':
                return redirect('dash_analista') 
            else:
                return redirect('inicio')
        else:
            messages.error(request, "Credenciales inválidas")
    
    return render(request, 'login_clientes.html')

def reg_empleados(request):
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

        rol_id = request.POST.get('rol')
        if not rol_id:
            errores.append("Seleccione un rol.")

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('reg_empleados')

        rol = Rol.objects.get(id=rol_id)

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
            rol=rol,
        )
        nuevo_usuario.save()

        messages.success(request, 'Usuario registrado exitosamente.')
        return redirect('dashboard_admin')

    roles = Rol.objects.all()
    return render(request, 'reg_empleados.html', {'roles': roles})

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
    
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    productos = Producto.objects.all()
    servicios = Servicio.objects.all()
    
    context = {
        'productos': productos,
        'servicios': servicios,
        'usuario': usuario,
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
        
        imagen = request.FILES.get('imagen', None)
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('reg_productos')
        
        nuevo_producto = Producto(
            nombre=nombre,
            cant_producto=cant_producto,
            descripcion=descripcion,
            precio=precio,
            imagen=imagen 
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
        
        imagen = request.FILES.get('imagen', None)
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('reg_servicios')
        
        nuevo_servicio = Servicio(
            nombre=nombre,
            descripcion=descripcion,
            imagen=imagen
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
    if request.method == "GET":
        fecha_str = request.GET.get("fecha_servicio")
        available_slots = []
        possible_slots = [time(h, 0) for h in range(6, 17)]
        if fecha_str:
            selected_date = parse_date(fecha_str)
            citas = Cotizacion.objects.filter(fecha_servicio=selected_date, estado='visita_programada')
            for slot in possible_slots:
                slot_start = datetime.combine(selected_date, slot)
                slot_end = slot_start + timedelta(hours=2)
                conflict = False
                for cita in citas:
                    cita_start = datetime.combine(cita.fecha_servicio, cita.hora_servicio)
                    cita_end = cita_start + timedelta(hours=2)
                    if slot_start < cita_end and cita_start < slot_end:
                        conflict = True
                        break
                if not conflict:
                    available_slots.append(slot.strftime("%H:%M"))
        else:
            available_slots = [slot.strftime("%H:%M") for slot in possible_slots]
        
        context = {
            'available_slots': available_slots,
        }
        return render(request, "cotizaciones.html", context)
    
    elif request.method == "POST":
        departamento = request.POST.get("departamento")
        ciudad = request.POST.get("ciudad")
        fecha_servicio = request.POST.get("fecha_servicio")
        hora_servicio_str = request.POST.get("hora_servicio")
        direccion_servicio = request.POST.get("direccion_servicio")
        especificaciones = request.POST.get("especificaciones", "")
        
        fecha_servicio_date = parse_date(fecha_servicio)
        current_date = datetime.now().date()
        if not fecha_servicio_date or fecha_servicio_date < current_date:
            messages.error(request, "La fecha del servicio no puede ser anterior a la fecha actual.")
            return redirect("cotizaciones")
        if (fecha_servicio_date - current_date).days < 4:
            messages.error(request, "Debe seleccionar una fecha que permita al menos 3 días de preparación.")
            return redirect("cotizaciones")
        
        try:
            hora_servicio_obj = datetime.strptime(hora_servicio_str, "%H:%M").time()
        except ValueError:
            messages.error(request, "Formato de hora inválido.")
            return redirect("cotizaciones")
        if hora_servicio_obj < time(6, 0) or hora_servicio_obj > time(16, 0):
            messages.error(request, "La hora del servicio debe estar entre las 6:00 AM y las 4:00 PM.")
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
        
        cotizacion = Cotizacion.objects.create(
            servicio=servicio,
            usuario=usuario,
            fecha_servicio=fecha_servicio_date,
            hora_servicio=hora_servicio_obj,
            direccion_servicio=direccion_servicio,
            departamento=departamento,
            ciudad=ciudad,
            especificaciones=especificaciones,
        )
        
        try:
            cotizacion.programar_visita()
        except Exception as e:
            messages.error(request, f"Error al programar la visita: {e}")
            return redirect("cotizaciones")
        
        messages.success(request, "Cotización registrada y visita programada exitosamente.")
        return redirect("inicio")
 
def recibo_cotizacion(request, id_cotizacion):
    cotizacion = get_object_or_404(Cotizacion, id_cotizacion=id_cotizacion)
    evaluacion = getattr(cotizacion, 'evaluacion', None)
    
    if evaluacion:
        mano_obra = evaluacion.precio_mano_obra
        desplazamiento = evaluacion.precio_desplazamiento
        total = evaluacion.valor_total
        fecha_programada = evaluacion.fecha_servicio_programado
        hora_programada = evaluacion.hora_servicio_programado
    else:
        from decimal import Decimal
        mano_obra = Decimal('50000')
        desplazamiento = Decimal('20000')
        total = cotizacion.servicio.precio + mano_obra + desplazamiento
        fecha_programada = cotizacion.fecha_servicio
        hora_programada = cotizacion.hora_servicio

    context = {
        'cotizacion': cotizacion,
        'evaluacion': evaluacion,
        'mano_obra': mano_obra,
        'desplazamiento': desplazamiento,
        'total': total,
        'fecha_servicio_programado': fecha_programada,
        'hora_servicio_programado': hora_programada,
    }
    return render(request, "recibo_cotizacion.html", context)

def confirmar_cotizacion(request):
    if request.method == "POST":
        servicio_id = request.POST.get("servicio_id")
        departamento = request.POST.get("departamento")
        ciudad = request.POST.get("ciudad")
        fecha_servicio = request.POST.get("fecha_servicio")
        hora_servicio = request.POST.get("hora_servicio")
        direccion_servicio = request.POST.get("direccion_servicio")
        especificaciones = request.POST.get("especificaciones")
        
        if not request.session.get("usuario_id"):
            messages.error(request, "Debes iniciar sesión para confirmar la cotización.")
            return redirect("login_clientes")
        usuario = Usuario.objects.get(id=request.session["usuario_id"])
        servicio = Servicio.objects.get(pk=servicio_id)
        
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
        messages.success(request, "Cotización confirmada exitosamente.")
        return redirect("recibo_cotizacion", id_cotizacion=nueva_cotizacion.id_cotizacion)
    else:
        messages.error(request, "Acción no permitida.")
        return redirect("inicio")
    
def cancelar_cotizacion(request):
    messages.info(request, "Cotización cancelada.")
    return redirect("inicio")

def dashboard_admin(request):
    usuarios_count = Usuario.objects.count()
    productos_count = Producto.objects.count()
    cotizaciones_count = Cotizacion.objects.filter(estado='pendiente').count()
    
    context = {
        'usuarios_count': usuarios_count,
        'productos_count': productos_count,
        'cotizaciones_count': cotizaciones_count,
    }
    return render(request, 'dash_admin.html', context)

def dash_analista(request):
    usuarios_count = Usuario.objects.count()
    productos_count = Producto.objects.count()
    cotizaciones_count = Cotizacion.objects.filter(estado='pendiente').count()
    
    context = {
        'usuarios_count': usuarios_count,
        'productos_count': productos_count,
        'cotizaciones_count': cotizaciones_count,
    }

    return render(request, 'dash_analista.html')

def tablero(request):
    if request.method == "POST":
        action = request.POST.get("action")
        id_cotizacion = request.POST.get("id_cotizacion")
        
        if not id_cotizacion:
            messages.error(request, "No se proporcionó el ID de la cotización.")
            return redirect("tablero")
        
        try:
            cotizacion = Cotizacion.objects.get(id_cotizacion=id_cotizacion)
        except Cotizacion.DoesNotExist:
            messages.error(request, "Cotización no encontrada.")
            return redirect("tablero")
        
        if cotizacion.estado.lower() != "evaluado":
            messages.error(request, "La cotización ya fue procesada.")
            return redirect("tablero")
        
        if action == "aceptar":
            cotizacion.estado = "aprobado"
            messages.success(request, "Cotización aprobada exitosamente.")
        elif action == "rechazar":
            cotizacion.estado = "rechazado"
            messages.success(request, "Cotización rechazada exitosamente.")
        else:
            messages.error(request, "Acción no válida.")
        
        cotizacion.save()
        return redirect("tablero")
    else:
        cotizaciones = Cotizacion.objects.all().order_by('-fecha_solicitud')
        context = {
            'cotizaciones': cotizaciones,
        }
        return render(request, "tablero.html", context)

def aceptar_cotizacion(request, id_cotizacion):
    if request.method == 'POST':
        cotizacion = get_object_or_404(Cotizacion, id_cotizacion=id_cotizacion)
        if cotizacion.estado == 'evaluado':
            try:
                cotizacion.aprobar()
                messages.success(request, "Cotización aprobada exitosamente.")
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, "La cotización ya fue procesada.")
        return redirect('dashboard_cotizaciones')
    else:
        messages.error(request, "Acción no permitida.")
        return redirect('dashboard_cotizaciones')

def rechazar_cotizacion(request, id_cotizacion):
    if request.method == 'POST':
        cotizacion = get_object_or_404(Cotizacion, id_cotizacion=id_cotizacion)
        if cotizacion.estado == 'evaluado':
            try:
                comentario = request.POST.get('comentario', '')
                cotizacion.rechazar(comentario)
                messages.success(request, "Cotización rechazada exitosamente.")
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, "La cotización ya fue procesada.")
        return redirect('dashboard_cotizaciones')
    else:
        messages.error(request, "Acción no permitida.")
        return redirect('dashboard_cotizaciones')
    
def listar_visitas_programadas(request):
    visitas = Cotizacion.objects.filter(estado='visita_programada')
    context = {
        'visitas': visitas,
    }
    return render(request, "lista_solicitudes_visita.html", context)

def evaluar_cotizacion(request, id_cotizacion):
    cotizacion = get_object_or_404(Cotizacion, id_cotizacion=id_cotizacion)
    
    if request.method == "POST":
        insumos = request.POST.get("insumos")
        observaciones = request.POST.get("observaciones", "")
        tiempo_estimado = request.POST.get("tiempo_estimado")
        precio_mano_obra = request.POST.get("precio_mano_obra")
        precio_insumos = request.POST.get("precio_insumos")
        precio_desplazamiento = request.POST.get("precio_desplazamiento")
        valor_total = request.POST.get("valor_total")
        fecha_servicio_programado = request.POST.get("fecha_servicio_programado")
        hora_servicio_programado = request.POST.get("hora_servicio_programado")
        
        evaluacion = EvaluacionCotizacion(
            cotizacion=cotizacion,
            insumos=insumos,
            observaciones=observaciones,
            tiempo_estimado=tiempo_estimado,
            precio_mano_obra=precio_mano_obra,
            precio_insumos=precio_insumos,
            precio_desplazamiento=precio_desplazamiento,
            valor_total=valor_total,
            fecha_servicio_programado=fecha_servicio_programado,
            hora_servicio_programado=hora_servicio_programado
        )
        
        try:
            evaluacion.save()
            messages.success(request, "Evaluación registrada exitosamente.")
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('evaluar_cotizacion', id_cotizacion=id_cotizacion)
        
        return redirect('listar_visitas_programadas')
    
    context = {"cotizacion": cotizacion}
    return render(request, "evaluar_cotizacion.html", context)

def solicitudes(request):
    if not request.session.get('usuario_id'):
        return redirect('login_clientes')
    
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    
    cotizaciones = Cotizacion.objects.filter(usuario=usuario)
    
    try:
        carrito = Carrito.objects.get(usuario=usuario)
    except Carrito.DoesNotExist:
        carrito = None
    
    context = {
        'usuario': usuario,
        'cotizaciones': cotizaciones,
        'carrito': carrito,
    }
    
    return render(request, 'solicitudes.html', context)
