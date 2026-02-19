from django.urls import path
from .views import ShipmentCreateView, PaymentWebhookView, ShipmentTrackingView
from .views import (
    ShipmentCreateView, 
    PaymentWebhookView, 
    ShipmentTrackingView,
    UniversalLogoutView,
    WhoAmIView
)

urlpatterns = [
    path('shipments/create/', ShipmentCreateView.as_view(), name='shipment-create'),
    path('payments/webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('tracking/<str:tracking_code>/live/', ShipmentTrackingView.as_view(), name='shipment-tracking'),    
    path('auth/logout/', UniversalLogoutView.as_view(), name='logout'),
    path('auth/me/', WhoAmIView.as_view(), name='who-am-i'),
]
