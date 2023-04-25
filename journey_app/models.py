from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
from django.db import models


class Usuario(models.Model):
    usuario = models.CharField(max_length=100, unique=True, validators=[EmailValidator(message='Ingresa una dirección de correo válida')])
    password = models.CharField(max_length=100, help_text='La contraseña se almacenará en forma de hash', default=make_password)
    activo = models.BooleanField(default=False)
    nombre = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.usuario

    class Meta:
        verbose_name_plural = "Usuarios"


class Itinerario(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class Usu_ite(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='usu_ites')
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False)
    fecha_create = models.DateTimeField(auto_now_add=True)
    fecha_update = models.DateTimeField(blank=True, null=True)
    dif_fecha = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.usuario} - {self.itinerario.nombre}"

    class Meta:
        verbose_name = 'Usu_ite'
        verbose_name_plural = 'Usu_iten'


class Encuesta(models.Model):
    usuario = models.CharField(max_length=100)
    id_pregunta = models.IntegerField()
    id_respuesta = models.IntegerField()
    fecha_creacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario} - Pregunta {self.id_pregunta}, Respuesta {self.id_respuesta}"

    class Meta:
        verbose_name_plural = "Encuestas"
