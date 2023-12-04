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
# Create your views here.


class Shopdetails(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ShopDetailSerializer
    @extend_schema(responses=ShopDetailSerializer)
    def get(self,request,pk=None):
        try:

            user=Workshopdetails.objects.get(id=pk)
            serializer=ShopDetailSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'Msg':'User Not Found'},status=status.HTTP_404_NOT_FOUND)
        
    serializer_class = ShopDetailSerializer
    @extend_schema(responses=ShopDetailSerializer)  
    def put(self,request,pk=None):
        shop = Workshopdetails.objects.get(id=pk)
        print(shop)
        serializer = ShopDetailSerializer(shop,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




class AddServices(APIView):
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

            



    







