from django.contrib.gis.db import models
from userapp.models import User
# Create your models here.


class Services(models.Model):
    service = models.CharField(max_length=100)
    price = models.IntegerField()
    def __str__(self) :
        return self.service

    
class Category(models.Model):
   category = models.CharField(max_length=100,null=True, blank=True)

   def __str__(self) :
       return self.category

    


class Workshopdetails(models.Model):
    shop_owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name='workshops')
    shopname=models.CharField(max_length=255,null=True)
    phone = models.CharField(max_length=13,unique=True, null=True)
    branch = models.CharField(max_length=100,null=True,blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    service = models.ManyToManyField(Services,blank=True,related_name='services')
    # location = models.ForeignKey(Location,on_delete=models.CASCADE,null=True,blank=True)
    is_approved = models.BooleanField(default=False,null=True, blank=True)
    
    shop_coordinates = models.PointField(geography=True,null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)

    
    