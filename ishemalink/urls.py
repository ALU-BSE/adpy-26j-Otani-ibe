from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from domestic.views import (
    get_route_analytics,
    update_shipment_status_async_view,
    get_tariffs_view,
    clear_tariffs_cache_view,
    get_shipment_manifest_list_with_pagination
)

def api_status_check(request):
    return JsonResponse({"status": "Healthy", "version": "1.0.0"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/status/", api_status_check),
    path("api/shipments/list/", get_shipment_manifest_list_with_pagination),
    path("api/shipments/<int:shipment_id>/update-status/", update_shipment_status_async_view),
    path("api/pricing/tariffs/", get_tariffs_view),
    path("api/admin/cache/clear-tariffs/", clear_tariffs_cache_view),
    path("api/shipments/analytics/route/", get_route_analytics),
    path("api/", include("domestic.urls")),
]
