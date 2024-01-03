from rest_framework import serializers
from userside.models import Location,RequestShop,ServiceBooking,Payment
from shopdetails.models import Workshopdetails,Services
from rest_framework_gis.serializers import GeoFeatureModelListSerializer



class LocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            "country",
            "state",
            "district",
            "city",
            "place", 
            "coordinates"
        )
        def update(self, instance, validated_data):
            instance.country=validated_data.get('country', instance.country)
            instance.state=validated_data.get('state', instance.state)
            instance.district=validated_data.get('district', instance.district)
            instance.city=validated_data.get('city', instance.city)
            instance.place=validated_data.get('place', instance.place)
            instance.coordinates=validated_data.get('coordinates', instance.coordinates)
            instance.save()
            return instance



class RequestedShopListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestShop
        fields = (
            "user",
            "country",
            "state",
            "district",
            "place",
            "city",
            "req_category",
            "req_service",
            "status"
        )
        read_only_fields = ('user',) 

        

# class ShopSearchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Workshopdetails
#         fields = '__all__'


class ServiceBookingSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()

    class Meta:
        model = ServiceBooking
        fields = ['id', 'user_service', 'vehicle_make', 'model_name', 'model_year',
                  'user_currentlocation', 'country', 'state', 'district', 'city', 'place',
                  'created_date', 'created_time']

    # Methods to get date and time separately
    def get_created_date(self, obj):
        return obj.created_at.date() if obj.created_at else None

    def get_created_time(self, obj):
        return obj.created_at.time() if obj.created_at else None



    def update(self, instance,validated_data):

        instance.user_service= validated_data.get('user_service',instance.user_service)

        instance.save()
        return instance
        
class PaymentServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['id','service_name','price']


class PaymentSerializer(serializers.ModelSerializer):
    user_service = PaymentServiceSerializer(many=True)
    class Meta:
        model = ServiceBooking
        fields =['user_service']


class StripepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['paid_user','pay_workshop','payment_services','total_price','customer_id','stripe_id']