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
    path('adminshopsearch/',ShopsearchView.as_view(),name='search'),
    path('adminshopretrive/',ShopsAdminRetriveView.as_view(),name='shopretrive'),
    path('requestedshops/',RequestShopListAdminView.as_view(),name='reuestedshops'),
    path('requestupdate/<int:pk>/',RequestShopUpdateAdminView.as_view(),name='requestupdate'),


    path('adminservices/',SeriveceListAdminView.as_view(),name='adminservices'),
    path('admincategory/',CategoryAdminView.as_view(),name='admincategory'),
    path('adminbookinglist/',BookingLIstAdminView.as_view(),name='adminbooking'),
    path('adminbookingshop/',BookingshopAdminView.as_view(),name='bookingshop'),


    path('sendmail/',SendApprovalmail.as_view(),name='sendbulkemail'),


    
]