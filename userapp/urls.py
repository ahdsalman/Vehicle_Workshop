from django.urls import path,include
from userapp.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView

urlpatterns = [
    path('register/',UserRegisterView.as_view(),name='register'),
    path('phone/',PhoneVarify.as_view(),name='phone'),
    path('otp/',Otpverification.as_view(),name='otp'),
    path('userlogin/',UserLoginView.as_view(),name='login'),
    path('changepassword/',ChangeUserPassword.as_view(),name='changepassword'),
    path('forgotpassword/',ForgotPassword.as_view(),name='forgotpassword'),
    path('google/',GoogleSocialAuth.as_view(),name='social_auth'),

    # resend otp
    # google auth
    # location
    
]
