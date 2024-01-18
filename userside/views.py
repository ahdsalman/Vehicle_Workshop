
from shopdetails.models import Workshopdetails,Category,Services
from userapp.models import User,Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from userapp.custompermission import OnlyUserPermission
from ipware import get_client_ip
from django.contrib.gis.geos import Point
from userside.models import Location,RequestShop,ServiceBooking,Payment
from django.conf import settings
import urllib, json
import os
from django.db.models import Q
from userside.serializers import (LocationListSerializer,RequestedShopListSerializer,
                                  ServiceBookingSerializer,PaymentSerializer,
                                  StripepaymentSerializer)
from shopdetails.serializers import ShopDetailRetriveSerializer,ServiceSerializer
from django.contrib.gis.measure import Distance
from userapp.auths.smtp import verify_mail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from shopdetails.tasks import send_mail_to_users






class ShopsearchRetriveRequestView(APIView):
    permission_classes=[IsAuthenticatedOrReadOnly,OnlyUserPermission]
    @swagger_auto_schema(
    tags=["User Searching"],
    operation_description="User Search for shop",
    responses={200: ShopDetailRetriveSerializer, 400: "bad request", 500: "errors"},
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
            serializer = ShopDetailRetriveSerializer(search_shop,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'Msg':'Shop Not Found '},status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
    tags=["User Request for add shop"],
    operation_description="User request for add shop specifide category,service and location ",
    responses={200: RequestedShopListSerializer, 400: "bad request", 500: "errors"},
    request_body=RequestedShopListSerializer
    )
    def post(self,request):

        
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
    permission_classes = [IsAuthenticated, OnlyUserPermission]

    @swagger_auto_schema(
        tags=["User Searching"],
        operation_description="User Search shops by location and category (if want user) within distance",
        responses={200: ShopDetailRetriveSerializer, 400: "bad request", 500: "errors"},
        manual_parameters=[
            openapi.Parameter(
                name='usr_longitude',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description='User longitude',
            ),
            openapi.Parameter(
                name='usr_latitude',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description='User latitude',
            ),
            openapi.Parameter(
                name='usr_distance',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description='User distance',
            ),
            openapi.Parameter(
                name='usr_category',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='User category',
            ),
        ]
    )
    def post(self, request):
        usr_longitude = request.data.get('usr_longitude')
        usr_latitude = request.data.get('usr_latitude')
        usr_distance = request.data.get('usr_distance')
        usr_category = request.data.get('usr_category')
    

        try:
            usr_longitude = float(usr_longitude)
            usr_latitude = float(usr_latitude)
            
        except (ValueError, TypeError):
            return Response({'error': 'Invalid coordinates or distance'}, status=status.HTTP_400_BAD_REQUEST)

        if usr_category is not None and usr_distance is not None:
            usr_location = Point(usr_longitude, usr_latitude, srid=4326)

            shops = Workshopdetails.objects.filter(
                shop_coordinates__distance_lte=(usr_location, Distance(km=usr_distance)),
                category=usr_category,
                is_approved=True,
            )
        elif usr_category is not None and not usr_distance:
            usr_location = Point(usr_longitude, usr_latitude, srid=4326)
            shops = Workshopdetails.objects.filter(
                shop_coordinates__distance_lte=(usr_location, Distance(km=10)),
                category=usr_category,
                is_approved=True,
            )
        elif usr_distance is not None and not usr_category:
            usr_location = Point(usr_longitude, usr_latitude, srid=4326)
            shops = Workshopdetails.objects.filter(
                shop_coordinates__distance_lte=(usr_location, Distance(km=usr_distance)),
                is_approved=True,
            )
        else:
            usr_location = Point(usr_longitude, usr_latitude, srid=4326)
            shops = Workshopdetails.objects.filter(
                shop_coordinates__distance_lte=(usr_location, Distance(km=10)),
                is_approved=True,
            )

        if not shops:
            return Response({'Msg': 'No shops found'})

        serializer = ShopDetailRetriveSerializer(shops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserShopRetriveView(APIView):
     permission_classes=[IsAuthenticated,OnlyUserPermission]
     @swagger_auto_schema(
    tags=["User ShopRetrive"],
    operation_description="Show specifide shop",
    responses={200: ShopDetailRetriveSerializer, 400: "bad request", 500: "errors"},
    )
     def get(self, request,pk=None):
         
        try:
             shop=Workshopdetails.objects.filter(id=pk,is_approved=True)
             serializer=ShopDetailRetriveSerializer(shop,many=True)
             return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Msg':f'Shop Not Found {e}'},status=status.HTTP_404_NOT_FOUND)
         


class UserCurrentLocation(APIView):
    permission_classes = [IsAuthenticated,OnlyUserPermission]
    @swagger_auto_schema(
    tags=["User Booking"],
    operation_description="User add current location",
    responses={400: "bad request", 500: "errors"},
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
        try:
            service_booking = ServiceBooking.objects.get(user=request.user)
            
            service_booking.country = data["country"]
            service_booking.state = data["region"]
            service_booking.district = data["county"]
            service_booking.city = data["city"]
            service_booking.user_currentlocation = point
            service_booking.save()
        except ServiceBooking.DoesNotExist:
           
            service_booking = ServiceBooking.objects.create(
                user=request.user,
                country=data["country"],
                state=data["region"],
                district=data["county"],
                city=data["city"],
                user_currentlocation=point,
                
            )

        return Response(data["county"], status=status.HTTP_200_OK)

class UserServiceBooking(APIView):
    permission_classes = [IsAuthenticated,OnlyUserPermission]
    @swagger_auto_schema(
    tags=["User Booking"],
    operation_description="User get booking part of user specifide shop",
    responses={200: ServiceSerializer, 400: "bad request", 500: "errors"},
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
    def get(self, request):
        shop_id = request.GET.get("shop_id")
        if not shop_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            workshop = Workshopdetails.objects.get(id=shop_id)
            services = workshop.services.all()
            serializer = ServiceSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Workshopdetails.DoesNotExist:
            return Response({'Msg': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
    tags=["User Booking"],
    operation_description="User booking creation",
    responses={200: ServiceBookingSerializer, 400: "bad request", 500: "errors"},
    request_body=ServiceBookingSerializer,
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
    def post(self,request):
        try:
            shop_id = request.GET.get('shop_id')
            workshop = Workshopdetails.objects.get(id=shop_id)
            
            serializer = ServiceBookingSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    booking = ServiceBooking.objects.get(user=request.user)
                    
                    booking.workshop = workshop
                    booking.vehicle_make = serializer.validated_data.get('vehicle_make')
                    booking.model_name = serializer.validated_data.get('model_name')
                    booking.model_year = serializer.validated_data.get('model_year')
                    booking.user_service.set(serializer.validated_data.get('user_service'))
                    booking.save()
                except ServiceBooking.DoesNotExist:
                    
                    booking = ServiceBooking.objects.create(
                        user=request.user,
                        workshop=workshop,
                        vehicle_make=serializer.validated_data.get('vehicle_make'),
                        model_name=serializer.validated_data.get('model_name'),
                        model_year=serializer.validated_data.get('model_year'),
                        
                    )
                    booking.user_service.set(serializer.validated_data.get('user_service'))
                return Response (serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Msg':f'Shop not Found {e}'})

    @swagger_auto_schema(
    tags=["User Booking"],
    operation_description="User booking update",
    responses={200: ServiceBookingSerializer, 400: "bad request", 500: "errors"},
    request_body=ServiceBookingSerializer,
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
    def put(self,request):
        try:
            shop_id = request.GET.get('shop_id')
            workshop = Workshopdetails.objects.get(id=shop_id)
            user = request.user
            
            booking_data = ServiceBooking.objects.get(user=user, workshop=workshop)
            serializer = ServiceBookingSerializer(booking_data,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except ServiceBooking.DoesNotExist:
            return Response({'Msg': 'ServiceBooking not found for the specified user and workshop.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Msg': f'Shop Not Found: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from django.db.models import Sum 
from django.conf import settings
import os
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET')
class UserPaymentView(APIView):
    permission_classes = [IsAuthenticated,OnlyUserPermission]
    @swagger_auto_schema(
    tags=["User Payment"],
    operation_description="User Payment bill get",
    responses={200: PaymentSerializer, 400: "bad request", 500: "errors"},
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
            shop_id = request.GET.get('shop_id')
            shop = Workshopdetails.objects.get(id=shop_id)
            
            user = request.user
            user_services = ServiceBooking.objects.filter(user=user,workshop=shop)
            total_price = user_services.aggregate(total_price=Sum('user_service__price'))['total_price'] or 0
            request.session['total_price']=total_price
            serializer = PaymentSerializer(user_services,many =True).data
            response_data = {
                'user_service': serializer,
                'total_price': total_price
            }
            return Response(response_data)
        except Exception as e:
            return Response({f'User Not Found {e}'})
        


    @swagger_auto_schema(
    tags=["User Payment"],
    operation_description="User stripe Payment post",
    responses={200: PaymentSerializer, 400: "bad request", 500: "errors"},
    request_body=PaymentSerializer,
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
    def post(self, request):
        try:
            shop_id = request.GET.get('shop_id')
            shop = Workshopdetails.objects.get(id=shop_id)
            
            user = request.user
            user_services = ServiceBooking.objects.filter(user=user,workshop=shop)
            total_price = user_services.aggregate(total_price=Sum('user_service__price'))['total_price'] or 0
            request.session['total_price']=total_price
            serializer = PaymentSerializer(user_services,many =True).data
            response_data = {
                'user_service': serializer,
                'total_price': total_price
            }
            service_name = str(response_data.get('user_service'))
            service = stripe.Product.create(
                    name= service_name,
                    
                )
            print(service,'prooooooo')
            price = stripe.Price.create(
                    unit_amount=int(total_price * 100),
                    currency='usd',
                    product=service.id,  
                )


            customer = stripe.Customer.create(
                email=request.user.email,
                phone=request.user.username
            )

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': price.id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                customer=customer.id,
                success_url='http://127.0.0.1:8000/userside/invoice/',
                cancel_url='http://127.0.0.1:8000/cancel.html',
            )
           

            formatted_data = []

            for service in serializer:
                user_services = service.get('user_service') 
                for individual_service in user_services:
                    service_details = {
                        'id': individual_service.get('id'),
                        'servicename': individual_service.get('service_name'),
                        'price': individual_service.get('price')
                    }
                    formatted_data.append(service_details)
            

            
            service_payment = Payment.objects.create(
                paid_user=user,
                pay_workshop=shop,
                total_price=total_price,
                customer_id=customer.id,  
                stripe_id=checkout_session.id,
                payment_services = formatted_data
                
            )

            return Response({'url':checkout_session.url})
        except Exception as e:
            return Response({'error_message': str(e)})
        
class PaymentInvoice(APIView):
    permission_classes=[IsAuthenticated,OnlyUserPermission]
    @swagger_auto_schema(
    tags=["User Payment"],
    operation_description="User stripe Payment invoice get",
    responses={200: PaymentSerializer, 400: "bad request", 500: "errors"},
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
    def get(self, request):
        try:
            shop_id = request.GET.get('shop_id')
            
            workshop = Workshopdetails.objects.get(id=shop_id)
            
            user = request.user
            payment_invoice = Payment.objects.filter(paid_user=user, pay_workshop=workshop)
            serializer = StripepaymentSerializer(payment_invoice, many=True).data
            return Response(serializer, status=status.HTTP_200_OK)
        except Workshopdetails.DoesNotExist:
            return Response({'Msg': 'Workshop not found'}, status=status.HTTP_404_NOT_FOUND)
        except Payment.DoesNotExist:
            return Response({'Msg': 'Payment details not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Msg': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)



        
from django.shortcuts import render


from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated,OnlyUserPermission])
def display_invoice(request, pk):
    try:
        shop = Workshopdetails.objects.get(id=pk)
        user = request.user  
        
        user_services = ServiceBooking.objects.filter(user=user, workshop=shop)
        
        total_price = user_services.aggregate(total_price=Sum('user_service__price'))['total_price'] or 0
        print(total_price,'totllllllllllll')
        return render(request, 'invoice.html', {
            # 'user_service': user_services,
            # 'total_price': total_price,
        })
    except Workshopdetails.DoesNotExist:
        # Handle the case where the Workshopdetails object does not exist
    #     return render(request, 'error.html')
    # except ServiceBooking.DoesNotExist:
        # Handle the case where the ServiceBooking object does not exist
        return render(request, 'error.html')


# This is your test secret API key.
# stripe.api_key = 'sk_test_51OSGuJSEcQBgekAfTSPIvfZsWJtvO6TvHO92BIAFze6zHwu6IreuSdNWpcaZ7KBPzTiSiXwmSklvrikq3HsoHKSA008kzi794J'

# YOUR_DOMAIN = 'http://localhost:4242'

   
    

    # def post(self,request):
    #     try:
    #         shop_id = request.GET.get('shop_id')
    #         workshop_id = Workshopdetails.objects.get(id=shop_id)
    #         user = request.user
    #         user_services = ServiceBooking.objects.filter(user=user,workshop=workshop_id)
    #         total_price = user_services.aggregate(total_price=Sum('user_service__price'))['total_price'] or 0

    #         host = request.get_host()
    #         paypal_payment = PayPalPaymentsForm(initial={
    #         'business': settings.PAYPAL_RECEIVER_EMAIL,
    #         'amount': total_price,
    #         'invoice': uuid.uuid4(),
    #         'currency_code': 'USD',
    #         'notify_url': f"http://{host}{reverse('paypal-ipn')}",
    #         'return_url': f"http://{host}{reverse('userpayment')}",
    #         'cancel_url': f"http://{host}{reverse('userpayment')}",
    #     })
    #         # paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    #         payment = Payment.objects.create(
    #             paid_user = user,
    #             pay_workshop = workshop_id,
    #             total_price = total_price

    #         )
    #         payment.paypal_payment = str(paypal_payment)  # Assuming a string representation is needed
    #         payment.save()
    #         return Response({'Msg':'Payment success'},status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({'Msg':f'Not found {e}'})
        





# import requests
# from userside.paypal.paypalpayment import PaypalToken
# clientID = os.getenv('PAYPAL_CLIENT_ID')
# clientSecret = os.getenv('PAYPAL_CLIENT_SECRET')
# class CreateOrderViewRemote(APIView):
#     permission_classes = [IsAuthenticated,OnlyUserPermission]

#     def get(self, request):
#         shop_id = request.GET.get('shop_id')
#         workshop_id = Workshopdetails.objects.get(id=shop_id)
#         user = request.user
#         user_services = ServiceBooking.objects.filter(user=user,workshop=workshop_id)
#         total_price = user_services.aggregate(total_price=Sum('user_service__price'))['total_price'] or 0
#         token = PaypalToken(clientID, clientSecret)
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': 'Bearer '+token,
#         }
#         json_data = {
#              "intent": "CAPTURE",
#              "application_context": {
#                  "notify_url": "https://paypal-ipn",
#                  "return_url": "http://127.0.0.1:8000/" + "userside/userpayment/",#change to your doma$
#                  "cancel_url": "http://127.0.0.1:8000/" + "userside/userpayment/", #change to your domain
#                  "brand_name": "Workshopin",
#              },
#              "purchase_units": [
#                  {
#                      "description": "Service Booking",
#                      "amount": {
#                          "currency_code": "USD",
#                          "value": total_price #amount,
#                      },
#                  }
#              ]
#          }
#         response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=headers, json=json_data)
#         order_id = response.json()['id']
#         print(order_id,'orderrrrrrrrrrrrrrrrrrrrr')
#         linkForPayment = response.json()['links'][1]['href']
#         return Response({'linkForPayment': linkForPayment,'order_id':order_id})

# class CaptureOrderView(APIView):
#     permission_classes = [IsAuthenticated,OnlyUserPermission]
#     #capture order aims to check whether the user has authorized payments.
#     def post(self, request):
#         token = request.data.get('token')#the access token we used above for creating an order, or call the function for generating the token
#         captureurl = request.data.get('url')#captureurl = 'https://api.sandbox.paypal.com/v2/checkout/orders/6KF61042TG097104C/capture'#see transaction status
#         headers = {"Content-Type": "application/json", "Authorization": "Bearer "+token}
#         response = requests.post(captureurl, headers=headers)
#         return Response(response.json())