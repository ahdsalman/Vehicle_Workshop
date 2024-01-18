from django.urls import path,include
from .views import MessageList
from chat.routing import websocket_urlpatterns

urlpatterns = [
    path('ws/', include(websocket_urlpatterns)),

    path("sendmessage/", MessageList.as_view(), name="send-message"),
]


