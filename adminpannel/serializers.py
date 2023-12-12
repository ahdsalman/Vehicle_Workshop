from rest_framework import serializers
from userapp.models import User,Profile
from shopdetails.models import Workshopdetails,Services


class UserProfileSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Profile
        fields = ['phone', 'city', 'pincode']


class UserProfileListSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username','is_active','is_shopowner','profile']



class ServiceListAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['service_name','price']



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
