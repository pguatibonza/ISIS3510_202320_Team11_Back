from rest_framework import serializers
from  .models import User,Load,Trailer,AccessPoint,Trip

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
class LoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Load
        fields = '__all__'
class TrailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trailer
        fields = '__all__'
class AccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
        fields = '__all__'
class TripSerializer(serializers.ModelSerializer):
    class Meta:    
        model = Trip
        fields = '__all__'
