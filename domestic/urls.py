from django.urls import path
from .views import (
    LiveTrackingView,
    AdminDashboardView,
    BroadcastNotificationView,
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
    path('tracking/<str:tracking_code>/live/', LiveTrackingView.as_view(), name='live-tracking'),
    path('admin/dashboard/summary/', AdminDashboardView.as_view(), name='dashboard-summary'),
    path('notifications/broadcast/', BroadcastNotificationView.as_view(), name='broadcast'),
]