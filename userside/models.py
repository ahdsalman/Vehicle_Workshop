# from django.db import models
from userapp.models import User
from django.contrib.gis.db import models
from shopdetails.models import Category,Services,Workshopdetails
# Create your models here.



class Location(models.Model):
    coordinates = models.PointField(srid=4326,null=True,blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)

    @property
    def longitude(self):
        return self.coordinates.x

    @property
    def latitude(self):
        return self.coordinates.y

    def __str__(self) -> str:
        return self.place


class RequestShop(models.Model):
    STATUS = [
        ("PENDING", "PENDING"),
        ("ACCEPTED", "ACCEPTED"),
        ("REJECTED", "REJECTED"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    district = models.CharField(max_length=100,null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    place = models.CharField(max_length=100,null=True,blank=True)
    req_category = models.ManyToManyField(Category,blank=True,related_name='reqcategory')
    req_service = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(default="PENDING", choices=STATUS, max_length=10)
    

    def __str__(self) -> str:
        return f"{self.user.username} location request"




class ServiceBooking(models.Model):

    YEAR =[
        (2010 , 2010),
        (2011 , 2011),
        (2012 , 2012),
        (2013 , 2013),
        (2014 , 2014),
        (2015 , 2015),
        (2016 , 2016),
        (2017 , 2017),
        (2018 , 2018),
        (2019 , 2019),
        (2020 , 2020),
        (2021 , 2021),
        (2022 , 2022),
        (2023 , 2023),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='bookinguser',null=True,blank=True)
    workshop = models.ForeignKey(Workshopdetails,on_delete=models.CASCADE,null=True,blank=True)
    user_service =models.ManyToManyField(Services,blank=True,related_name='bookingservice')
    vehicle_make = models.CharField(max_length=100,null=True,blank=True)
    model_name = models.CharField(max_length=100,null=True,blank=True)
    model_year = models.IntegerField(choices = YEAR,null=True,blank=True)
    user_currentlocation = models.PointField(srid=4326,null=True,blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    @property
    def longitude(self):
        return self.user_currentlocation.x
    
    @property
    def latitude(self):
        return self.user_currentlocation.y
    



class Payment(models.Model):
    paid_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='paid_user',null=True,blank=True)
    pay_workshop = models.ForeignKey(Workshopdetails,on_delete=models.CASCADE,related_name='paymentworkshop',null=True,blank=True)
    payment_services = models.CharField(null=True,blank=True)
    total_price = models.IntegerField(null=True,blank=True)
    customer_id = models.CharField(null=True,blank=True)
    stripe_id = models.CharField(null=True,blank=True)





