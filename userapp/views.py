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
from rest_framework.decorators import permission_classes
from userapp.custompermission import OnlyUserPermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# Create your views here.



class UserRegisterCreateView(APIView):
    @swagger_auto_schema(
    tags=["User Authentication"],
    operation_description="User Registeration",
    responses={200: UserRegisterSerializer, 400: "bad request", 500: "errors"},
    request_body=UserRegisterSerializer,  
    )
    
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
    


class PhoneVarifyView(APIView):
    @swagger_auto_schema(
    tags=["User otp generating"],
    operation_description="User phone verify ",
    responses={200: PhoneSerializer, 400: "bad request", 500: "errors"},
    request_body=PhoneSerializer
    )
    def post(self,request):

        if request.method == 'POST':
            serializer=PhoneSerializer(data=request.data)
            if serializer.is_valid():
                phone=serializer.validated_data.get('phone')
                try:
                    verification_sid=send_sms(phone)
                    request.session['verification_sid']=verification_sid
                    print(f'verification_sid: {verification_sid}, phone: {phone}')
                    request.session['phone']=phone
                    return Response({'id':verification_sid},status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    return Response({'msg':'cant send otp...!'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
    tags=["User otp generating"],
    operation_description="User Resend otp",
    responses={200: PhoneSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self, request):
            
            previous_phone=request.session.get('phone')
            if previous_phone:
                try:
                    verification_sid=send_sms(previous_phone)
                    
                    verification_sid = request.session.get('verification_sid')
                    return Response({'id':verification_sid},status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    return Response({'Msg':'Can\t send OTP...!'},status= status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({'Msg':'Previous OTP request not found,Please submit a new request'},status=status.HTTP_404_NOT_FOUND)
                


class OtpverificationView(APIView):
    @swagger_auto_schema(
    tags=["User otp generating"],
    operation_description="User otp verify",
    responses={200: OtpSerializer, 400: "bad request", 500: "errors"},
    request_body=OtpSerializer
    )
    def post(self,request):

        serializer=OtpSerializer(data=request.data)
        if serializer.is_valid():
            otp=serializer.validated_data.get('otp')
            print(otp)
            verification_sid = request.session.get('verification_sid')

            verification_check=verify_user_code(verification_sid,otp)
            print(verification_sid,otp)
            if verification_check.status =='approved':
                
                data={
                    'msg':'Registeration successful'
                }
                return Response(data)
            
            return Response({'msg':'wrong!!!'})
        
        return Response(serializer.errors)



class UserLoginView(APIView):
    @swagger_auto_schema(
    tags=["User Authentication"],
    operation_description="User login",
    responses={200: UserLoginSerializer, 400: "bad request", 500: "errors"},
    request_body=UserLoginSerializer
    )
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
    


class ChangeUserPasswordView(APIView):

    permission_classes = [IsAuthenticated,OnlyUserPermission]
    @swagger_auto_schema(
    tags=["User password Updations"],
    operation_description="User change password",
    responses={200: ChangePasswordSerializer, 400: "bad request", 500: "errors"},
    request_body=ChangePasswordSerializer
    )
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



class ForgotPasswordView(APIView):
    @swagger_auto_schema(
    tags=["User password Updations"],
    operation_description="User forgot password",
    responses={200: ForgotpasswordSerializer, 400: "bad request", 500: "errors"},
    request_body=ForgotpasswordSerializer
    )
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
    
    
class GoogleSocialAuthUserView(APIView):
    @swagger_auto_schema(
    tags=["User Authentication"],
    operation_description="User SocialAuthentication",
    responses={200: GoogleSocialAuthSerializer, 400: "bad request", 500: "errors"},
    request_body=GoogleSocialAuthSerializer
    )
    def post(self, request):

        serializer=GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=(serializer.validated_data)['auth_token']
        return Response(data, status=status.HTTP_200_OK)
 


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated,OnlyUserPermission]
    @swagger_auto_schema(
    tags=["User Profile"],
    operation_description="User Profile get",
    responses={200: UserProfileSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            user=User.objects.get(email=request.user.email)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'User Not Found'},status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
    tags=["User Profile"],
    operation_description="User Profile updation",
    responses={200: UserProfileSerializer, 400: "bad request", 500: "errors"},
    request_body=UserProfileSerializer
    )
    def put(self, request):
        user = request.user

        serializer = UserProfileSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors)
    
    @swagger_auto_schema(
    tags=["User Profile"],
    operation_description="User Profile delete",
    responses={200: UserProfileSerializer, 400: "bad request", 500: "errors"},
    )
    def delete(self,request):
        user = request.user
        user.delete()
        return Response({'Msg':'Your profile and accound was deleted'})

            



            
            
        


                    
                    

