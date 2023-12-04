from django.db.models.signals import post_save
from django.dispatch import receiver
from userapp.models import User
from shopdetails.models import Workshopdetails,Services



@receiver(post_save, sender=User)
def create_shop_owner(sender, instance, created, **kwargs):
    if created:
        if instance.is_shopowner:
            Workshopdetails.objects.create(shop_owner=instance)
            




# @receiver(post_save,sender=User)
# def create_service(sender, instance, created, **kwargs):
#     if created:
#         if instance.is_shopowner:
#             Services.objects.create(service=instance)