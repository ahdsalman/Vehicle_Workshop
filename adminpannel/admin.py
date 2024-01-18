from django.contrib import admin
from adminpannel.models import Notifications
# Register your models here.

@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display=['noticed_shop']
