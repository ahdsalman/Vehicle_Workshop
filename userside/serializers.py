from rest_framework import serializers
from userside.models import Location,RequestShop
from shopdetails.models import Workshopdetails
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
            "req_service"
        )
        read_only_fields = ('user',) 

        

class ShopShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshopdetails
        fields = '__all__'