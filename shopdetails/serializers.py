from rest_framework import serializers
from shopdetails.models import Workshopdetails,Services,Category
from userside.models import Location
from userapp.models import User,Profile



class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'






class ShopDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workshopdetails
        fields = [
            "id",
            'shopname',
            'phone',
            'branch',
            'category',
            'service',
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
        instance.is_approved = True

        category_data = validated_data.get('category')
        if category_data:
            category_instance = Category.objects.get(pk=category_data.id)
            instance.category = category_instance


        if 'service' in validated_data:
            service_data = validated_data.pop('service', None)
            for service_item in service_data:
                instance.service.add(service_item)

        instance.save()
        return instance

            

