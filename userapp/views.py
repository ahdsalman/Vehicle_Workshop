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
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes
from userapp.custompermission import OnlyUserPermission
# Create your views here.



class UserRegisterCreateView(APIView):
    serializer_class=UserRegisterSerializer
    @extend_schema(responses=UserRegisterSerializer)
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
    serializer_class=PhoneSerializer
    @extend_schema(responses=PhoneSerializer)
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
    serializer_class=PhoneSerializer
    @extend_schema(responses=PhoneSerializer)
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
    serializer_class=OtpSerializer
    @extend_schema(responses=OtpSerializer)
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
    serializer_class=UserLoginSerializer
    @extend_schema(responses=UserLoginSerializer)
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



class ForgotPasswordView(APIView):
    serializer_class=ForgotpasswordSerializer
    @extend_schema(responses=ForgotpasswordSerializer)
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
    serializer_class=GoogleSocialAuthSerializer
    @extend_schema(responses=GoogleSocialAuthSerializer)
    def post(self, request):

        serializer=GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=(serializer.validated_data)['auth_token']
        return Response(data, status=status.HTTP_200_OK)
 


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated,OnlyUserPermission]
    serializer_class=UserProfileSerializer
    @extend_schema(responses=UserProfileSerializer)
    def get(self,request):
        try:
            user=User.objects.get(email=request.user.email)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'User Not Found'},status=status.HTTP_404_NOT_FOUND)
    
    serializer_class=UserProfileSerializer
    @extend_schema(responses=UserProfileSerializer)
    def put(self, request):
        user = request.user

        serializer = UserProfileSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors)
    
    
    def delete(self,request):
        user = request.user
        user.delete()
        return Response({'Msg':'Your profile and accound was deleted'})

            



            
            
        


                    
                    

