from django.db import models

from django.conf import settings

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

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


class Cotizacion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    id_cotizacion = models.AutoField(primary_key=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE) 
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    comentario = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"Cotización {self.id_cotizacion} - {self.servicio.nombre} - {self.estado}"

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
