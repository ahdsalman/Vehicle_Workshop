from django.urls import path,include
from shopdetails.views import*



urlpatterns = [
    path('addservice/',AddServicesCreateView.as_view(),name='addservice'),
    # path('shopdetails/',Shopdetails.as_view(),name='shopdetails'),
    path('shopdetails/',ShopdetailsCreateUpdateView.as_view(),name='shopdetailsupdate'),
    path('shopcurrentlocation/',ShopCurrentLocationView.as_view(),name='shop_currentlocation')
]