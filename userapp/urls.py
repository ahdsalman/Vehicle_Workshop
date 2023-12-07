from django.urls import path,include
from userapp.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView

urlpatterns = [
    path('register/',UserRegisterCreateView.as_view(),name='register'),
    path('phone/',PhoneVarifyView.as_view(),name='phone'),
    path('otp/',OtpverificationView.as_view(),name='otp'),
    path('userlogin/',UserLoginView.as_view(),name='login'),
    path('changepassword/',ChangeUserPasswordView.as_view(),name='changepassword'),
    path('forgotpassword/',ForgotPasswordView.as_view(),name='forgotpassword'),
    path('google/',GoogleSocialAuthUserView.as_view(),name='socialauth'),
    path('profile/',UserProfileView.as_view(),name='profile'),

    # resend otp
    # google auth
    # location
    
]
