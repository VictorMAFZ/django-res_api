from django.urls import path
from .views import login, GetItinerarioAPIView, UpdateItinerarioAPIView, EstadisticaAPIView, EncuestaView, \
    ValidaEncuestaView

urlpatterns = [
    path('api/login/', login, name='login'),
    path('api/get_itinerario/', GetItinerarioAPIView.as_view(), name='get_itinerario'),
    path('api/update_itinerario/', UpdateItinerarioAPIView.as_view(), name='update_itinerario'),
    path('api/estadistica', EstadisticaAPIView.as_view(), name='estadistica'),
    path('api/encuesta/', EncuestaView.as_view(), name='encuesta'),
    path('api/valida_encuesta/', ValidaEncuestaView.as_view(), name='encuesta'),
]
