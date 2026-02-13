from django.contrib import admin
from django.urls import path
from core.views import SessionLoginView, WhoAmIView, UniversalLogoutView, IshemaLinkTokenView
from domestic.views import (
    update_shipment_status_async_view, 
    get_tariffs_view, 
    get_shipment_manifest_list_with_pagination
)
from security_compliance.views import (
    SendIdentityOTPView, 
    CompleteIdentityVerificationView, 
    ViewSecureProfileView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/shipments/<int:shipment_id>/update-status/', update_shipment_status_async_view),
    path('api/pricing/tariffs/', get_tariffs_view),
    path('api/shipments/', get_shipment_manifest_list_with_pagination),
    
    path('api/auth/login/session/', SessionLoginView.as_view()),
    path('api/auth/whoami/', WhoAmIView.as_view()),
    path('api/auth/token/obtain/', IshemaLinkTokenView.as_view()),
    path('api/auth/logout/', UniversalLogoutView.as_view()),
    
    path('api/identity/send-otp/', SendIdentityOTPView.as_view()),
    path('api/identity/verify-and-complete/', CompleteIdentityVerificationView.as_view()),
    path('api/identity/my-secure-profile/', ViewSecureProfileView.as_view()),
]