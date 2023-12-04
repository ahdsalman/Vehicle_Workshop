from django.urls import path,include
from shopdetails.views import*



urlpatterns = [
    path('addservice/',AddServices.as_view(),name='addservice'),
    # path('shopdetails/',Shopdetails.as_view(),name='shopdetails'),
    path('shopdetails/<int:pk>/',Shopdetails.as_view(),name='shopdetailsupdate')
]