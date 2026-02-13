from django.contrib import admin
from django.urls import path
from core.views import SessionLoginView, WhoAmIView, UniversalLogoutView, IshemaLinkTokenView
from security_compliance.views import (
    SendIdentityOTPView, 
    CompleteIdentityVerificationView, 
    ViewSecureProfileView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/login/session/', SessionLoginView.as_view()),
    path('api/auth/whoami/', WhoAmIView.as_view()),
    path('api/auth/token/obtain/', IshemaLinkTokenView.as_view()),
    path('api/auth/logout/', UniversalLogoutView.as_view()),
    
    path('api/identity/send-otp/', SendIdentityOTPView.as_view()),
    path('api/identity/verify-and-complete/', CompleteIdentityVerificationView.as_view()),
    path('api/identity/my-secure-profile/', ViewSecureProfileView.as_view()),
]