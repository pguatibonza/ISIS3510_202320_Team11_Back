from rest_framework import serializers
from .models.trip import Trip
from .models.user import User
from .models.load import Load
from .models.trailer import Trailer
from .models.accespoint import AccessPoint
#implement business logic here
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'

    def validate_email(self,value):
        user_id = self.instance.id if self.instance else None  # Exclude current user when updating
        if User.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

class LoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Load
        fields = '__all__'
    def validate_weight(self,value):
        if value <=0:
            raise serializers.ValidationError("Weight must be positive.")
        return value
    def validate_volume(self,value):
        if value!= None and value <=0:
            raise serializers.ValidationError("Volume must be positive.")
        return value
    
class TrailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trailer
        fields = '__all__'

    def validate_capacity(self,value):
        if value < 0:
            raise serializers.ValidationError("Capacity must be positive.")
        return value
    def validate_volume(self,value):
        if value!=None and value < 0:
            raise serializers.ValidationError("Volume must be positive.")
        return value
    
class AccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
        fields = '__all__'

    def validate(self,data):
        print(data)
        before=data.get('before')

        after=data.get('after')
        if before and after and before<after:
            raise serializers.ValidationError("Date before must be after date after.")
        return data
        
class TripSerializer(serializers.ModelSerializer):
    class Meta:    
        model = Trip
        fields = '__all__'

    def validate_loadOwner(self,value):

        if value.userType != 'LO':
            raise serializers.ValidationError("User must be LoadOwner.")
        return value 