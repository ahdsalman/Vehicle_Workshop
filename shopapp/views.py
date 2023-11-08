from django.shortcuts import render
from shopapp.models import WorkshopOwner
from userapp.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from shopapp.serializer import *
from userapp.serializers import ChangePasswordSerializer,ForgotpasswordSerializer,UserLoginSerializer
from rest_framework import status
from userapp.auths.smtp import verify_mail
from userapp.auths.tokens import get_tokens_for_user
from django.conf import settings
import random
import math
from threading import Thread
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
# Create your views here.

class WorkshopOwnerRegister(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ShopOwnerRegisterSerializer
    @extend_schema(responses=ShopOwnerRegisterSerializer)

    def post(self, request):
        
        serializer = ShopOwnerRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            workshop_owner = WorkshopOwner.objects.get(user=user)

            workshop_owner.shopname=serializer.validated_data.get('shopname')
            workshop_owner.city=serializer.validated_data.get('city')
            workshop_owner.phone=serializer.validated_data.get('phone')
            user.is_shopowner = True
            user.save()
            workshop_owner.save()
            
            return Response({'Msg': 'Enter your Email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EmailVerify(APIView):
    serializer_class=EmailSerializer
    @extend_schema(responses=EmailSerializer)
    def post(self, request):

        serializer=EmailSerializer(data=request.data)
        if serializer.is_valid():
            email=request.data.get('email')

            otp = math.floor(random.randint(100000, 999999))
            
            subject = "Your OTP for Email Verification"
            message = f"Your OTP is:{otp}"

            sender = settings.EMAIL_HOST_USER
            recipient_list = [email]
            verify_mail(subject, message, sender, recipient_list)

            response_data={
                'email':email,
                'otp':otp
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailOtpVerify(APIView):
    serializer_class=EmailSerializer
    @extend_schema(responses=EmailSerializer)
    def post(self, request):
        serializer=EmailSerializer(data=request.data)
        if serializer.is_valid():
            email=serializer.validated_data.get('email')

            usr_otp =   request.data.get('entered_otp')   #Retrive the user provided OTP
            stored_otp = request.data.get('otp') #Access the OTP from the response data in 'EmailVerify' view
            if usr_otp == stored_otp:
                try:
                    user=User.objects.get(email=email)
                    token=get_tokens_for_user(user)
                    return Response({'Msg':'Your Login Successful','token':token},status=status.HTTP_200_OK)
            
                except User.DoesNotExist:
                    return Response({'Msg':'Your Email is invalid'},status=status.HTTP_404_NOT_FOUND)

            return Response({'Invalid OTP'},status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    
class UpdateOwnerPassword(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class=ChangePasswordSerializer
    @extend_schema(responses=ChangePasswordSerializer)

    def patch(self, request):
        serializer=ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user=request.user
            old_password=serializer.validated_data.get('old_password')
            new_password=serializer.validated_data.get('new_password')
            confirm_password=serializer.validated_data.get('confirm_password')
            
            if user.check_password(old_password):

                if new_password==confirm_password:
                    user.set_password(new_password)
                    user.save()

                    return Response({'Msg':'Password changed'},status=status.HTTP_200_OK)
                return Response({'Msg':'New password and Confirm Password are not match'})
            return Response({'Msg':'Invalid Old password'},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ResetOwnerpassword(APIView):
    serializer_class=ForgotpasswordSerializer
    @extend_schema(responses=ForgotpasswordSerializer)
    def patch(self, request):
        serializer=ForgotpasswordSerializer(data=request.data)
        if serializer.is_valid():
            email=request.data.get('email')
            type_password=serializer.validated_data.get('update_password')
            equel_password=serializer.validated_data.get('sure_password')
            if type_password==equel_password:
                try:
                    user=User.objects.get(email=email)
                    user.set_password(type_password)
                    user.save()
                    return Response({'Msg':'Reset Your Password'},status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({'Msg':'Your Email is invalid'},status= status.HTTP_404_NOT_FOUND)
            else:
                return Response({'Msg':'Type password and Equel Password are not match'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            
class WorkshopOwnerLogin(APIView):
    serializer_class=UserLoginSerializer
    @extend_schema(responses=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        print(serializer,'haiiiiiiiii')
        if serializer.is_valid():
            email=serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            shopowner=authenticate(request, email=email,password=password)
            print(shopowner,'hloooo')
            if shopowner is not None:
                if shopowner.is_active :
                    token = get_tokens_for_user(shopowner)
                    return Response({'Msg':'Login Success','token':token},status=status.HTTP_200_OK)
                return Response({'Msg':'You are Bloked'})
            else:
                return Response({'Msg':'Email or Password is invalid'},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


            

            
