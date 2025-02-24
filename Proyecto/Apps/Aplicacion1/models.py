from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time
from django.utils import timezone

class Rol(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    aceptar_condiciones = models.BooleanField(default=False)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    puesto = models.CharField(max_length=100)
    certificaciones = models.FileField(upload_to='certificaciones/', blank=True, null=True)

    def __str__(self):
        return f'{self.usuario.nombre} - {self.puesto}'
    
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    cant_producto = models.IntegerField()
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='producto/', blank=True, null=True)


    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='servicio/', blank=True, null=True)


    def __str__(self):
        return self.nombre
    
class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.nombre}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class Cotizacion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('visita_programada', 'Visita Programada'),
        ('evaluado', 'Evaluado'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id_cotizacion = models.AutoField(primary_key=True)
    servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_servicio = models.DateField()
    hora_servicio = models.TimeField()
    direccion_servicio = models.TextField()
    departamento = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    especificaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    comentario = models.TextField(blank=True, null=True)
    insumos = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cotización {self.id_cotizacion} - {self.servicio.nombre} - {self.estado}"
    
    def analista_disponible(self):
        VISIT_DURATION = timedelta(hours=1)
        nueva_inicio = datetime.combine(self.fecha_servicio, self.hora_servicio)
        nueva_fin = nueva_inicio + VISIT_DURATION
        citas_conflictivas = Cotizacion.objects.filter(
            estado='visita_programada',
            fecha_servicio=self.fecha_servicio
        ).exclude(pk=self.pk)

        for cita in citas_conflictivas:
            cita_inicio = datetime.combine(cita.fecha_servicio, cita.hora_servicio)
            cita_fin = cita_inicio + VISIT_DURATION
            if nueva_inicio < cita_fin and cita_inicio < nueva_fin:
                return False
        return True

    def programar_visita(self):
        if self.estado != 'pendiente':
            raise ValidationError("Solo se puede programar la visita si la cotización está en estado 'pendiente'.")
        if not self.analista_disponible():
            raise ValidationError("El analista ya tiene una visita programada en ese horario.")
        self.estado = 'visita_programada'
        self.save()

    def registrar_evaluacion(self, insumos):
        if self.estado != 'visita_programada':
            raise ValidationError("La cotización debe estar en estado 'visita_programada' para registrar la evaluación.")
        self.insumos = insumos
        self.estado = 'evaluado'
        self.save()

    def aprobar(self):
        if self.estado != 'evaluado':
            raise ValidationError("La cotización debe estar en estado 'evaluado' para poder aprobarla.")
        self.estado = 'aprobado'
        self.save()

    def rechazar(self, comentario=None):
        if self.estado != 'rechazado':
            raise ValidationError("La cotización debe estar en estado 'evaluado' para poder rechazarla.")
        self.comentario = comentario
        self.estado = 'rechazado'
        self.save()


class EvaluacionCotizacion(models.Model):
    cotizacion = models.OneToOneField('Cotizacion', on_delete=models.CASCADE, related_name='evaluacion')
    insumos = models.TextField(help_text="Descripción de los insumos necesarios.")
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones y comentarios técnicos.")
    tiempo_estimado = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tiempo estimado en horas.")
    precio_mano_obra = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    default=0.00, 
    help_text="Precio de mano de obra."
    )
    precio_insumos = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    default=0.00, 
    help_text="Precio de los insumos."
    )
    precio_desplazamiento = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        help_text="Precio de desplazamiento."
    )    
    valor_total = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    default=0.00, 
    help_text="Valor total a pagar."
    )
    fecha_servicio_programado = models.DateField(default=timezone.now, help_text="Fecha programada para realizar el servicio.")
    hora_servicio_programado = models.TimeField(default=time(9, 0), help_text="Hora programada para realizar el servicio.")
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de Cotización {self.cotizacion.id_cotizacion}"

    def save(self, *args, **kwargs):
        if self.cotizacion.estado != 'visita_programada':
            raise ValidationError("La cotización debe estar en estado 'visita_programada' para registrar la evaluación.")
        self.cotizacion.estado = 'evaluado'
        self.cotizacion.save()
        super().save(*args, **kwargs)