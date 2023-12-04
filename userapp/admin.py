from django.contrib import admin
from userapp.models import*
from shopdetails.models import*
from userside.models import *
from django.contrib.gis.admin import OSMGeoAdmin
# Register your models here.

class userAdmin(admin.ModelAdmin):
    list_display=('id','first_name','username')
admin.site.register(User,userAdmin)

@admin.register(Workshopdetails)
class Workshopdetails(OSMGeoAdmin):
    list_display = ('id','shopname','city','place','shop_coordinates')


class userAdmin(admin.ModelAdmin):
    list_display = ('id','category')
admin.site.register(Category,userAdmin)


@admin.register(Profile)
class Profile(OSMGeoAdmin):
    list_display =['id','user','usr_location']

class userAdmin(admin.ModelAdmin):
    list_display =('id','service')
admin.site.register(Services,userAdmin)

@admin.register(Location)
class LocationAdmin(OSMGeoAdmin):
    list_display = ('city','district','coordinates','country','state')
    
admin.site.register(RequestShop)

