from rest_framework import serializers
from userapp.models import *
from userapp import google
from rest_framework.exceptions import AuthenticationFailed
from userapp.register import register_social_user




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
    
import os
from dotenv import load_dotenv

load_dotenv()

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )
        if user_data['aud'] != os.getenv('GOOGLE_CLIENT_ID'):
            raise AuthenticationFailed('oops, Who are you ?')
        
        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        

        return register_social_user(
             user_id=user_id, email=email, name=name)
        




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


class ProfileSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Profile
        fields = ['phone', 'city', 'pincode','usr_location']


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'profile']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        
        
        instance.save()
        
        profile_data = validated_data.pop('profile', [])
        if profile_data:
            # Get or create the profile instance
            profile_instance, created = Profile.objects.get_or_create(user=instance)
            
            # Update the profile fields
            for attr, value in profile_data.items():
                setattr(profile_instance, attr, value)
            
            profile_instance.save()

        return instance

