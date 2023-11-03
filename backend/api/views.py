from django.shortcuts import render
from rest_framework import generics
from .models import User,Trip,Load,Trailer,AccessPoint
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime





from .serializers import LoadSerializer,TrailerSerializer,AccessPointSerializer,TripSerializer,AssignTripTrailerSerializer,UserSerializer
# Create your views here.
# GET POST UPDATE DELETE
class UserGetCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
class UserUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserGetByEmail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'email'  # Use email as the lookup field

    
class LoadGetCreate(generics.ListCreateAPIView):
    queryset = Load.objects.all()
    serializer_class = LoadSerializer
class LoadUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Load.objects.all()
    serializer_class = LoadSerializer


class TrailerGetCreate(generics.ListCreateAPIView):
    queryset = Trailer.objects.all()
    serializer_class = TrailerSerializer
class TrailerUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trailer.objects.all()
    serializer_class = TrailerSerializer
class TrailersGetByOwnerId(generics.ListAPIView):
    serializer_class = TrailerSerializer
    lookup_field = 'owner'
    
    def get_queryset(self):
        owner_id = self.kwargs['owner']
        return Trailer.objects.filter(owner=owner_id)

class AccessPointGetCreate(generics.ListCreateAPIView):
    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer
class AccessPointUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer


class TripGetCreate(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class TripUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class AssignTripTrailer(generics.UpdateAPIView):
    queryset = Trip.objects.all()
    serializer_class = AssignTripTrailerSerializer
    lookup_url_kwarg = 'trip_id'

    def update(self, request, *args, **kwargs):
        trip = self.get_object()
        serializer = AssignTripTrailerSerializer(data=request.data)
        if serializer.is_valid():
            # Valid trailer_id from the serializer
            trailer_id = serializer.validated_data['trailer_id']

            try:
                # Check if the trailer exists
                trailer = Trailer.objects.get(pk=trailer_id)
            except Trailer.DoesNotExist:
                return Response({'detail': 'Trailer not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Assign the trailer to the trip
            trip.trailer = trailer
            trip.save()

            #Changes Trailer status
            trailer.status = Trailer.TrailerStatus.INTRANSIT
            trailer.save()

            return Response({'detail': f'Trailer {trailer_id} assigned to trip {trip.id}.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
def generateReport(req):
    print("Generating report...")

    load_types_data = Load.objects.values('type') \
        .annotate(load_type_count=Count('type')) \
        .order_by('-load_type_count')[:3]  # Get the top 3 most common types

    # Query the Trailer model to get the most common Trailer types
    trailer_types_data = Trailer.objects.values('type') \
        .annotate(trailer_type_count=Count('type')) \
        .order_by('-trailer_type_count')[:3]  # Get the top 3 most common types

    # Query the AccessPoint model to get the top 3 used cities
    access_point_cities_data = AccessPoint.objects.values('city') \
        .annotate(city_count=Count('city')) \
        .order_by('-city_count')[:3]  # Get the top 3 most used cities

    # Query the Trip model to get the top 3 routes
    trip_routes_data = Trip.objects.values('pickup__city', 'dropoff__city') \
        .annotate(route_count=Count('*')) \
        .order_by('-route_count')[:3]  # Get the top 3 routes by pickup and dropoff cities

    # Serialize the data into a JSON object
    report_data = {
        'most_common_load_types': [
            {
                'type': item['type'],
                'count': item['load_type_count']
            }
            for item in load_types_data
        ],
        'most_common_trailer_types': [
            {
                'type': item['type'],
                'count': item['trailer_type_count']
            }
            for item in trailer_types_data
        ],
        'top_used_cities': [
            {
                'city': item['city'],
                'count': item['city_count']
            }
            for item in access_point_cities_data
        ],
        'top_trip_routes': [
            {
                'pickup_city': item['pickup__city'],
                'dropoff_city': item['dropoff__city'],
                'count': item['route_count']
            }
            for item in trip_routes_data
        ]
    }
    # Generar strings para los top load types
    top_load_types = "\n".join([f"El tipo de carga {item['type']} aparece {item['count']} veces" for item in report_data['most_common_load_types']])

    # Generar strings para los top trailer types
    top_trailer_types = "\n".join([f"El tipo de camión {item['type']}, aparece {item['count']} veces" for item in report_data['most_common_trailer_types']])

    # Generar strings para las top ciudades
    top_cities = "\n".join([f"La ciudad {item['city']} ha sido destino u origen {item['count']} veces" for item in report_data['top_used_cities']])

    # Generar strings para las top trip routes
    top_trip_routes = "\n".join([f"La ruta de {item['pickup_city']} a {item['dropoff_city']} se ha realizado {item['count']} veces" for item in report_data['top_trip_routes']])

    # Generar el string completo para el reporte
    report_string = f"**Top Load Types:**\n{top_load_types}\n\n**Top Trailer Types:**\n{top_trailer_types}\n\n**Top Cities:**\n{top_cities}\n\n**Top Trip Routes:**\n{top_trip_routes}"

    send_email_alert(report_string)

    print("Email with report sent!")
    response = JsonResponse(report_data, status=200)
    
    return response



def send_email_alert(report_string):
    recipients = ['juanddiaz13@gmail.com']  # Lista de destinatarios

    for recipient in recipients:
        msg = MIMEMultipart()
        password = "xyqe sfyk wezi eusn"
        msg['From'] = "juanddiaz13@gmail.com"
        msg['Subject'] = f"Analytics Engine Report - {datetime.now().strftime('%Y-%m-%d')}"
        msg['To'] = recipient

        # Adjuntar la cadena decodificada al correo electrónico
        msg.attach(MIMEText(report_string))

        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

