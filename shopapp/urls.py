from django.urls import path,include
from shopapp.views import *





urlpatterns = [
    path('shopregister/',WorkshopOwnerCreateView.as_view(),name='shopregister'),
    path('emailverify/',EmailVerifyView.as_view(),name='emailverify'),
    path('otpverify/',EmailOtpVerifyView.as_view(),name='otpverify'),
    path('gsocial/',GoogleSocialAuthOwnerView.as_view(),name='gsocialauth'),
    path('ownerprofile/',OwnerProfileView.as_view(),name='ownerprofile'),
    # path('updatepassword/',UpdateOwnerPassword.as_view(),name='updatepassword'),
    # path('resetpassword/',ResetOwnerpassword.as_view(),name='resetpassword'),
    
    
    
]