from django.shortcuts import render
from rest_framework.views import APIView
from userapp.models import User
from userside.models import Location,RequestShop,ServiceBooking
from shopdetails.models import Workshopdetails,Services,Category
from adminpannel.models import Notifications
from userapp.serializers import UserLoginSerializer,UserProfileSerializer
from userside.serializers import LocationListSerializer,RequestedShopListSerializer
from adminpannel.serializers import (ShopDetailRetriveAdminSerializer,UserProfileListSerializer,
                                     ShopSearchAdminSerializer,ServiceListAdminSerializer,
                                     CategoryAdminSerializer,BookingAdminSerializer,
                                     ShopBookingAdminSerializer)
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from userapp.auths.tokens import get_tokens_for_user
from django.conf import settings
from userapp.auths.smtp import verify_mail
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from rest_framework.permissions import IsAuthenticated
from userapp.custompermission import OnlyAdminPermission
from shopdetails.tasks import send_mail_to_users,send_notifications_to_users
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Prefetch
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Create your views here.



class AdminLoginView(APIView):
    @swagger_auto_schema(
    tags=["AdminProfile"],
    operation_description="Login for Admin",
    responses={200: UserLoginSerializer, 400: "bad request", 500: "errors"},
    request_body=UserLoginSerializer
    )
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
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminUsersView"],
    operation_description="Admin User List",
    responses={200: UserProfileListSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            users=User.objects.filter(is_shopowner=False,is_admin=False)
            serializer= UserProfileListSerializer(users,many=True)
            return Response (serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':'Have not Users'})
        

        
class UserUpdateAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminUserUpdate"],
    operation_description="Admin User Update",
    responses={200: UserProfileListSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request,pk=None):

        try:
            user = User.objects.get(id=pk)
            serializer = UserProfileListSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'User Not Found {e}'},status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
    tags=["AdminUserUpdate"],
    operation_description="Admin User Update",
    responses={200: UserProfileListSerializer, 400: "bad request", 500: "errors"},
    request_body=UserProfileListSerializer
    )
    def patch(self,request,pk=None):

        try:
            user = User.objects.get(id=pk)
            serializer = UserProfileListSerializer(user,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except Exception as e:
            return Response({"Msg":f'User not found {e}'})
        
    @swagger_auto_schema(
    tags=["AdminUserUpdate"],
    operation_description="Admin User Update",
    responses={200: UserLoginSerializer, 400: "bad request", 500: "errors"},
    )
    def delete(self,request,pk=None):

        try:
            user = User.objects.get(id=pk)
            user.delete()
            return Response({'Msg':'User deleted'})
        except Exception as e:
            return Response({'Msg':f'User not found {e}'})
        



class ShopOwnerListAdminView(APIView):
    
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminShopOwnerList"],
    operation_description="Admin ShopOwner List",
    responses={200: UserProfileListSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            owner=User.objects.filter(is_shopowner=True)
            serializer=UserProfileListSerializer(owner,many=True)
            return Response (serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':'Have not ShopOwners'})
        


class ShopdetailsListView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminShopsList"],
    operation_description="Admin Shops List",
    responses={200: ShopDetailRetriveAdminSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):

        try:
            shops = Workshopdetails.objects.all()
            serializer = ShopDetailRetriveAdminSerializer(shops,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'Shops are not found {e}'})

class ShopUpdateAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminShopUpdate"],
    operation_description="Admin Shop get",
    responses={200: ShopDetailRetriveAdminSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request,pk=None):

        try:
            shop = Workshopdetails.objects.get(id=pk)
            serializer = ShopDetailRetriveAdminSerializer(shop)
            return Response(serializer.data)
        except Exception as e:
            return Response({'Msg':f'Shop NOt Found {e}'})
    @swagger_auto_schema(
    tags=["AdminShopUpdate"],
    operation_description="Admin Shop update",
    responses={200: ShopDetailRetriveAdminSerializer, 400: "bad request", 500: "errors"},
    request_body=ShopDetailRetriveAdminSerializer
    )

    def put(self, request, pk=None):
        try:
            shop = Workshopdetails.objects.get(id=pk)
            serializer = ShopDetailRetriveAdminSerializer(shop, data=request.data, partial=True)
            if serializer.is_valid():
                approved = request.data.get('is_approved')
                serializer.save()
                if approved:
                    content = 'NewShopRegistered'
                    name = shop.shopname
                    location = shop.place
                    send_notifications_to_users.delay(name, location, content)

                    return Response(serializer.data)
                return Response(serializer.data)
            return Response(serializer.errors)
        except Exception as e:
            return Response({'Msg': f'Shop Not Found {e}'})
        
    @swagger_auto_schema(
    tags=["AdminShopUpdate"],
    operation_description="Admin Shop Delete",
    responses={200: UserProfileListSerializer, 400: "bad request", 500: "errors"},
    )
    def delete(self,request,pk=None):
        try:
            shop =Workshopdetails.objects.get(id=pk)
            shop.delete()
            return Response({'Msg':'Shop deleted'})
        except Exception as e:
            return Response({'Msg':f'Shop data not found {e}'})


class SendApprovalmail(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["ShopAuthentication"],
    operation_description="Shop Registeration",
    responses={200: 'Success', 400: "bad request", 500: "errors"},
    )
    def post(self, request):
        users = User.objects.filter(is_shopowner=True).prefetch_related(
            Prefetch('workshops', queryset=Workshopdetails.objects.filter(is_approved=True), to_attr='approved_workshops')
        )
        recipient_emails = [user.email for user in users if user.approved_workshops]

        if recipient_emails:
            subject = "Your shop data updated..."
            message = "Verified your data and updated. Please check it..."
            sender = settings.EMAIL_HOST_USER
            send_mail_to_users.delay(subject, message, sender, recipient_emails)
            return Response(recipient_emails,status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'No approved workshops found'})


class LocationAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminLocationsList"],
    operation_description="Admin ocations get",
    responses={200: LocationListSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):

        try:
            locations = Location.objects.all()
            serializer = LocationListSerializer(locations,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':f'Locations not found {e}'})
        


class AddLocationAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminLocationUpdate"],
    operation_description="Admin Shop get",
    responses={200: LocationListSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request,pk=None):
        try:
            exist_location = Location.objects.get(id=pk)
            print(exist_location, 'Location object')
            serializer = LocationListSerializer(exist_location)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'Location not found {e}'},status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
    tags=["AdminLocationUpdate"],
    operation_description="Admin Location Creation",
    responses={200: LocationListSerializer, 400: "bad request", 500: "errors"},
    request_body=LocationListSerializer
    )
        
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
    

    @swagger_auto_schema(
    tags=["AdminLocationUpdate"],
    operation_description="Admin Location Update",
    responses={200: LocationListSerializer, 400: "bad request", 500: "errors"},
    request_body=LocationListSerializer
    )
    def put(self,request,pk=None):
        
        loc = Location.objects.get(id=pk)
        serializer = LocationListSerializer(loc,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    @swagger_auto_schema(
    tags=["AdminLocationUpdate"],
    operation_description="Admin Location Delete",
    responses={200: LocationListSerializer, 400: "bad request", 500: "errors"},
    )
    def delete(self,request,pk=None):
        try:
            location = Location.objects.get(id=pk)
            location.delete()
            return Response({'Msg':'Location deleted'})
        except Exception as e:
            return Response({'Msg':'Location not found'})


class ShopsearchView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminSerch"],
    operation_description="Admin Shop Serch",
    responses={200: ShopSearchAdminSerializer, 400: "bad request", 500: "errors"},
    manual_parameters=[
        openapi.Parameter(
            name='q',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Search',
            required=True
        ),
        
    ]
    )
    def get(self, request):

        q= request.GET.get("q")
        if q is None or len(q.strip()) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        search =( Q(state__icontains=q)| Q(district__icontains=q)| Q(city__icontains=q)| Q(place__icontains=q) |
                 Q(category__category__icontains=q)|Q(services__service_name__icontains=q)|Q(shopname__iexact=q))

        search_shop=Workshopdetails.objects.filter(search).distinct()
        if search_shop:
            serializer = ShopSearchAdminSerializer(search_shop,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'Msg':'Shop Not Found '},status=status.HTTP_404_NOT_FOUND)



