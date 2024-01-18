from rest_framework import serializers
from .models import Message
from shopdetails.models import Workshopdetails

class MessageSerializer(serializers.ModelSerializer):
       class Meta:
           model = Message
           fields = ('id', 'username','message','timestamp','file')
           read_only_fields = ('id', 'timestamp')




class UserchatSerializer(serializers.ModelSerializer):
      class meta:
            model = Workshopdetails
            fields = ['shopname']