from django.shortcuts import render
from shopdetails.models import *
from userside.models import Location
from userside.serializers import LocationListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from shopdetails.serializers import ServiceSerializer,ShopDetailSerializer
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from ipware import get_client_ip
from django.contrib.gis.geos import Point
import urllib, json
import os
from django.conf import settings
from userapp.auths.smtp import verify_mail
# Create your views here.



class ShopCurrentLocationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        client_ip, is_routable = get_client_ip(request)
        print(client_ip,'clintttttttt')
        if client_ip is None:
            client_ip = "0.0.0.0"
        else:
            if is_routable:
                ip_type = "public"
            else:
                ip_type = "private"
        print(ip_type, client_ip)
        auth = os.getenv('IP_AUTH')
        print(auth)
        ip_address = "103.70.197.189"  # for checking
        url = f"https://api.ipfind.com?ip={ip_address}&auth={auth}"
        response = urllib.request.urlopen(url)
        print(response,'lllllllll')
        data = json.loads(response.read())
        data["client_ip"] = client_ip
        data["ip_type"] = ip_type
        point = Point(data["longitude"], data["latitude"])
        workshop_details, created = Workshopdetails.objects.get_or_create(
            shop_owner=request.user,
            defaults={
                'country': data["country"],
                'state': data["region"],
                'district': data["county"],
                'city': data["city"],
                'shop_coordinates': point,
            }
        )
        
        if not created:
            # If Workshopdetails already existed, update the location information
            workshop_details.country = data["country"]
            workshop_details.state = data["region"]
            workshop_details.district = data["county"]
            workshop_details.city = data["city"]
            workshop_details.shop_coordinates = point
            workshop_details.save()

        return Response(data["county"], status=status.HTTP_200_OK)

class ShopdetailsCreateUpdateView(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ShopDetailSerializer
    @extend_schema(responses=ShopDetailSerializer)
    def get(self,request):
        try:
            shop_owner =request.user
            shop=Workshopdetails.objects.filter(shop_owner=shop_owner).first()
            if shop:
                serializer=ShopDetailSerializer(shop)
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response({'Msg':'Shop Details Not Found'})
        except User.DoesNotExist:
            return Response({'Msg':'User Not Found'},status=status.HTTP_404_NOT_FOUND)
        
    def post(self,request):

        owner = request.user
        serializer = ShopDetailSerializer(owner,data=request.data)
        if serializer.is_valid():
            shop= Workshopdetails.objects.create(
                shop_owner=owner,
                shopname = serializer.validated_data.get('shopname'),
                phone = serializer.validated_data.get('phone'),
                branch = serializer.validated_data.get('branch'),
                id_proof = serializer.validated_data.get('id_proof'),
                country = serializer.validated_data.get('country'),
                state = serializer.validated_data.get('state'),
                district = serializer.validated_data.get('district'),
                city = serializer.validated_data.get('city'),
                place = serializer.validated_data.get('place'),
            
            )
            category_id = serializer.validated_data.get('category')
            select_category=Category.objects.get(category=category_id)
            shop.category=select_category
            shop.save()
            services = serializer.validated_data.get('service', []) 
            service_ids = [service.id for service in services]  
            shop.service.set(service_ids)

            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    serializer_class = ShopDetailSerializer
    @extend_schema(responses=ShopDetailSerializer)  
    def put(self,request):
        shop_owner =request.user
        shop = Workshopdetails.objects.get(shop_owner=shop_owner)
        print(shop)
        serializer = ShopDetailSerializer(shop,data=request.data,partial=True)
        if serializer.is_valid():
            subject = "Shop New Update..."
            message = "Shop Updated thire credentials add the location point..."
            sender = request.user.email
            recipient_list = (settings.EMAIL_HOST_USER,)
            verify_mail(subject, message, sender, recipient_list)
            serializer.save()
            data = serializer.data
            updated_data={
                'data':data,
                'Msg':"Your data updated, If you don't get the Location point. It will be updated..."
            }
            return Response(updated_data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       
    def delete(self,request):
        try:
            shop_owner = request.user
            workshop = Workshopdetails.objects.get(shop_owner=shop_owner)
            workshop.delete()
            return Response({'Msg': 'Shop details deleted'})
        except Workshopdetails.DoesNotExist:
            return Response({'Msg': 'Workshop details not found...!'}, status=status.HTTP_404_NOT_FOUND)


class AddServicesCreateView(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ServiceSerializer
    @extend_schema(responses=ServiceSerializer)
    def post(self, request):

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
                service_data = serializer.validated_data.get('service')
                price_data = serializer.validated_data.get('price')  # Retrieve the price

                service, created = Services.objects.get_or_create(service=service_data, defaults={'price': price_data})
                if created:
                    return Response({'Msg':'New Service Added'},status=status.HTTP_200_OK)
                else:
                    return Response({'Msg':'Service Allready Exist You can Select that when you create your shop details'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

            



    







