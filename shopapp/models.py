from django.db import models
from userapp.models import User
# Create your models here.

class WorkshopOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='workshopowner')
    shopname=models.CharField(max_length=255,null=True)
    city = models.CharField(max_length=255,null=True)
    phone = models.CharField(max_length=13,unique=True, null=True)
    is_approved = models.BooleanField(default=False)

    

    
    

