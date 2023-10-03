from django.shortcuts import render
from rest_framework import generics
from .models import User,Trip,Load,Trailer,AccessPoint
from rest_framework.response import Response
from rest_framework import status


from .serializers import LoadSerializer,TrailerSerializer,AccessPointSerializer,TripSerializer,AssignTripTrailerSerializer
# Create your views here.
# GET POST UPDATE DELETE
# class UserGetCreate(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
# class UserUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


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

