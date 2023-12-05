from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from .views import AssignDriverToFirstNullTrailer, LoadGetCreate,LoadUpdateDelete, TrailerAssignedToDriver,TrailerGetCreate, TrailersGetByDriverId,TrailersGetByOwnerId,TrailerUpdateDelete,AccessPointGetCreate,AccessPointUpdateDelete,TripGetCreate,TripUpdateDelete, AssignTripToTrailer, UpdateTripStatusToDE,UserGetCreate,UserUpdateDelete,UserGetByEmail, generateReport, TripsGetByTrailerId,TripsByTrailerStatusView
urlpatterns = [
    # path('',UserGetCreate.as_view()), 
     path('users',UserGetCreate.as_view()), 
    path('users/<int:pk>', UserUpdateDelete.as_view()),

    path('users/email/<str:email>', UserGetByEmail.as_view()),

    path('auth/',include('dj_rest_auth.urls')),
    path('auth/registration/',include('dj_rest_auth.registration.urls')),
    
    path('loads',LoadGetCreate.as_view()),
    path('loads/<int:pk>',LoadUpdateDelete.as_view()),

    path('trailers',TrailerGetCreate.as_view()),
    path('trailers/owner/<int:owner>/', TrailersGetByOwnerId.as_view()),
    path('trailers/driver/<int:driver>/', TrailersGetByDriverId.as_view()),
    path('trailers/<int:pk>',TrailerUpdateDelete.as_view()),

    path('assignTrailer',AssignDriverToFirstNullTrailer.as_view()),
    path('trailerAssigned/<int:driver_id>',TrailerAssignedToDriver.as_view()),

    path('accesspoints',AccessPointGetCreate.as_view()),
    path('accesspoints/<int:pk>',AccessPointUpdateDelete.as_view()),

    path('trips',TripGetCreate.as_view()),
    path('trips/<int:pk>',TripUpdateDelete.as_view()),
    path('trips/trailer/<int:trailer>',TripsGetByTrailerId.as_view()),
    path('trips/trailer/<int:trailer_id>/status/<str:status>/', TripsByTrailerStatusView.as_view(), name='trips-by-trailer-status'),

    path('trips/updateStatus/<int:trip_id>', UpdateTripStatusToDE.as_view(), name='update_trip_status_to_de'),


    path('trips/assignTrailer/<int:trip_id>', AssignTripToTrailer.as_view()),

    path('generate-report/', generateReport, name='generate_report'),


]
