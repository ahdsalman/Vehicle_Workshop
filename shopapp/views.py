from django.shortcuts import render
from shopapp.models import WorkshopOwner
from userapp.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from shopapp.serializer import *
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
# Create your views here.

class WorkshopOwnerRegister(APIView):
    def post(self, request):
        serializer = shopOwnerRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create a new User instance
            user = User.objects.create_user(
                first_name=serializer.validated_data.get('first_name'),
                last_name=serializer.validated_data.get('last_name'),
                username=serializer.validated_data.get('username'),
                email=serializer.validated_data.get('email'),
                password=serializer.validated_data.get('password'),
                is_shopowner = True
                
            )

            # Create a WorkshopOwner instance with the required fields
            workshop_owner, created = WorkshopOwner.objects.get_or_create(user=user)
            # user=user,
            workshop_owner.shopname=serializer.validated_data.get('shopname')
            workshop_owner.city=serializer.validated_data.get('city')
            workshop_owner.phone=serializer.validated_data.get('phone')
            
            workshop_owner.save()
            
            

            return Response({'Msg': 'Registeration Successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EmailVerify(APIView):
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

            email_thread = Thread(target=verify_mail, args=(subject, message, sender, recipient_list))
            email_thread.start()

            response_data={
                'email':email,
                'otp':otp
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailOtpVerify(APIView):
    def post(self, request):
                
        usr_otp =   request.data.get('entered_otp')   #Retrive the user provided OTP
        email=request.data.get('email')
        stored_otp = request.data.get('otp') #Access the OTP from the response data in 'EmailVerify' view
        if usr_otp == stored_otp:
            try:
                user=User.objects.get(email=email)
                token=get_tokens_for_user(user)
                return Response({'Msg':'Your Login Successful','token':token},status=status.HTTP_200_OK)
            
            except User.DoesNotExist:
                return Response({'Msg':'Your Email is invalid'},status=status.HTTP_404_NOT_FOUND)

        return Response({'Invalid OTP'},status=status.HTTP_401_UNAUTHORIZED)
    
# class WorkshopOwnerLogin(APIView):
#     def post(self, request):
#         serializer = ShopOwnerLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             email=serializer.validated_data.get('email')
#             password = serializer.validated_data.get('password')
#             shoowner=authenticate(request, email=email,password=password)
#             if shoowner is not None:
#                 if shoowner.is_active:
#                     token = get_tokens_for_user(shoowner)
#                     return Response({'Msg':'Login Success','token':token},status=status.HTTP_200_OK)
#                 return Response({'Msg':'You are Bloked'})
#             else:
#                 return Response({'Msg':'Email or Password is invalid'},status=status.HTTP_404_NOT_FOUND)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


            

            
