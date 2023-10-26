from django.urls import path,include
from userapp.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView

urlpatterns = [
    path('register/',UserRegisterView.as_view(),name='register'),
    path('phone/',PhoneVarify.as_view(),name='phone'),
    path('otp/',Otpverification.as_view(),name='otp'),
    path('userlogin/',UserLoginView.as_view(),name='login'),
    
]


# urlpatterns = [
#     path('gettoken/',TokenObtainPairView.as_view(),name='token_obtain'),
#     path('refreshtoken/',TokenRefreshView.as_view(),name='token_refresh'),
#     path('varifytoken/',TokenVerifyView.as_view(),name='token_varify'),
    
# ]