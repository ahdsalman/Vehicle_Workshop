from django.shortcuts import render
from shopdetails.models import *
from userside.models import Location,ServiceBooking
from userside.serializers import LocationListSerializer,ServiceBookingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from shopdetails.serializers import ServiceSerializer,ShopDetailSerializer,ShopDetailRetriveSerializer
from rest_framework.response import Response
from django.db.models import Q
from ipware import get_client_ip
from django.contrib.gis.geos import Point
import urllib, json
import os
from django.conf import settings
from userapp.auths.smtp import verify_mail
from userapp.custompermission import OnlyShopPermission,OnlyOwnerPermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from shopdetails.tasks import send_mail_to_users
# Create your views here.



class ShopCurrentLocationView(APIView):
    permission_classes=[IsAuthenticated,OnlyOwnerPermission]
    @swagger_auto_schema(
    tags=["ShopDetails"],
    operation_description="Shop add current location",
    responses={200: ShopDetailRetriveSerializer,400: "bad request", 500: "errors"},
    )
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
            workshop_details.country = data["country"]
            workshop_details.state = data["region"]
            workshop_details.district = data["county"]
            workshop_details.city = data["city"]
            workshop_details.shop_coordinates = point
            workshop_details.save()

        return Response(data["county"], status=status.HTTP_200_OK)


class ShopdetailsCreateUpdateView(APIView):
    permission_classes=[IsAuthenticated,OnlyOwnerPermission]
    parser_classes=[MultiPartParser]
    @swagger_auto_schema(
    tags=["ShopDetails"],
    operation_description="Shop Details get",
    responses={200: ShopDetailRetriveSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            shop_owner =request.user
            shop=Workshopdetails.objects.filter(shop_owner=shop_owner).first()
            if shop:
                serializer=ShopDetailRetriveSerializer(shop)
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response({'Msg':'Shop Details Not Found'})
        except User.DoesNotExist:
            return Response({'Msg':'User Not Found'},status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
    tags=["ShopDetails"],
    operation_description="Shop Details creation",
    responses={200: ShopDetailSerializer, 400: "bad request", 500: "errors"},
    request_body=ShopDetailSerializer
    )
    def post(self,request):

        owner = request.user
        serializer = ShopDetailSerializer(data=request.data)

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
            try:
                select_category=Category.objects.get(category=category_id)
                shop.category=select_category
                shop.save()
            except Category.DoesNotExist as e:
                return Response({'error': f'Category does not exist.{e}'}, status=status.HTTP_400_BAD_REQUEST)
            
            service_ids = [service.id for service in serializer.validated_data.get('services', [])]
  
            existing_services = Services.objects.filter(id__in=service_ids)
            existing_service_ids = existing_services.values_list('id', flat=True)
            if set(service_ids) != set(existing_service_ids):
                
                return Response({'error': 'One or more services do not exist.'}, status=status.HTTP_400_BAD_REQUEST)
            shop.services.set(service_ids)

            subject = "New Shop Launched..."
            message = "Shop created Please check it..."
            sender = request.user.email
            recipient_list = (settings.EMAIL_HOST_USER,)
            verify_mail(subject, message, sender, recipient_list)
            created_data=serializer.data
            service_data={
                'create_data':created_data,
                'Msg':'Will approve your shop after verify your ID Proof and add your shop Location coordinates,You Will know this trough email'
            }
            return Response(service_data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    @swagger_auto_schema(
    tags=["ShopDetails"],
    operation_description="Shop Details updation",
    responses={200: ShopDetailSerializer, 400: "bad request", 500: "errors"},
    request_body=ShopDetailSerializer
    )
    def put(self,request):
        shop_owner =request.user
        shop = Workshopdetails.objects.get(shop_owner=shop_owner)
        
        serializer = ShopDetailSerializer(shop,data=request.data,partial=True)
        if serializer.is_valid():
            subject = "Shop New Update..."
            message = "Shop Updated Please check it..."
            sender = request.user.email
            recipient_list = (settings.EMAIL_HOST_USER,)
            verify_mail(subject, message, sender, recipient_list)
            serializer.save()
            data = serializer.data
            updated_data={
                'data':data,
                'Msg':"Your data updated, If you don't get the Location point. It will be updated...,If you have update your ID Proof will approve after verifying"
            }
            return Response(updated_data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       
    @swagger_auto_schema(
    tags=["ShopDetails"],
    operation_description="Shop Details Delete",
    responses={200: ShopDetailSerializer, 400: "bad request", 500: "errors"},
    )
    def delete(self,request):
        try:
            shop_owner = request.user
            workshop = Workshopdetails.objects.get(shop_owner=shop_owner)
            workshop.delete()
            return Response({'Msg': 'Shop details deleted'})
        except Workshopdetails.DoesNotExist:
            return Response({'Msg': 'Workshop details not found...!'}, status=status.HTTP_404_NOT_FOUND)


    
class AddServicesCreateView(APIView):
    permission_classes=[IsAuthenticated,OnlyShopPermission,OnlyOwnerPermission]
    @swagger_auto_schema(
    tags=["Shop Add Service"],
    operation_description="Shop service adding",
    responses={200: ServiceSerializer, 400: "bad request", 500: "errors"},
    request_body=ServiceSerializer
    )
    def post(self, request):

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
                service_data = serializer.validated_data.get('service_name')
                price_data = serializer.validated_data.get('price')

                service, created = Services.objects.get_or_create(service_name=service_data,price=price_data, defaults={'price': price_data})
                if created:
                    return Response({'Msg':'New Service Added'},status=status.HTTP_200_OK)
                else:
                    return Response({'Msg':'Service Allready Exist You can Select that when you create your shop details'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class ShopServiceBookingRetriveView(APIView):
     permission_classes=[IsAuthenticated,OnlyShopPermission,OnlyOwnerPermission]
     @swagger_auto_schema(
    tags=["Shop Service Booking details"],
    operation_description="Shop booking details get",
    responses={200: ServiceBookingSerializer, 400: "bad request", 500: "errors"},
    )
     def get(self,request):
        try:
             shop = request.user.id
            
             workshop = Workshopdetails.objects.prefetch_related('servicebooking_set').get(shop_owner=shop)
             bookings = workshop.servicebooking_set.all()
             serializer = ServiceBookingSerializer(bookings,many=True)
             return Response(serializer.data,status=status.HTTP_200_OK)
        except ServiceBooking.DoesNotExist:
            return Response({'Msg':'booking data not found'})
         

from userside.models import Payment
from userside.serializers import StripepaymentSerializer

class ServicePaymentRetriveView(APIView):
    permission_classes=[IsAuthenticated,OnlyShopPermission,OnlyOwnerPermission]
    @swagger_auto_schema(
    tags=["Shop Payment Details"],
    operation_description="Shop Payment Details get",
    responses={200: ServiceBookingSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            shop = request.user.id
            workshop = Workshopdetails.objects.get(shop_owner=shop)
            payments = Payment.objects.filter(pay_workshop=workshop)
            serializer = StripepaymentSerializer(payments,many = True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'Msg':'Shop not found'})