from django.db import models
from shopdetails.models import Workshopdetails
from userside.models import User
# Create your models here.

class Notifications(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    noticed_shop = models.CharField()
    noticed_location = models.CharField()
    content = models.CharField()
    

    def __str__(self) :
        return self.noticed_shop
    

