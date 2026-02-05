from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

from domestic.views import (
    update_shipment_status_async_view, 
    get_tariffs_view, 
    clear_tariffs_cache_view,
    get_shipment_manifest_list_with_pagination
)

def api_status_check(request):
    return JsonResponse({"status": "Healthy", "version": "1.0.0"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/status/', api_status_check),
    
    path('api/shipments/<int:shipment_id>/update-status/', update_shipment_status_async_view),
    
    path('api/pricing/tariffs/', get_tariffs_view),
    path('api/admin/cache/clear-tariffs/', clear_tariffs_cache_view),
    
    path('api/shipments/', get_shipment_manifest_list_with_pagination),
]