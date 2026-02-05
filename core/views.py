from django.http import JsonResponse
from .models import PackageShipmentTrackingModel
from .notifications import send_sms_notification_to_farmer_asynchronously
import asyncio

async def update_shipment_status_async_view(request, shipment_id):
    try:
        the_shipment = await PackageShipmentTrackingModel.objects.aget(id=shipment_id)
    except PackageShipmentTrackingModel.DoesNotExist:
        return JsonResponse({"error": "Shipment not found"}, status=404)

    the_shipment.current_package_status_right_now = "ARRIVED_AT_HUB"
    await the_shipment.asave()

    asyncio.create_task(send_sms_notification_to_farmer_asynchronously(
        the_shipment.receiver_phone_number_for_sms, 
        f"Your package {the_shipment.tracking_number_generated_by_system} has arrived at Nyabugogo!"
    ))

    return JsonResponse({
        "message": "Status update started!",
        "new_status": "ARRIVED_AT_HUB",
        "instruction": "Check your terminal. The 'SMS Sent' message will appear in 3 seconds."
    })