from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from .views import LoadGetCreate,LoadUpdateDelete,TrailerGetCreate,TrailerUpdateDelete,AccessPointGetCreate,AccessPointUpdateDelete,TripGetCreate,TripUpdateDelete
urlpatterns = [
    # path('',UserGetCreate.as_view()), 
    # path('users',UserGetCreate.as_view()), 
    # path('users/<int:pk>', UserUpdateDelete.as_view()),
    
    path('loads',LoadGetCreate.as_view()),
    path('loads/<int:pk>',LoadUpdateDelete.as_view()),

    path('trailers',TrailerGetCreate.as_view()),
    path('trailers/<int:pk>',TrailerUpdateDelete.as_view()),

    path('accesspoints',AccessPointGetCreate.as_view()),
    path('accesspoints/<int:pk>',AccessPointUpdateDelete.as_view()),

    path('trips',TripGetCreate.as_view()),
    path('trips/<int:pk>',TripUpdateDelete.as_view()),

]
