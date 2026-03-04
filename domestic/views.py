import uuid
import datetime
from django.http import JsonResponse
from django.core.cache import cache
from django.db import transaction, connections
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, AllowAny
from django.db.models import Sum
from .models import Shipment

from .serializers import ShipmentCreateSerializer, PaymentWebhookSerializer
from .models import Shipment, PaymentRecord
from .services import BookingService

from rest_framework.renderers import JSONRenderer

class DeepHealthCheckView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer] 

    def get(self, request):
        health_status = {
            "status": "Healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "services": {
                "database": "Unknown",
                "cache_redis": "Unknown"
            }
        }

        try:
            connections['default'].cursor()
            health_status["services"]["database"] = "Healthy"
        except Exception as e:
            health_status["status"] = "Unhealthy"
            health_status["services"]["database"] = f"Error: {str(e)}"

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
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)
        if serializer.is_valid():
            tx_id = serializer.validated_data.get("transaction_id")
            momo_status = serializer.validated_data.get("status")
            try:
                with transaction.atomic():
                    payment = PaymentRecord.objects.select_for_update().get(transaction_id=tx_id)
                    shipment = payment.shipment
                    if payment.is_confirmed:
                        return Response({
                            "message": "Payment already confirmed, ignoring callback",
                            "shipment_status": shipment.payment_status,
                            "tracking_code": str(shipment.tracking_code)
                        }, status=status.HTTP_200_OK)
                    if momo_status == "SUCCESS":
                        payment.is_confirmed = True
                        payment.save()
                        shipment.ebm_signature = f"RRA-EBM-{uuid.uuid4().hex[:10].upper()}"
                        shipment.payment_status = "PAID"
                        shipment.save()
                        return Response({
                            "message": "Confirmed",
                            "ebm": shipment.ebm_signature,
                            "shipment_status": shipment.payment_status,
                            "tracking_code": str(shipment.tracking_code)
                        }, status=status.HTTP_200_OK)
                    else:
                        shipment.payment_status = "FAILED"
                        shipment.save()
                        return Response({
                            "message": "Payment failed",
                            "shipment_status": shipment.payment_status,
                            "tracking_code": str(shipment.tracking_code)
                        }, status=status.HTTP_400_BAD_REQUEST)
            except PaymentRecord.DoesNotExist:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    stats = Shipment.objects.values('origin', 'destination').annotate(
        total_weight=Sum('weight_kg')
    ).order_by('-total_weight')
    
    return JsonResponse({"route_intelligence": list(stats)})

class LiveTrackingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, tracking_code):
        try:
            from domestic.models import Shipment
            shipment = Shipment.objects.get(tracking_code=tracking_code)
            return Response({
                'tracking_code': str(shipment.tracking_code),
                'status': shipment.payment_status,
                'origin': shipment.origin,
                'destination': shipment.destination,
                'current_location': shipment.origin if shipment.payment_status == 'PENDING' else 'In Transit',
                'coordinates': {'lat': -1.9441, 'lng': 30.0619},
                'last_updated': shipment.created_at.isoformat()
            })
        except Shipment.DoesNotExist:
            return Response({'error': 'Shipment not found'}, status=404)

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        from domestic.models import Shipment, PaymentRecord
        from django.db.models import Sum
        total = Shipment.objects.count()
        paid = Shipment.objects.filter(payment_status='PAID').count()
        in_transit = Shipment.objects.filter(payment_status='DISPATCHED').count()
        failed = Shipment.objects.filter(payment_status='FAILED').count()
        revenue = PaymentRecord.objects.filter(is_confirmed=True).aggregate(
            total=Sum('amount'))['total'] or 0
        return Response({
            'total_shipments': total,
            'paid': paid,
            'in_transit': in_transit,
            'failed': failed,
            'total_revenue_rwf': str(revenue),
            'active_trucks': in_transit,
        })

class BroadcastNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        message = request.data.get('message')
        priority = request.data.get('priority', 'NORMAL')
        if not message:
            return Response({'error': 'message is required'}, status=400)
        return Response({
            'status': 'broadcast_sent',
            'message': message,
            'priority': priority,
            'recipients': 'all_active_drivers',
            'channel': 'SMS'
        })
