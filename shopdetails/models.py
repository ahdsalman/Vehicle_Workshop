from django.contrib.gis.db import models
from userapp.models import User
# Create your models here.


class Services(models.Model):
    service_name = models.CharField(max_length=100)
    price = models.IntegerField()
    def __str__(self) :
        return self.service_name

    
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
    services = models.ManyToManyField(Services,blank=True,related_name='services')
    id_proof = models.FileField(upload_to='id_proof',null=True,blank=True)
    # location = models.ForeignKey(Location,on_delete=models.CASCADE,null=True,blank=True)
    is_approved = models.BooleanField(default=False,null=True, blank=True)
    is_oppen = models.BooleanField(default=True,null=True,blank=True)
    
    shop_coordinates = models.PointField(geography=True,null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)

    # def __str__(self) :
    #     return self.shopname
    

# class Notification(models.Model):
#     notification_shop = models.ForeignKey(Workshopdetails,on_delete=models.CASCADE)
#     notification_location = models.CharField(max_length=250,null=True)
