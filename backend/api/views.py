from django.shortcuts import render
from rest_framework import generics
from .models import User,Trip,Load,Trailer,AccessPoint,ExecutionTime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from django.db import OperationalError
import time

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

class TripsByTrailerStatusView(APIView):
    def get(self, request, trailer_id, status):
        trips = Trip.objects.filter(trailer=trailer_id, status=status)
        if trips.exists():
            serializer = TripSerializer(trips, many=True)
            return Response(serializer.data)
        else:
            return Response([], status=status.HTTP_404_NOT_FOUND)

class TripsGetByTrailerId(generics.ListAPIView):
    serializer_class = TripSerializer
    lookup_field = 'trailer'
    
    def get_queryset(self):
        trailer_id = self.kwargs['trailer']
        return Trip.objects.filter(trailer=trailer_id)

class TripUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class AssignTripTrailer(generics.UpdateAPIView):
    queryset = Trip.objects.all()
    serializer_class = AssignTripTrailerSerializer
    lookup_url_kwarg = 'trip_id'

    def update(self, request, *args, **kwargs):
        start_time = time.time()
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

            end_time = time.time()
            execution_time = int((end_time - start_time) * 1000)
            ExecutionTime.objects.create(function="update-triptrailer-function", duration=execution_time)

            return Response({'detail': f'Trailer {trailer_id} assigned to trip {trip.id}.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
def getTop3MostCommonLoadTypes():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            load_types_data = Load.objects.values('type') \
                .annotate(load_type_count=Count('type')) \
                .order_by('-load_type_count')[:3]  # Get the top 3 most common types
            return [
                {
                    'type': item['type'],
                    'count': item['load_type_count']
                }
                for item in load_types_data
            ]
        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return []  # Return empty list or handle as needed

def getTop3MostCommonTrailerTypes():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            trailer_types_data = Trailer.objects.values('type') \
                .annotate(trailer_type_count=Count('type')) \
                .order_by('-trailer_type_count')[:3]  # Get the top 3 most common types
            return [
                {
                    'type': item['type'],
                    'count': item['trailer_type_count']
                }
                for item in trailer_types_data
            ]
        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return []  # Return empty list or handle as needed
    
def getTopUsedCities():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            access_point_cities_data = AccessPoint.objects.values('city') \
                .annotate(city_count=Count('city')) \
                .order_by('-city_count')[:3]  # Get the top 3 most used cities
            return [
                {
                    'city': item['city'],
                    'count': item['city_count']
                }
                for item in access_point_cities_data
            ]
        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return []  # Return empty list or handle as needed

def getTop3RoutesByPickupAndDropoff():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            trip_routes_data = Trip.objects.values('pickup__city', 'dropoff__city') \
                .annotate(route_count=Count('*')) \
                .order_by('-route_count')[:3]  # Get the top 3 routes by pickup and dropoff cities
            return [
                {
                    'pickup_city': item['pickup__city'],
                    'dropoff_city': item['dropoff__city'],
                    'count': item['route_count']
                }
                for item in trip_routes_data
            ]
        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return []  # Return empty list or handle as needed

        
def generateReport(req):
    start_time = time.time()
    print("Generating report...")

    # Serialize the data into a JSON object
    report_data = {
        'most_common_load_types': getTop3MostCommonLoadTypes(),
        'most_common_trailer_types': getTop3MostCommonTrailerTypes(),
        'top_used_cities': getTopUsedCities(),
        'top_trip_routes': getTop3RoutesByPickupAndDropoff()
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

    response = JsonResponse(report_data, status=200)
    end_time = time.time()
    execution_time = int((end_time - start_time) * 1000)
    ExecutionTime.objects.create(function="generate-report-function", duration=execution_time)

    return response


def send_email_alert(report_string):
    recipients = ['juanddiaz13@gmail.com']  # List of recipients

    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            for recipient in recipients:
                msg = MIMEMultipart()
                password = "xyqe sfyk wezi eusn"
                msg['From'] = "juanddiaz13@gmail.com"
                msg['Subject'] = f"Analytics Engine Report - {datetime.now().strftime('%Y-%m-%d')}"
                msg['To'] = recipient

                # Attach the decoded string to the email
                msg.attach(MIMEText(report_string))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(msg['From'], password)
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                server.quit()

            print("Email with report sent!")
            break  # Break out of the retry loop upon successful email sending

        except smtplib.SMTPException as e:
            print(f"Email sending failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Email couldn't be sent.")
                # Consider raising an exception or logging the failure
                break  # Break out of the retry loop after all attempts

