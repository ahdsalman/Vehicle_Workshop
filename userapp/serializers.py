from rest_framework import serializers
from userapp.models import *




class UserRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)

    class Meta:
        model= User
        fields=['first_name','last_name','username','email','password','password2']
        



    def validate(self,valid):
        password=valid.get('password')
        password2=valid.get('password2')
        fisrt_name=valid.get('first_name')
        last_name=valid.get('last_name')

        if fisrt_name==last_name:
            raise serializers.ValidationError('Fist_name and Last_name can\'t be same')
        if password != password2:
            raise serializers.ValidationError('Password didn\'t match')
        return valid
    


class PhoneSerializer(serializers.Serializer):
     phone = serializers.CharField()




class OtpSerializer(serializers.Serializer):
    otp = serializers.IntegerField()


class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=250)

    class Meta:
        model= User
        fields=['email','password']

class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField()
    new_password=serializers.CharField(max_length=100,required=True)
    confirm_password=serializers.CharField(max_length=100,required=True)
    
class ForgotpasswordSerializer(serializers.Serializer):
    update_password=serializers.CharField(max_length=100)
    sure_password=serializers.CharField(max_length=100)