from django.urls import path,include
from adminpannel.views import *


urlpatterns = [
    path('adminlogin/',AdminLoginView.as_view(),name='adminlogin'),
    path('userlist/',UserListAdminView.as_view(),name='userlist'),
    path('shoplist/',ShopOwnerListAdminView.as_view(),name='shoplist'),
    path('shopdetails/',ShopdetailsListView.as_view(),name='shopdetails'),
    path('userupdate/<int:pk>/',UserUpdateAdminView.as_view(),name='useruapdate'),
    path('shopupdate/<int:pk>/',ShopUpdateAdminView.as_view(),name='shopupdate'),
    path('location/',LocationAdminView.as_view(),name='location'),
    path('locationupdate/<int:pk>/',AddLocationAdminView.as_view(),name='newlocation'),
]