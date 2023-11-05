from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from .views import LoadGetCreate,LoadUpdateDelete,TrailerGetCreate,TrailersGetByOwnerId,TrailerUpdateDelete,AccessPointGetCreate,AccessPointUpdateDelete,TripGetCreate,TripUpdateDelete, AssignTripTrailer,UserGetCreate,UserUpdateDelete,UserGetByEmail, generateReport, TripsGetByTrailerId
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
    path('trailers/<int:pk>',TrailerUpdateDelete.as_view()),

    path('accesspoints',AccessPointGetCreate.as_view()),
    path('accesspoints/<int:pk>',AccessPointUpdateDelete.as_view()),

    path('trips',TripGetCreate.as_view()),
    path('trips/<int:pk>',TripUpdateDelete.as_view()),
    path('trips/trailer/<int:trailer>',TripsGetByTrailerId.as_view()),

    path('assign-trailer/<int:trip_id>/', AssignTripTrailer.as_view()),

    path('generate-report/', generateReport, name='generate_report'),


]
