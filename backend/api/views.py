from django.shortcuts import render
from rest_framework import generics
from .models import User,Trip,Load,Trailer,AccessPoint

from .serializers import LoadSerializer,TrailerSerializer,AccessPointSerializer,TripSerializer
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
