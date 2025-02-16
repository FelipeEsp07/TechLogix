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
