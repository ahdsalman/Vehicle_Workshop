from django.urls import path,include
from userside.views import *

urlpatterns = [
    # path('usercurrentlocation/',UserCurrentLocation.as_view(),name='user_currentlocation'),
    path('shopsearch/',ShopsearchRetriveRequestView.as_view(),name='shopsearch'),
    path('shopretrive/',ShopsRetriveView.as_view(),name='shopretrive'),
    path('shopget/<int:pk>/',UserShopRetriveView.as_view(),name='shopselect'),
    
]