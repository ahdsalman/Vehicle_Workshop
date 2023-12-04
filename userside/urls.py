from django.urls import path,include
from userside.views import *

urlpatterns = [
    path('currentlocation/',CurrentLocation.as_view(),name='currentlocation'),
    path('shopsearch/',Shopsearch.as_view(),name='shopsearch'),
    path('shopshow/',ShopShow.as_view(),name='shopshow'),
    # path('shopshow/<int:pk>/',ShopShow.as_view(),name='shopselect'),
    
]
