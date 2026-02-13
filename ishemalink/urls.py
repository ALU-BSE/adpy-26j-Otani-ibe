from django.contrib import admin
from django.urls import path
from core.views import SessionLoginView, WhoAmIView, UniversalLogoutView, IshemaLinkTokenView
from security_compliance.views import SendIdentityOTPView, CompleteIdentityVerificationView

def api_status(request):
    from django.http import JsonResponse
    return JsonResponse({"app": "IshemaLink", "security_status": "Hardening In Progress"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/status/', api_status),
    
    path('api/auth/login/session/', SessionLoginView.as_view()),
    path('api/auth/whoami/', WhoAmIView.as_view()),
    path('api/auth/token/obtain/', IshemaLinkTokenView.as_view()),
    
    path('api/identity/send-otp/', SendIdentityOTPView.as_view()),
    path('api/identity/verify-and-complete/', CompleteIdentityVerificationView.as_view()),
]