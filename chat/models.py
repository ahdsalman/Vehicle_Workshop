from django.db import models
from userapp.models import User
from userside.models import ServiceBooking

    

class Message(models.Model):
    room_name = models.ForeignKey(ServiceBooking,on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="uploads/", null=True, blank=True)

    class Meta:
        db_table = "chat_message"
        ordering = ("timestamp",)