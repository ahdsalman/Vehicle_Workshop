from django.urls import path,include
from userside.views import *

urlpatterns = [
    path('usercurrentlocation/',UserCurrentLocation.as_view(),name='user_currentlocation'),
    path('shopsearch/',ShopsearchRetriveRequestView.as_view(),name='shopsearch'),
    path('shopretrive/',ShopsRetriveView.as_view(),name='shopretrive'),
    path('shopget/<int:pk>/',UserShopRetriveView.as_view(),name='shopselect'),
    path('servicebooking/',UserServiceBooking.as_view(),name='servicebooking'),
    path('userpayment/',UserPaymentView.as_view(),name='userpayment'),
    path('paymentinvoice/',PaymentInvoice.as_view(),name='invoice'),

    # path('invoice/<int:pk>/', display_invoice, name='invoice'),
    # path('paypal/create/order', CreateOrderViewRemote.as_view(), name='ordercreate'),
    # path('paypal/capture/order', CaptureOrderView.as_view(), name='captureorder')
    
]

# from django.urls import path, include, re_path
# from paypal.standard.ipn import views


