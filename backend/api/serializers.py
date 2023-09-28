from rest_framework import serializers
from .models import Trip,Load,Trailer,AccessPoint
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
class NewLoginSerializer(LoginSerializer):
    pass
class NewRegisterSerializer(RegisterSerializer):
    name=serializers.CharField(max_length=50)
    lastName=serializers.CharField(max_length=50)
    userType=serializers.CharField(max_length=2)
    phone=serializers.CharField(max_length=15)
    def custom_signup(self, request, user):
        user.name=request.data['name']
        user.last_name=request.data['lastName']
        user.userType=request.data['userType']
        user.phone=request.data['phone']
        user.save()
         
#implement business logic here
# class UserSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = User
#         fields = '__all__'

#     def validate_email(self,value):
#         user_id = self.instance.id if self.instance else None  # Exclude current user when updating
#         if User.objects.filter(email=value).exclude(id=user_id).exists():
#             raise serializers.ValidationError("Email already exists.")
#         return value

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