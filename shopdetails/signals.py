# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from shopdetails.models import Notification
# from shopdetails.tasks import send_notification



# @receiver(post_save, sender=Notification)
# def create_notification(sender, instance, created, **kwargs):
#     if created:
#         notification = Notification.objects.get()