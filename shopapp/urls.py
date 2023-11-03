from django.urls import path,include
from shopapp.views import *





urlpatterns = [
    path('shopregister/',WorkshopOwnerRegister.as_view(),name='shopregister'),
    path('emailverify/',EmailVerify.as_view(),name='emailverify'),
    path('otpverify/',EmailOtpVerify.as_view(),name='otpverify'),
    # path('shoplogin/',WorkshopOwnerLogin.as_view(),name='shoplogin'),
    
]