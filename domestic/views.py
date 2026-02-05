from django.http import JsonResponse
from django.core.cache import cache
from django.core.paginator import Paginator
from .models import PackageShipmentTrackingModel
import asyncio
import datetime

async def send_sms_notification_to_farmer_asynchronously(phone_number: str, message_content: str) -> bool:
    print(f"DEBUG: Connecting to Rwanda SMS Gateway for {phone_number}...")
    await asyncio.sleep(3) # The 3-second delay
    print(f"DEBUG: SMS sent successfully: {message_content}")
    return True

async def update_shipment_status_async_view(request, shipment_id):
    try:
        the_shipment_to_update = await PackageShipmentTrackingModel.objects.aget(id=shipment_id)
    except PackageShipmentTrackingModel.DoesNotExist:
        return JsonResponse({"error": "Shipment not found"}, status=404)

    the_shipment_to_update.current_package_status_right_now = "ARRIVED_AT_HUB"
    await the_shipment_to_update.asave()

    asyncio.create_task(send_sms_notification_to_farmer_asynchronously(
        the_shipment_to_update.receiver_phone_number_for_sms, 
        f"Package {the_shipment_to_update.tracking_number_generated_by_system} arrived at Nyabugogo!"
    ))

    return JsonResponse({
        "message": "Status update started!",
        "new_status": "ARRIVED_AT_HUB",
        "note": "Wait 3 seconds and check your terminal for the SMS log."
    })

def get_tariffs_view(request):
    the_cached_rates = cache.get("ishemalink_rates")
    
    if the_cached_rates:
        print("DEBUG: Cache Hit! Serving prices from memory.")
        response = JsonResponse(the_cached_rates)
        response["X-Cache-Hit"] = "TRUE" 
        return response
    
    print("DEBUG: Cache Miss! Fetching from database...")
    rates_data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "zones": {
            "Zone_1_Kigali": "1500 RWF",
            "Zone_2_Provinces": "2500 RWF"
        }
    }
    
    cache.set("ishemalink_rates", rates_data, 600) 
    
    response = JsonResponse(rates_data)
    response["X-Cache-Hit"] = "FALSE"
    return response

def clear_tariffs_cache_view(request):
    cache.delete("ishemalink_rates")
    return JsonResponse({"message": "Tariff cache has been cleared successfully!"})

def get_shipment_manifest_list_with_pagination(request):
    the_page_number = request.GET.get('page', 1)
    the_status_filter = request.GET.get('status')
    
    all_shipments = PackageShipmentTrackingModel.objects.all().order_by('-id')
    
    if the_status_filter:
        all_shipments = all_shipments.filter(current_package_status_right_now=the_status_filter)
    
    paginator = Paginator(all_shipments, 5) 
    page_obj = paginator.get_page(the_page_number)
    
    manifest_data = []
    for s in page_obj:
        manifest_data.append({
            "tracking_code": s.tracking_number_generated_by_system,
            "status": s.current_package_status_right_now,
            "updated": "Just now"
        })
        
    return JsonResponse({
        "meta": {
            "total_count": paginator.count,
            "current_page": page_obj.number,
            "next_link": f"/api/shipments/?page={page_obj.next_page_number()}" if page_obj.has_next() else None
        },
        "data": manifest_data
    })