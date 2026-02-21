from django.urls import path
from .views import (
    ShipmentCreateView, 
    PaymentWebhookView, 
    WhoAmIView,
    UniversalLogoutView,
    DeepHealthCheckView # Add this
)

urlpatterns = [
    path('shipments/create/', ShipmentCreateView.as_view(), name='shipment-create'),
    path('payments/webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('auth/me/', WhoAmIView.as_view(), name='who-am-i'),
    path('auth/logout/', UniversalLogoutView.as_view(), name='logout'),
    
    # Task 3: Production Endpoint
    path('health/deep/', DeepHealthCheckView.as_view(), name='deep-health'),
]