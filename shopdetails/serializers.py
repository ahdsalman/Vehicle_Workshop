from rest_framework import serializers
from shopdetails.models import Workshopdetails,Services,Category
from userside.models import Location
from userapp.models import User,Profile
from rest_framework.response import Response


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['service_name','price']



class ShopDetailRetriveSerializer(serializers.ModelSerializer):
    
    services = ServiceSerializer(many=True)
    
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


class ShopDetailSerializer(serializers.ModelSerializer):
    
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Services.objects.all())
    
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
            'country',
            'state',
            'district',
            'city',
            'place',
            'shop_coordinates'
           
        ]
        

    def update(self, instance, validated_data):
        instance.shopname = validated_data.get('shopname', instance.shopname)
        instance.city = validated_data.get('city', instance.city)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.id_proof = validated_data.get('id_proof', instance.id_proof)
        instance.country = validated_data.get('country', instance.country)
        instance.state = validated_data.get('state', instance.state)
        instance.district = validated_data.get('district', instance.district)
        instance.place= validated_data.get('place', instance.place)
        instance.shop_coordinates = validated_data.get('shop_coordinates', instance.shop_coordinates)

        if instance.id_proof:
            instance.is_approved=False
        

        category_data = validated_data.get('category')
        if category_data:
            category_instance = Category.objects.get(pk=category_data.id)
            instance.category = category_instance


        if 'services' in validated_data:
            service_data = validated_data.pop('services', None)

            current_service =instance.services.values_list('id',flat=True)
            for service_id in current_service:
                if service_id not in service_data:
                    instance.services.remove(service_id)

            for service_item in service_data:
                instance.services.add(service_item)

       
        


        instance.save()
        return instance

            

