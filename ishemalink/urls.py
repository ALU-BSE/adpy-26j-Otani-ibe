from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import SessionLoginView, WhoAmIView, UniversalLogoutView, IshemaLinkTokenView
from security_compliance.views import SendOTPView, VerifyNIDView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/token/obtain/', IshemaLinkTokenView.as_view()),
    path('api/auth/token/refresh/', TokenRefreshView.as_view()),
    path('api/auth/login/session/', SessionLoginView.as_view()),
    path('api/auth/logout/', UniversalLogoutView.as_view()),
    path('api/auth/whoami/', WhoAmIView.as_view()),
    
    path('api/identity/send-otp/', SendOTPView.as_view()),
    path('api/identity/kyc/nid/', VerifyNIDView.as_view()),
]