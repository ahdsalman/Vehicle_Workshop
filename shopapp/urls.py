from django.urls import path,include
from shopapp.views import *





urlpatterns = [
    path('shopregister/',WorkshopOwnerRegister.as_view(),name='shopregister'),
    path('emailverify/',EmailVerify.as_view(),name='emailverify'),
    path('otpverify/',EmailOtpVerify.as_view(),name='otpverify'),
    path('updatepassword/',UpdateOwnerPassword.as_view(),name='updatepassword'),
    path('resetpassword/',ResetOwnerpassword.as_view(),name='resetpassword'),
    path('shoplogin/',WorkshopOwnerLogin.as_view(),name='shoplogin'),

    
    
]