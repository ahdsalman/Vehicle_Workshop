from django.shortcuts import render
from userapp.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from userapp.serializers import * 
from rest_framework import status
from userapp.auths.utils import send_sms,verify_user_code
from userapp.auths.tokens import get_tokens_for_user
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken


# Create your views here.


class UserRegisterView(APIView):
    def post(self,request):

        serializer=UserRegisterSerializer(data=request.data)
        if serializer.is_valid():            
            User.objects.create_user(
            first_name = serializer.validated_data.get('first_name'),
            last_name = serializer.validated_data.get('last_name'),
            password = serializer.validated_data.get('password'),
            email = serializer.validated_data.get('email'),
            username = serializer.validated_data.get('username'),
            
        )
                  
            return Response({'Msg':'Enter your Mobile number'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


class PhoneVarify(APIView):
    def post(self,request):
        
        serializer=PhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone=serializer.validated_data.get('phone')
            try:
                verification_sid=send_sms(phone)
                request.session['verification_sid']=verification_sid
                return Response({'id':verification_sid},status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({'msg':'cant send otp...!'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class Otpverification(APIView):
    def post(self,request):

        serializer=OtpSerializer(data=request.data)
        if serializer.is_valid():
            otp=serializer.validated_data.get('otp')
            verification_sid = request.session.get('verification_sid')

            verification_check=verify_user_code(verification_sid,otp)
            
            if verification_check.status =='approved':
                data={
                    'msg':'Registeration successful'
                }
                return Response(data)
            
            return Response({'msg':'wrong!!!'})
        
        return Response(serializer.errors)

class UserLoginView(APIView):
    def post(self, request):

        serializer=UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email=serializer.data.get('email')
            password=serializer.data.get('password')
            user=authenticate(request,email=email,password=password)
            if user is not None:
                if user.is_active:
                    token=get_tokens_for_user(user)
                    return Response({'Msg':'Login Success','token':token},status=status.HTTP_200_OK)
                 
                return Response({'Msg':'User is blocked'})
            else:
                return Response({'Msg':'Email or Password is not valid'},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


class ChangeUserPassword(APIView):
    permission_classes = [IsAuthenticated]
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



class ForgotPassword(APIView):
    def patch(self, request):
        
        email=request.data.get('email')
        serializer=ForgotpasswordSerializer(data=request.data)
        if serializer.is_valid():
            update_password=serializer.validated_data.get('update_password')
            sure_password=serializer.validated_data.get('sure_password')
            if update_password==sure_password:
                try:
                    user=User.objects.get(email=email)
                    user.set_password(update_password)
                    user.save()
                    return Response({'Password updated'},status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({'Please check your Email'},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'Msg':'Update Password and Sure Password are not match'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                    
                    

