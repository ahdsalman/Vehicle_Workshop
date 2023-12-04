# from django.db import models
from userapp.models import User
from django.contrib.gis.db import models
from shopdetails.models import Category,Services
# Create your models here.



class Location(models.Model):
    coordinates = models.PointField(srid=4326)
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


