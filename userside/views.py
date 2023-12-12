
from shopdetails.models import Workshopdetails,Category,Services
from userapp.models import User,Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from ipware import get_client_ip
from django.contrib.gis.geos import Point
from userside.models import Location,RequestShop
from django.conf import settings
import urllib, json
import os
from django.db.models import Q
from userside.serializers import LocationListSerializer,RequestedShopListSerializer,ShopShowSerializer
from django.contrib.gis.measure import Distance
from userapp.auths.smtp import verify_mail
from drf_spectacular.utils import extend_schema


# class UserCurrentLocation(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         client_ip, is_routable = get_client_ip(request)
#         print(client_ip,'clintttttttt')
#         if client_ip is None:
#             client_ip = "0.0.0.0"
#         else:
#             if is_routable:
#                 ip_type = "public"
#             else:
#                 ip_type = "private"
#         print(ip_type, client_ip)
#         auth = os.getenv('IP_AUTH')
#         print(auth)
#         ip_address = "103.70.197.189"  # for checking
#         url = f"https://api.ipfind.com?ip={ip_address}&auth={auth}"
#         response = urllib.request.urlopen(url)
#         print(response,'lllllllll')
#         data = json.loads(response.read())
#         data["client_ip"] = client_ip
#         data["ip_type"] = ip_type
#         point = Point(data["longitude"], data["latitude"])
#         if not Profile.objects.filter(usr_location=point).exists():
#             Profile.objects.create(
#                 country=data["country"],
#                 state=data["region"],
#                 district=data["county"],
#                 city=data["city"],
#                 place=data["place"],
#                 coordinates=point,
#             )
#         return Response(data["county"], status=status.HTTP_200_OK)


class ShopsearchRetriveRequestView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class=ShopShowSerializer
    extend_schema(responses=ShopShowSerializer)
    def get(self, request):

        q= request.GET.get("q")
        if q is None or len(q.strip()) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        search =( Q(state__icontains=q)| Q(district__icontains=q)| Q(city__icontains=q)| Q(place__icontains=q) |
                 Q(category__category__icontains=q)|Q(service__service_name__icontains=q)|Q(shopname__iexact=q))

        search_shop=Workshopdetails.objects.filter(search).distinct()
        if search_shop:
            serializer = ShopShowSerializer(search_shop,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'Msg':'Shop Not Found '},status=status.HTTP_404_NOT_FOUND)

    serializer_class = RequestedShopListSerializer
    extend_schema(responses=RequestedShopListSerializer)
    def post(self,request):

        print(request.user,"kkkkkkkkk")
        serializer= RequestedShopListSerializer(data=request.data)
        if serializer.is_valid():
            try:
                new_request_shop=RequestShop.objects.create(
                    user = request.user,
                    country = serializer.validated_data.get('country'),
                    state = serializer.validated_data.get('state'),
                    district =serializer.validated_data.get('district'),
                    city = serializer.validated_data.get('city'),
                    place = serializer.validated_data.get('place'),
                    req_service = serializer.validated_data.get('req_service')
                )
                req_category = serializer.validated_data.get('req_category',[])

                for category_id in req_category:
                    category = Category.objects.get(category=category_id)
                    new_request_shop.req_category.add(category)

                subject = "New Request For adding Shops"
                message = "New Shop adding request, check it out ......."
                sender = request.user.email
                recipient_list = (settings.EMAIL_HOST_USER,)
                verify_mail(subject, message, sender, recipient_list)
                return Response({'Msg':'Your Location and Shops will be updated Soon...'},status=status.HTTP_200_OK)
            except Exception as e :
                return Response({'Msg':f'Somthing wrong..! {e}'})
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

            


class ShopsRetriveView(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ShopShowSerializer
    @extend_schema(responses=ShopShowSerializer)
    def post(self, request):
        usr_longitude = request.data.get('usr_longitude')
        usr_latitude = request.data.get('usr_latitude')
        usr_category = request.data.get('usr_category')

        try:
            usr_longitude = float(usr_longitude)
            usr_latitude = float(usr_latitude)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid coordinates'}, status=status.HTTP_400_BAD_REQUEST)

        usr_location = Point(usr_longitude, usr_latitude, srid=4326)

        shops = Workshopdetails.objects.filter(
            shop_coordinates__distance_lte=(usr_location, Distance(km=50)),
            category=usr_category,
            is_approved=True
        )
        if not shops :
            return Response({'Msg':'Have nt Shop here'})

        serializer = ShopShowSerializer(shops, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)




class UserShopRetriveView(APIView):
     def get(self, request,pk=None):
         
        try:
             shop=Workshopdetails.objects.get(id=pk)
             serializer=ShopShowSerializer(shop)
             return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':f'User Not Found {e}'},status=status.HTTP_404_NOT_FOUND)
         
         

        
