from rest_framework import serializers
from shopapp.models import *
from userapp.models import *



class shopOwnerRegisterSerializer(serializers.ModelSerializer):
    # Add your WorkshopOwner-specific fields here
    shopname = serializers.CharField(max_length=255, required=True)
    city = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=13, required=True)

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'password2','shopname', 'city', 'phone']
    
    def validate(self, valid):
        # Add your custom validation for WorkshopOwner registration
        password = valid.get('password')
        password2 = valid.get('password2')
        first_name = valid.get('first_name')
        last_name = valid.get('last_name')
        shopname = valid.get('shopname')
        city = valid.get('city')
        phone = valid.get('phone')

        if first_name == last_name:
            raise serializers.ValidationError('First name and last name can\'t be the same')

        if password != password2:
            raise serializers.ValidationError("Passwords didn't match")

        # Add more custom validation logic for WorkshopOwner registration if needed

        return valid
    
class EmailSerializer(serializers.Serializer):
    email=models.EmailField(max_length=100)


class ShopOwnerLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=100)
    class Meta:
        model = User
        fields =['email','password']