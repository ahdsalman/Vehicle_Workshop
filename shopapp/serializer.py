from rest_framework import serializers
from shopapp.models import *
from userapp.models import *



class ShopOwnerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=WorkshopOwner
        fields=['shopname','city','phone']
    # Add your WorkshopOwner-specific fields here
    
        # Add more custom validation logic for WorkshopOwner registration if needed

        
    
class EmailSerializer(serializers.Serializer):
    email=models.EmailField(max_length=100)


