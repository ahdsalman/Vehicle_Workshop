# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from shopdetails.models import Workshopdetails
import json

@receiver(post_save, sender=Workshopdetails)
def send_notification_on_shop_registration(sender, instance,created, **kwargs):
    if created:
        if instance.is_approved:
            channel_layer = get_channel_layer()
            id =str(instance.id)
            content =id+instance.shopname
            async_to_sync(channel_layer.group_send)('message',{'type':'send Notification','notification':content})
