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

class TrailersGetByDriverId(generics.ListAPIView):
    serializer_class = TrailerSerializer
    lookup_field = 'driver'
    
    def get_queryset(self):
        driver_id= self.kwargs['driver']
        return Trailer.objects.filter(driver=driver_id)

class AssignDriverToFirstNullTrailer(generics.UpdateAPIView):
    serializer_class = TrailerSerializer

    def update(self, request, *args, **kwargs):
        # Assuming 'user_id' is passed in the request data
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the first trailer with a null driver
        trailer = Trailer.objects.filter(driver__isnull=True).first()

        if trailer is not None:
            trailer.driver = user
            trailer.status = 'AV'
            trailer.save()

            serializer = self.get_serializer(trailer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No trailer available for assignment.'}, status=status.HTTP_404_NOT_FOUND)


class TrailerAssignedToDriver(generics.RetrieveAPIView):
    serializer_class = TrailerSerializer

    def get(self, request, *args, **kwargs):
        driver_id = self.kwargs.get('driver_id')

        try:
            user = User.objects.get(id=driver_id)
        except User.DoesNotExist:
            return Response({'detail': 'Driver not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve the trailer assigned to the driver
            trailer = Trailer.objects.get(driver=user)
            serializer = self.get_serializer(trailer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Trailer.DoesNotExist:
            return Response({'detail': 'No trailer assigned to the driver.'}, status=status.HTTP_404_NOT_FOUND)

class UpdateTripStatusToDE(APIView):
    def put(self, request, trip_id, format=None):
        try:
            # Get the trip instance
            trip = Trip.objects.get(id=trip_id)

            # Update the status to 'DE'
            trip.status = 'DE'
            trip.save()

            trailer=trip.trailer
            trailer.status='AV'
            trailer.save()

            # Serialize the updated trip data
            serializer = TripSerializer(trip)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error updating trip status to DE: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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

class AssignTripToTrailer(APIView):
    def get(self, request, trip_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

        # Find the first available trailer with a driver
        available_trailer = Trailer.objects.filter(status=Trailer.TrailerStatus.AVAILABLE, driver__isnull=False).first()

        if not available_trailer:
            return Response({"error": "No available trailer with a driver found"}, status=status.HTTP_400_BAD_REQUEST)

        # Assign the trip to the available trailer
        trip.trailer = available_trailer
        trip.status = Trip.Status.INPROGESS
        trip.save()

        # Update the status of the trailer to Unavailable
        available_trailer.status = Trailer.TrailerStatus.INTRANSIT
        available_trailer.save()

        return Response({"message": "Trip assigned successfully"}, status=status.HTTP_200_OK)


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
    
def getTopDropoffPlaces():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            trip_routes_data = Trip.objects.values('dropoff__city') \
                .annotate(route_count=Count('*')) \
                .order_by('-route_count')[:3]  # Get the top 3 routes by pickup and dropoff cities
            return [
                {
                    'dropoff__city': item['dropoff__city'],
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

def getTopPickupPlaces():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            trip_routes_data = Trip.objects.values('pickup__city') \
                .annotate(route_count=Count('*')) \
                .order_by('-route_count')[:3]  # Get the top 3 routes by pickup and dropoff cities
            return [
                {
                    'pickup__city': item['pickup__city'],
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
            

def getInactiveUsersAfterOneMonth():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            # Calculate the date 29 to 31 days ago
            threshold_date = timezone.now() - timezone.timedelta(days=31)

            # Query the User model to get inactive users
            inactive_users_data = User.objects.filter(last_login__range=[threshold_date, timezone.now() - timezone.timedelta(days=20)]) \
                .values('email', 'name')

            # You can perform additional processing on inactive_users_data if needed
            return list(inactive_users_data)
        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return []  # Return empty list or handle as needed

def trips_by_trailer_id():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            trailer_trip_data = Trip.objects.values('trailer_id') \
                .annotate(trip_count=Count('*')) \
                .order_by('-trip_count')  # Get the count of trips for each trailer_id
            return [
                {
                    'trailer_id': item['trailer_id'],
                    'trip_count': item['trip_count']
                }
                for item in trailer_trip_data
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

from django.db.models import Sum, F

def camiones_con_cargas_pesadas():
    retry_attempts = 3  # Número de intentos de reintento
    for intento in range(retry_attempts):
        try:
            camiones_cargas_pesadas = Trip.objects.filter(
                load__weight__gt=1200
            ).values('trailer_id').annotate(
                total_carga=Sum(F('load__weight'))
            ).order_by('-total_carga')  # Obtén el total de carga para cada trailer_id
            return [
                {
                    'trailer_id': item['trailer_id'],
                    'total_carga': item['total_carga']
                }
                for item in camiones_cargas_pesadas
            ]
        except OperationalError as e:
            print(f"Falla en la consulta de la base de datos. Reintentando... Intento {intento + 1}")
            if intento < retry_attempts - 1:
                time.sleep(5)  # Espera antes de reintentar
            else:
                # Registra el error o maneja el fallo después de todos los intentos
                print("Todos los intentos fallaron. La base de datos no está actualmente disponible.")
                # Considera lanzar una excepción o registrar el fallo
                return []  # Devuelve una lista vacía o maneja según sea necesario

def getMostCommonTripStatus():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            trip_status_data = Trip.objects.values('status') \
                .annotate(trip_status_count=Count('status')) \
                .order_by('-trip_status_count').first()  # Get the most common status
            
            if trip_status_data:
                return {
                    'status': trip_status_data['status'],
                    'count': trip_status_data['trip_status_count']
                }
            else:
                # Handle the case where no data is found
                return None

        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return None
most_common_status = getMostCommonTripStatus()

def getMostCommonTrailerStatus():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            trailer_status_data = Trailer.objects.values('status') \
                .annotate(trailer_status_count=Count('status')) \
                .order_by('-trailer_status_count').first()  # Get the most common status
            
            if trailer_status_data:
                return {
                    'status': trailer_status_data['status'],
                    'count': trailer_status_data['trailer_status_count']
                }
            else:
                # Handle the case where no data is found
                return None

        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return None
most_common_status_trailer = getMostCommonTrailerStatus()

def getMostCommonUserType():
    retry_attempts = 3  # Number of retry attempts
    for attempt in range(retry_attempts):
        try:
            user_type_data = User.objects.values('userType') \
                .annotate(user_type_count=Count('userType')) \
                .order_by('-user_type_count').first()  #
            
            if user_type_data:
                return {
                    'userType': user_type_data['userType'],
                    'count': user_type_data['user_type_count']
                }
            else:
                # Handle the case where no data is found
                return None

        except OperationalError as e:
            print(f"Database query failed. Retrying... Attempt {attempt + 1}")
            if attempt < retry_attempts - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # Log error or handle failure after all attempts
                print("All attempts failed. Database is currently unreachable.")
                # Consider raising an exception or logging the failure
                return None
most_common_typeuser = getMostCommonUserType()

def generateReport(req):
    start_time = time.time()
    print("Generating report...")
    # Serialize the data into a JSON object
    report_data = {
        'most_common_load_types': getTop3MostCommonLoadTypes(),
        'most_common_trailer_types': getTop3MostCommonTrailerTypes(),
        'top_used_cities': getTopUsedCities(),
        'top_trip_routes': getTop3RoutesByPickupAndDropoff(),
        'top_dropoff_cities': getTopDropoffPlaces(),
        'top_pickup_cities': getTopPickupPlaces(),
        'one_month_inactive': getInactiveUsersAfterOneMonth(),
        'trips_by_trailer': trips_by_trailer_id(),
        'heaviest_loads': camiones_con_cargas_pesadas(),
        'most_common_trip_status': getMostCommonTripStatus(),
        'most_common_trailer_status': getMostCommonTrailerStatus(),
        'most_common_type_user': getMostCommonUserType()
    }
    print(report_data['heaviest_loads'])
    # Generar strings para los top load types
    top_load_types = "\n".join([f"El tipo de carga {item['type']} aparece {item['count']} veces" for item in report_data['most_common_load_types']])

    # Generar strings para los top trailer types
    top_trailer_types = "\n".join([f"El tipo de camión {item['type']}, aparece {item['count']} veces" for item in report_data['most_common_trailer_types']])

    # Generar strings para las top ciudades
    top_cities = "\n".join([f"La ciudad {item['city']} ha sido destino u origen {item['count']} veces" for item in report_data['top_used_cities']])

    # Generar strings para las top trip routes
    top_trip_routes = "\n".join([f"La ruta de {item['pickup_city']} a {item['dropoff_city']} se ha realizado {item['count']} veces" for item in report_data['top_trip_routes']])

    #Generar strings para las top dropff
    top_dropoff_cities = "\n".join([f"El dropoff en {item['dropoff__city']}, aparece {item['count']} veces" for item in report_data['top_dropoff_cities']])

    #Generar strings para las top pickup
    top_pickup_cities = "\n".join([f"El pickup en {item['pickup__city']}, aparece {item['count']} veces" for item in report_data['top_pickup_cities']])
   
    #Generar strings para los inactivos
    inactivos = "\n".join([f"El usuario {item['name']} con correo {item['email']} lleva 1 mes sin ingresar a la app" for item in report_data['one_month_inactive']])
    
    #Generar strings para los más pesados
    trips_by_trailer = "\n".join([f"El camion {item['trailer_id']} ha realizado {item['trip_count']} viajes" for item in report_data['trips_by_trailer']])
    
    #Generar strings para los más pesados
    heaviest_loads = "\n".join([f"El camion {item['trailer_id']} ha llevado {item['total_carga']} kilogramos en sus viajes" for item in report_data['heaviest_loads']])
    
    #Generar strings para el top status trip
    most_common_trip_status = "\n".join([f"El estado más común de los viajes es '{most_common_status['status']}' con {most_common_status['count']} ocurrencias."])

    #Generar strings para el top status trailer
    most_common_trailer_status = "\n".join([f"El estado más común de los camiones es '{most_common_status_trailer['status']}' con {most_common_status_trailer['count']} ocurrencias."])

    #Generar strings para el top type user
    most_common_type_user = "\n".join([f"El tipo más común de los usuarios es '{most_common_typeuser['userType']}' con {most_common_typeuser['count']} ocurrencias."])


    # Generar el string completo para el reporte
    report_string = f"**Top Load Types:**\n{top_load_types}\n\n**Top Trailer Types:**\n{top_trailer_types}\n\n**Top Cities:**\n{top_cities}\n\n**Top Trip Routes:**\n{top_trip_routes} \n\n**Top Dropoff Places:**\n{top_dropoff_cities} \n\n**Top Pickup Places:**\n{top_pickup_cities} \n\n**Inactivos:**\n{inactivos} \n\n**Viajes por camión:**\n{trips_by_trailer} \n\n**Camiones que han cargado más:**\n{heaviest_loads} \n\n**Estado más común actualmente de los viajes:**\n{most_common_trip_status} \n\n**Estado más común actualmente de los camiones:**\n{most_common_trailer_status} \n\n**Tipo más común actualmente de los usuarios:**\n{most_common_type_user}"

    send_email_alert(report_string)

    response = JsonResponse(report_data, status=200)
    end_time = time.time()
    execution_time = int((end_time - start_time) * 1000)
    ExecutionTime.objects.create(function="generate-report-function", duration=execution_time)

    return response
    

def send_email_alert(report_string):
    recipients = ['juanddiaz13@gmail.com', 'laisamagal@gmail.com']  # List of recipients

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