class ShopsAdminRetriveView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminShopRetrive"],
    operation_description="Admin Shop retrive by location and category",
    responses={200: ShopSearchAdminSerializer, 400: "bad request", 500: "errors"},
    request_body=ShopSearchAdminSerializer
    )
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

        serializer = ShopSearchAdminSerializer(shops, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



class RequestShopListAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminShopRequestList"],
    operation_description="Admin get Requested Shops",
    responses={200: RequestedShopListSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            request_shops =RequestShop.objects.all()
            serializer = RequestedShopListSerializer(request_shops,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'Haven\'t Request Shops {e}'},status=status.HTTP_404_NOT_FOUND)
        

class RequestShopUpdateAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminRequestedShopUpdate"],
    operation_description="Admin get Requested Shop",
    responses={200: RequestedShopListSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request,pk=None):
        try:
            request_shop =RequestShop.objects.get(id=pk)
            serializer = RequestedShopListSerializer(request_shop)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'Msg':f'Request Not Found {e}'})
        

    @swagger_auto_schema(
    tags=["AdminRequestedShopUpdate"],
    operation_description="Admin update Requested Shop",
    responses={200: RequestedShopListSerializer, 400: "bad request", 500: "errors"},
    request_body=RequestedShopListSerializer
    )
    def patch(self,request,pk=None):
        try:
            request_shop =RequestShop.objects.get(id=pk)
            serializer = RequestedShopListSerializer(request_shop,data=request.data)
            if serializer.is_valid():
                email = request.data.get('email')
                status = request.data.get('status') 

                if status == 'PENDING':
                    message = "Your Request is still pending."
                elif status == 'ACCEPTED':
                    message = "Your Request has been accepted."
                elif status == 'REJECTED':
                    message = "Your Request has been rejected."

                subject = "Your Request Updation..."
                sender = settings.EMAIL_HOST_USER
                recipient_list = [email]
                verify_mail(subject, message, sender, recipient_list)
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        except Exception as e:
            return Response({'Msg':f'Request data not found {e}'})
            

class SeriveceListAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminServicesList"],
    operation_description="Admin update Requested Shop",
    responses={200: ServiceListAdminSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            serice_details = Services.objects.all()
            serializer = ServiceListAdminSerializer(serice_details,many = True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Services.DoesNotExist:
            return Response({'Msg':'Not found'},status=status.HTTP_404_NOT_FOUND)
        
class CategoryAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminCategoryCreation"],
    operation_description="Admin get Categories",
    responses={200: CategoryAdminSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):

        try:
            category = Category.objects.all()
            serializer = CategoryAdminSerializer(category,many = True)
            return Response (serializer.data,status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'Msg':'Not Found'},status=status.HTTP_404_NOT_FOUND)
        

    @swagger_auto_schema(
    tags=["AdminCategoryCreation"],
    operation_description="Admin Create Category",
    responses={200: CategoryAdminSerializer, 400: "bad request", 500: "errors"},
    request_body=CategoryAdminSerializer
    )
    def post(self,request):

        serializer = CategoryAdminSerializer(data=request.data)
        if serializer.is_valid():
            category = Category.objects.create(
                category = serializer.validated_data.get('category')
            )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class BookingLIstAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminBookingsList"],
    operation_description="Admin get all Bookings",
    responses={200: BookingAdminSerializer, 400: "bad request", 500: "errors"},
    )
    def get(self,request):
        try:
            bookings = ServiceBooking.objects.all()
            serializer = BookingAdminSerializer(bookings,many=True)
            return Response(serializer.data)
        except ServiceBooking.DoesNotExist:
            return Response(serializer.errors)


class BookingshopAdminView(APIView):
    permission_classes=[IsAuthenticated,OnlyAdminPermission]
    @swagger_auto_schema(
    tags=["AdminShopsBookingList"],
    operation_description="Admin get all Bookings of specifide shop",
    responses={200: ShopBookingAdminSerializer, 400: "bad request", 500: "errors"},
       manual_parameters=[
        openapi.Parameter(
            name='shop_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='ID of the shop',
            required=True
        ),
        
    ]
    
    )
    def get(self,request):
        try:
            shop = request.GET.get('shop_id')
            workshop = Workshopdetails.objects.get(id=shop)
            bookings = ServiceBooking.objects.filter(workshop=workshop)
            serializer = ShopBookingAdminSerializer(bookings,many=True)
            return Response(serializer.data)
        except ServiceBooking.DoesNotExist:
            return Response(serializer.errors)
        


        



