# ishemalink_api/urls.py
from django.contrib import admin
from django.urls import path

from core.views import * 
from domestic.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/status/', system_status),
    path('api/prices/', see_prices), 
    
    path('api/register/', register_user),
      path('api/verify-id/', verify_nid), 
    path('api/onboard/', onboard_agent),
    
    path('api/update/<int:pk>/', update_one_package), 
    path('api/bulk-update/', update_many_packages),
    
    path('api/list-packages/', list_shipments),
]