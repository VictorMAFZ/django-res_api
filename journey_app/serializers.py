from rest_framework import serializers
from .models import Usuario, Itinerario, Usu_ite, Encuesta
from django.utils import timezone


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['usuario', 'password', 'nombre']


class ItinerarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerario
        fields = '__all__'


class UsuIteSerializer(serializers.ModelSerializer):
    nombre = serializers.ReadOnlyField(source='itinerario.nombre')

    class Meta:
        model = Usu_ite
        fields = ['itinerario', 'nombre', 'activo']


class ItinerarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Itinerario
        fields = ['id', 'nombre', 'activo']


class UpdUsuIteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    activo = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.activo = validated_data.get('activo', instance.activo)
        instance.fecha_update = timezone.now()
        diff = instance.fecha_update - instance.fecha_create
        instance.dif_fecha = diff.total_seconds()
        instance.save()
        return instance


class EstadisticaSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    nombre = serializers.CharField()
    tiempo_final = serializers.CharField()
    tiempo_total = serializers.CharField()
    avance = serializers.DecimalField(max_digits=5, decimal_places=2)


class EncuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encuesta
        fields = ['id_pregunta', 'id_respuesta']

    def save(self, usuario, **kwargs):
        encuesta = Encuesta.objects.create(usuario=usuario, fecha_creacion=kwargs.get('fecha_creacion', None), **self.validated_data)
        return encuesta


class ValidaEncuestaSerializer(serializers.Serializer):
    valido = serializers.IntegerField()
    mensaje = serializers.CharField(max_length=100)
