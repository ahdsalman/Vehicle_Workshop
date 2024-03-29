from rest_framework import serializers
from userapp.models import User,Profile
from userside.models import ServiceBooking
from shopdetails.models import Workshopdetails,Services,Category


class UserProfileSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Profile
        fields = ['phone', 'city', 'pincode']
        ref_name = 'AdminPanelUserProfileSerializer'


class UserProfileListSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username','is_active','is_shopowner','profile']



class ServiceListAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['service_name','price']

from adminpannel.models import Notifications

class ShopDetailRetriveAdminSerializer(serializers.ModelSerializer):
    
    services = ServiceListAdminSerializer(many=True)
    
    class Meta:
        model = Workshopdetails
        fields = [
            "id",
            'shopname',
            'phone',
            'branch',
            'category',
            'services',
            'id_proof',
            'is_approved',
            'is_oppen',
            'country',
            'state',
            'district',
            'city',
            'place',
            'shop_coordinates'
           
        ]

    def update(self, instance, validated_data):
        instance.shop_coordinates = validated_data.get('shop_coordinates', instance.shop_coordinates)
        instance.is_approved=validated_data.get('is_approved',instance.is_approved)
        instance.save()
        return instance

class ShopSearchAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshopdetails
        fields = '__all__'



class CategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BookingAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceBooking
        fields = ['user','workshop']



class ShopBookingAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceBooking
        fields = '__all__'