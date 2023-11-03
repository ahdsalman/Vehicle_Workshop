from django.contrib import admin
from userapp.models import*
from shopapp.models import*
# Register your models here.

admin.site.register(User)
admin.site.register(WorkshopOwner)