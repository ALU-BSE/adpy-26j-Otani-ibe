import uuid
import datetime
from django.http import JsonResponse
from django.core.cache import cache
from django.db import transaction, connections
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from .models import Shipment

from .serializers import ShipmentCreateSerializer, PaymentWebhookSerializer
from .models import Shipment, PaymentRecord
from .services import BookingService

from rest_framework.renderers import JSONRenderer # Add this import

class DeepHealthCheckView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer] # Add this line to force JSON only

    def get(self, request):
        health_status = {
            "status": "Healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "services": {
                "database": "Unknown",
                "cache_redis": "Unknown"
            }
        }

        # Check Database
        try:
            connections['default'].cursor()
            health_status["services"]["database"] = "Healthy"
        except Exception as e:
            health_status["status"] = "Unhealthy"
            health_status["services"]["database"] = f"Error: {str(e)}"

        # Check Redis (Cache)
        try:
            cache.set("health_check_ping", "pong", timeout=10)
            if cache.get("health_check_ping") == "pong":
                health_status["services"]["cache_redis"] = "Healthy"
            else:
                raise Exception("Cache integrity failed")
        except Exception as e:
            health_status["status"] = "Unhealthy"
            health_status["services"]["cache_redis"] = f"Error: {str(e)}"

        http_status = status.HTTP_200_OK if health_status["status"] == "Healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health_status, status=http_status)

# --- KEEPING YOUR EXISTING VIEWS ---
class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "username": request.user.username,
            "user_type": getattr(request.user, 'user_type', 'N/A'),
            "is_verified": getattr(request.user, 'is_identity_verified', False)
        })

class UniversalLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class ShipmentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ShipmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            service = BookingService()
            try:
                shipment = service.create_unified_booking(request.user, serializer.validated_data)
                return Response({
                    "tracking_code": str(shipment.tracking_code),
                    "tariff": str(shipment.tariff_amount),
                    "status": shipment.payment_status,
                    "momo_id": shipment.payment.transaction_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentWebhookView(APIView):
    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)
        if serializer.is_valid():
            tx_id = serializer.validated_data.get("transaction_id")
            momo_status = serializer.validated_data.get("status")
            try:
                with transaction.atomic():
                    payment = PaymentRecord.objects.select_for_update().get(transaction_id=tx_id)
                    shipment = payment.shipment
                    if momo_status == "SUCCESS" and not payment.is_confirmed:
                        payment.is_confirmed = True
                        payment.save()
                        shipment.ebm_signature = f"RRA-EBM-{uuid.uuid4().hex[:10].upper()}"
                        shipment.payment_status = "PAID"
                        shipment.save()
                        return Response({"message": "Confirmed", "ebm": shipment.ebm_signature}, status=status.HTTP_200_OK)
                    else:
                        shipment.payment_status = "FAILED"
                        shipment.save()
                        return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
            except PaymentRecord.DoesNotExist:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- TASK 5 FUNCTIONS ---
def get_tariffs_view(request):
    the_cached_rates = cache.get("ishemalink_rates")
    if the_cached_rates:
        response = JsonResponse(the_cached_rates)
        response["X-Cache-Hit"] = "TRUE" 
        return response
    rates_data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "zones": {"Zone_1_Kigali": "1500 RWF", "Zone_2_Provinces": "2500 RWF"}
    }
    cache.set("ishemalink_rates", rates_data, 600) 
    response = JsonResponse(rates_data)
    response["X-Cache-Hit"] = "FALSE"
    return response

def clear_tariffs_cache_view(request):
    cache.delete("ishemalink_rates")
    return JsonResponse({"message": "Tariff cache cleared!"})

def update_shipment_status_async_view(request, shipment_id):
    return JsonResponse({"message": f"Status update for {shipment_id} initiated."})

def get_shipment_manifest_list_with_pagination(request):
    return JsonResponse({"manifests": [], "count": 0})
def get_route_analytics(request):
    """Task 5: Aggregated data for MINICOM planning"""
    # Optimized query using GROUP BY
    stats = Shipment.objects.values('origin', 'destination').annotate(
        total_weight=Sum('weight_kg')
    ).order_by('-total_weight')
    
    return JsonResponse({"route_intelligence": list(stats)})