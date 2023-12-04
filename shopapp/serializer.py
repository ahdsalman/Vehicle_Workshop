from rest_framework import serializers
from userapp.models import *
from shopdetails.models import *



class ShopRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model= User
        fields=['first_name','last_name','username','email','password','password2']

        # category = serializers.ChoiceField(choices=WorkshopOwner.CATEGORY_CHOICES)
    # Add your WorkshopOwner-specific fields here
    
        # Add more custom validation logic for WorkshopOwner registration if needed

        
    
class EmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)

class OtpVerifySerializer(serializers.Serializer):
    entered_otp=serializers.CharField()
    


class OwnerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.save()
        return instance




    




