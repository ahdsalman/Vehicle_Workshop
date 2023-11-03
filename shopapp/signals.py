from django.db.models.signals import post_save
from django.dispatch import receiver
from userapp.models import User
from shopapp.models import WorkshopOwner



@receiver(post_save, sender=User)
def create_shop_owner(sender, instance, created, **kwargs):
    if created:
        WorkshopOwner.objects.create(user=instance)