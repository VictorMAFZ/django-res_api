from django.http import JsonResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from .serializers import UsuarioSerializer, UsuIteSerializer, UpdUsuIteSerializer, \
    EstadisticaSerializer, EncuestaSerializer
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Usuario, Usu_ite, Itinerario, Encuesta
from django.db.models import Max, Min, Count, Sum, F, FloatField

@api_view(['POST'])
def login(request):
    # Obtiene los valores de usuario y contraseña de la petición
    usuario = request.data.get('usuario')
    password = request.data.get('password')

    try:
        # Busca en la tabla Usuario un objeto con el usuario y contraseña recibidos
        usuario_obj = Usuario.objects.get(usuario__iexact=usuario.lower(), password=password)
        # Crea un objeto serializer a partir del objeto encontrado
        serializer = UsuarioSerializer(usuario_obj)
        # Retorna una respuesta con los datos serializados
        return Response(serializer.data)
    except Usuario.DoesNotExist:
        # Si el objeto no existe, retorna una respuesta con un mensaje de error
        return Response({'error': 'Usuario o contraseña incorrectos.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data, status=status.HTTP_200_OK)


class GetItinerarioAPIView(APIView):

    def post(self, request):
        usuario = request.data.get('usuario')
        if usuario is None:
            return Response({'error': 'No se proporcionó el usuario'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario_obj = Usuario.objects.get(usuario=usuario)
            activo = usuario_obj.activo

            if activo:
                # El usuario ya existe en Usu_ite, se recuperan sus itinerarios ordenados por nombre
                usu_ite_obj = Usu_ite.objects.filter(usuario=usuario_obj).order_by('itinerario_id')
                serializer = UsuIteSerializer(usu_ite_obj, many=True)
            else:
                # Es el primer inicio de sesión, se crea una entrada en Usu_ite para cada itinerario
                itinerarios = Itinerario.objects.all()
                for itinerario in itinerarios:
                    usu_ite = Usu_ite(usuario=usuario_obj, itinerario=itinerario, fecha_create=timezone.now())
                    usu_ite.save()
                usuario_obj.activo = True  # se establece el valor del campo "activo" a True
                usuario_obj.save()
                # Recupera las instancias de Usu_ite correspondientes a ese usuario en particular y serialízalas
                usu_ite_obj = Usu_ite.objects.filter(usuario=usuario_obj).order_by('itinerario_id')
                serializer = UsuIteSerializer(usu_ite_obj, many=True)

            # Calcular el porcentaje de itinerarios activos
            itinerarios_activos = Usu_ite.objects.filter(usuario=usuario_obj, activo=True).count()
            total_itinerarios = Usu_ite.objects.filter(usuario=usuario_obj).count()
            avance = round(itinerarios_activos / total_itinerarios * 100, 2)

            # Agregar el porcentaje de itinerarios activos a la respuesta
            response_data = {
                'avance': avance,
                'itinerarios': serializer.data
            }

        except Usuario.DoesNotExist:
            return Response({'error': 'El usuario no existe'}, status=status.HTTP_404_NOT_FOUND)

        return Response(response_data, status=status.HTTP_200_OK)


class UpdateItinerarioAPIView(APIView):
    serializer_class = UpdUsuIteSerializer

    def post(self, request):
        # Obtener el usuario y los itinerarios a actualizar del cuerpo de la petición
        usuario = request.data.get('usuario')
        itinerarios = request.data.get('itinerarios')

        # Si alguno de los datos requeridos no fue proporcionado, retornar un error 400
        if not usuario or not itinerarios:
            return Response({'error': 'Se deben proporcionar usuario e itinerarios'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Buscar el objeto de usuario correspondiente al email proporcionado
        try:
            usuario_obj = Usuario.objects.get(usuario=usuario)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Crear un diccionario para almacenar el resultado de la actualización
        result = {}

        # Actualizar el estado de cada itinerario proporcionado para este usuario
        for itinerario in itinerarios:
            itinerario_id = itinerario.get('id')
            activo = itinerario.get('activo')

            # Buscar el objeto Usu_ite correspondiente a este usuario y itinerario
            try:
                usu_ite_obj = Usu_ite.objects.get(usuario=usuario_obj, itinerario__id=itinerario_id)

                # Actualizar el estado del itinerario y guardar el objeto si activo es False
                if not usu_ite_obj.activo and activo:
                    usu_ite_obj.activo = activo
                    usu_ite_obj.fecha_update = timezone.now()
                    usu_ite_obj.dif_fecha = usu_ite_obj.fecha_update - usu_ite_obj.fecha_create
                    usu_ite_obj.save()

                    # Agregar el resultado de la actualización al diccionario de resultados
                    result[itinerario_id] = {'mensaje': f'Itinerario {itinerario_id} actualizado correctamente'}

            # Si el objeto no existe, agregar un mensaje de error al diccionario de resultados
            except Usu_ite.DoesNotExist:
                result[itinerario_id] = {'error': f'Usu_ite para usuario {usuario} e itinerario {itinerario_id} no encontrado'}

        # Si todo se hizo correctamente, retornar un mensaje de éxito 200 y el diccionario de resultados
        return Response({'mensaje': 'Itinerarios actualizados correctamente', 'resultados': result}, status=status.HTTP_200_OK)


class EstadisticaAPIView(APIView):
    def get(self, request):
        # Obtener todos los registros de Usu_ite
        usu_itens = Usu_ite.objects.all()

        # Obtener una lista de usuarios únicos en Usu_ite
        usuarios = Usuario.objects.filter(usu_ites__in=usu_itens).distinct()

        # Inicializar una lista para almacenar los resultados
        resultados = []

        # Iterar sobre cada usuario para obtener los resultados de la estadística
        for usuario in usuarios:
            # Obtener todos los registros de Usu_ite que corresponden al usuario
            usu_itens_usuario = usu_itens.filter(usuario=usuario)

            # Encontrar la fecha más reciente de fecha_update
            fecha_update_max = usu_itens_usuario.aggregate(Max('fecha_update'))['fecha_update__max']

            # Encontrar la fecha más temprana de fecha_create
            fecha_create_min = usu_itens_usuario.aggregate(Min('fecha_create'))['fecha_create__min']

            # Calcular el tiempo transcurrido entre las fechas más reciente y temprana
            if fecha_update_max:
                tiempo_final = str(fecha_update_max - fecha_create_min)
            else:
                tiempo_final = None

            # Calcular el tiempo total de dif_fecha para el usuario
            tiempo_total = usu_itens_usuario.aggregate(Sum('dif_fecha'))['dif_fecha__sum']
            if tiempo_total:
                tiempo_total = str(tiempo_total)
            else:
                tiempo_total = None

            # Calcular el porcentaje de itinerarios activos en relación al total de itinerarios para el usuario
            num_itinerarios = usu_itens_usuario.count()
            num_itinerarios_activos = usu_itens_usuario.filter(activo=True).count()
            avance = round(num_itinerarios_activos / num_itinerarios * 100, 2) if num_itinerarios else None

            # Agregar los resultados a la lista de resultados
            resultados.append({
                'usuario': usuario.usuario,
                'nombre': usuario.nombre,
                'tiempo_final': tiempo_final,
                'tiempo_total': tiempo_total,
                'avance': avance,
            })
        # Ordenar la lista de resultados por avance (descendente) y tiempo_final (ascendente)
        resultados = sorted(resultados, key=lambda x: (-x['avance'], x['tiempo_final'] or ''))

        # Usar el serializador para convertir los resultados a JSON
        serializer = EstadisticaSerializer(resultados, many=True)
        return Response(serializer.data)


class EncuestaView(APIView):
    def post(self, request):
        usuario = request.data.get('usuario')
        encuesta_data = request.data.get('encuesta')

        # Si el valor de encuesta_data es un diccionario, lo convertimos a una lista
        if isinstance(encuesta_data, dict):
            encuesta_data = [encuesta_data]

        # Creamos una lista vacía para almacenar los ids de las encuestas creadas
        encuesta_ids = []

        for encuesta in encuesta_data:
            encuesta_serializer = EncuestaSerializer(data=encuesta)

            if encuesta_serializer.is_valid():
                encuesta_obj = encuesta_serializer.save(usuario=usuario, fecha_creacion=timezone.now())  # agregamos la fecha de creación y pasamos el usuario
                encuesta_ids.append(encuesta_obj.id)
            else:
                return Response(encuesta_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'encuesta_ids': encuesta_ids, 'message': 'La encuesta fue registrada correctamente.'}, status=status.HTTP_200_OK)


class ValidaEncuestaView(APIView):
    def post(self, request):
        usuario = request.data.get('usuario')

        if not usuario:
            return Response({'error': 'El usuario no fue proporcionado.'}, status=status.HTTP_400_BAD_REQUEST)

        encuesta_exists = Encuesta.objects.filter(usuario=usuario).exists()

        if encuesta_exists:
            return Response({'valido': 1, 'mensaje': 'La encuesta ya está respondida.'}, status=status.HTTP_200_OK)
        else:
            return Response({'valido': 0, 'mensaje': 'Puede responder la encuesta.'}, status=status.HTTP_200_OK)
