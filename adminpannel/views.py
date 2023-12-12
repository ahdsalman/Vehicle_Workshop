from django.shortcuts import render
from rest_framework.views import APIView
from userapp.models import User
from userside.models import Location
from shopdetails.models import Workshopdetails
from userapp.serializers import UserLoginSerializer,UserProfileSerializer
from userside.serializers import LocationListSerializer
from adminpannel.serializers import ShopDetailRetriveAdminSerializer
from adminpannel.serializers import UserProfileListSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from userapp.auths.tokens import get_tokens_for_user
from django.conf import settings
from userapp.auths.smtp import verify_mail
# Create your views here.



class AdminLoginView(APIView):
    def post(self, request):

        serializer= UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user=authenticate(email=email,password=password)
            if user is not None :
                if user.is_active and user.is_admin:
                    token= get_tokens_for_user(user)
                    return Response({'Msg':'Login Success','token':token},status=status.HTTP_200_OK)
                return Response({'Msg':'You are blocked or not admin'})
            return Response({'Msg':'User not found'},status=status.HTTP_401_UNAUTHORIZED)


     
class UserListAdminView(APIView):
    def get(self,request):
        try:
            users=User.objects.filter(is_shopowner=False,is_admin=False)
            serializer= UserProfileListSerializer(users,many=True)
            return Response (serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':'Have not Users'})
        

        
class UserUpdateAdminView(APIView):
    def get(self,request,pk=None):

        try:
            user = User.objects.get(id=pk)
            serializer = UserProfileListSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'User Not Found {e}'},status=status.HTTP_404_NOT_FOUND)
        
    def patch(self,request,pk=None):

        try:
            user = User.objects.get(id=pk)
            serializer = UserProfileListSerializer(user,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except Exception as e:
            return Response({"Msg":f'User not found {e}'})
        
    def delete(self,request,pk=None):

        try:
            user = User.objects.get(id=pk)
            user.delete()
            return Response({'Msg':'User deleted'})
        except Exception as e:
            return Response({'Msg':f'User not found {e}'})
        



class ShopOwnerListAdminView(APIView):
    def get(self,request):
        try:
            owner=User.objects.filter(is_shopowner=True)
            serializer=UserProfileListSerializer(owner,many=True)
            return Response (serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':'Have not ShopOwners'})
        


class ShopdetailsListView(APIView):

    def get(self,request):

        try:
            shops = Workshopdetails.objects.all()
            serializer = ShopDetailRetriveAdminSerializer(shops,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'Shops are not found {e}'})

class ShopUpdateAdminView(APIView):
    def get(self,request,pk=None):

        try:
            shop = Workshopdetails.objects.get(id=pk)
            serializer = ShopDetailRetriveAdminSerializer(shop)
            return Response(serializer.data)
        except Exception as e:
            return Response({'Msg':f'Shop NOt Found {e}'})
        
    def put(self,request,pk=None):
        try:
            shop = Workshopdetails.objects.get(id=pk)
            serializer = ShopDetailRetriveAdminSerializer(shop,data=request.data,partial=True)
            if serializer.is_valid():
                email = request.data.get('email')

                subject = "Your shop data updated..."
                message = "Verified your data and updated. Please check it..."
                sender = settings.EMAIL_HOST_USER
                recipient_list = [email]
                verify_mail(subject, message, sender, recipient_list)
                serializer.save()
            
            return Response(serializer.data)
        except Exception as e :
            return Response({'Msg':f'Shop Not Found {e}'})
        
    def delete(self,request,pk=None):
        try:
            shop =Workshopdetails.objects.get(id=pk)
            shop.delete()
            return Response({'Msg':'Shop deleted'})
        except Exception as e:
            return Response({'Msg':f'Shop data not found {e}'})



class LocationAdminView(APIView):
    def get(self,request):

        try:
            locations = Location.objects.all()
            serializer = LocationListSerializer(locations,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':f'Locations not found {e}'})
        


class AddLocationAdminView(APIView):
    def get(self,request,pk=None):
        print(pk, 'Received pk')
        try:
            exist_location = Location.objects.get(id=pk)
            print(exist_location, 'Location object')
            serializer = LocationListSerializer(exist_location)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'Location not found {e}'},status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):

        serializer = LocationListSerializer(data=request.data)
        if serializer.is_valid():
            new_location = Location.objects.create(
                country = serializer.validated_data.get('country'),
                state = serializer.validated_data.get('state'),
                district = serializer.validated_data.get('district'),
                city =serializer.validated_data.get('city'),
                place = serializer.validated_data.get('place'),

            )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,pk=None):
        
        loc = Location.objects.get(id=pk)
        serializer = LocationListSerializer(loc,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.data,status=status.HTTP_200_OK)





