from celery import shared_task
from django.core.mail import EmailMessage
from shopdetails.models import Workshopdetails
from userside.models import User
from adminpannel.models import Notifications
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

    
@shared_task(bind=True)
def send_mail_to_users(self, subject, message, sender, recipient_emails):
    for recipient_email in recipient_emails:
        email = EmailMessage(subject, message, sender, to=[recipient_email])
        email.send()
    return "Successful"
    



@shared_task(bind=True)
def send_notifications_to_users(self,name,location,content):

    users=User.objects.all()
    for user in users:
        Notifications.objects.create(
            user = user,
            noticed_shop=name,
            noticed_location=location,
            content=content,

        )
    
    return "Notifications sent to all users"

   
   
    


