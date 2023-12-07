from django.shortcuts import render
from userapp.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from shopapp.serializer import *
from userapp.serializers import GoogleSocialAuthSerializer
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
from userapp.custompermission import OnlyOwnerPermission
# Create your views here.

class WorkshopOwnerCreateView(APIView):
    serializer_class=ShopRegisterSerializer
    @extend_schema(responses=ShopRegisterSerializer)

    def post(self, request):
        serializer = ShopRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.create_user(
                first_name = serializer.validated_data.get('first_name'),
                last_name = serializer.validated_data.get('last_name'),
                username = serializer.validated_data.get('username'),
                email = serializer.validated_data.get('email'),
                password = serializer.validated_data.get('password'),
                is_shopowner =True
                
            )
            
            
            
            return Response({'Msg': 'Enter your Email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EmailVerifyView(APIView):
    serializer_class=EmailVerifySerializer
    @extend_schema(responses=EmailVerifySerializer)
    def post(self, request):
        serializer=EmailVerifySerializer(data=request.data)
        if serializer.is_valid():
            email=request.data.get('email')
            try:
                User.objects.get(email=email)
                otp = math.floor(random.randint(100000, 999999))
                request.session['email']=email
                request.session['otp']=otp
            
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
            except User.DoesNotExist:
                return Response({'Msg':'User not registered'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailOtpVerifyView(APIView):
    serializer_class=OtpVerifySerializer
    @extend_schema(responses=OtpVerifySerializer)
    def post(self, request):
        serializer=OtpVerifySerializer(data=request.data)
        if serializer.is_valid():
            email=request.session.get('email') #Access the email from the session
            stored_otp = request.session.get('otp') #Access the OTP from the session
            
            usr_otp =   request.data.get('entered_otp')   #Retrive the user provided OTP
             
            if int(usr_otp) == int(stored_otp):
                try:
                    user=User.objects.get(email=email)
                    if user.is_active and user.is_shopowner:
                        token=get_tokens_for_user(user)
                        return Response({'Msg':'Your Login Successful','token':token},status=status.HTTP_200_OK)
                    else:
                        return Response({'Msg':'You are bloked or Not shop Owner'})
            
                except User.DoesNotExist:
                    return Response({'Msg':'Your Email is invalid'},status=status.HTTP_404_NOT_FOUND)

            return Response({'Invalid OTP'},status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

   
    
class GoogleSocialAuthOwnerView(APIView):
    serializer_class=GoogleSocialAuthSerializer
    @extend_schema(responses=GoogleSocialAuthSerializer)
    def post(self, request):

        serializer=GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=(serializer.validated_data)['auth_token']
        return Response(data, status=status.HTTP_200_OK)



class OwnerProfileView(APIView):
    permission_classes = [IsAuthenticated,OnlyOwnerPermission]
    serializer_class = OwnerProfileSerializer

    @extend_schema(responses=OwnerProfileSerializer)
    def get(self, request):
        try:
            shop_owner = User.objects.get(email=request.user.email)
            serializer = OwnerProfileSerializer(shop_owner)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
    serializer_class = OwnerProfileSerializer
    @extend_schema(responses=OwnerProfileSerializer)
    def put(self, request):
        try:
            owner = request.user
            serializer = OwnerProfileSerializer(owner, data=request.data,partial=True)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
            
    def delete(self, request):
        owner=request.user
        owner.delete()
        return Response({'Msg':'Your account was deleted'},status=status.HTTP_200_OK)
    
    



# class UpdateOwnerPassword(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class=ChangePasswordSerializer
#     @extend_schema(responses=ChangePasswordSerializer)

#     def patch(self, request):
#         serializer=ChangePasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             user=request.user
#             old_password=serializer.validated_data.get('old_password')
#             new_password=serializer.validated_data.get('new_password')
#             confirm_password=serializer.validated_data.get('confirm_password')
            
#             if user.check_password(old_password):

#                 if new_password==confirm_password:
#                     user.set_password(new_password)
#                     user.save()

#                     return Response({'Msg':'Password changed'},status=status.HTTP_200_OK)
#                 return Response({'Msg':'New password and Confirm Password are not match'})
#             return Response({'Msg':'Invalid Old password'},status=status.HTTP_404_NOT_FOUND)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# class ResetOwnerpassword(APIView):
#     serializer_class=ForgotpasswordSerializer
#     @extend_schema(responses=ForgotpasswordSerializer)
#     def patch(self, request):
#         serializer=ForgotpasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             email=request.data.get('email')
#             type_password=serializer.validated_data.get('update_password')
#             equel_password=serializer.validated_data.get('sure_password')
#             if type_password==equel_password:
#                 try:
#                     user=User.objects.get(email=email)
#                     user.set_password(type_password)
#                     user.save()
#                     return Response({'Msg':'Reset Your Password'},status=status.HTTP_200_OK)
#                 except User.DoesNotExist:
#                     return Response({'Msg':'Your Email is invalid'},status= status.HTTP_404_NOT_FOUND)
#             else:
#                 return Response({'Msg':'Type password and Equel Password are not match'})
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
