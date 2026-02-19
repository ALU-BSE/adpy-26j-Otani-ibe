from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.db import transaction
from django.core.cache import cache
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated

from .serializers import ShipmentCreateSerializer, PaymentWebhookSerializer
from .services import BookingService
from .models import Shipment, PaymentRecord
from .notifications import NotificationEngine

class UniversalLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    schema = None 
    
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class ShipmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ShipmentCreateSerializer)
    def post(self, request):
        serializer = ShipmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            service = BookingService()
            try:
                shipment = service.create_unified_booking(request.user, serializer.validated_data)
                return Response({
                    "tracking_code": shipment.tracking_code,
                    "tariff": shipment.tariff_amount,
                    "status": shipment.payment_status,
                    "momo_id": shipment.payment.transaction_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentWebhookView(APIView):
    @extend_schema(request=PaymentWebhookSerializer)
    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)
        if serializer.is_valid():
            tx_id = serializer.validated_data.get("transaction_id")
            momo_status = serializer.validated_data.get("status")
            
            try:
                with transaction.atomic(): 
                    payment = PaymentRecord.objects.get(transaction_id=tx_id)
                    shipment = payment.shipment
                    
                    if momo_status == "SUCCESS":
                        payment.is_confirmed = True
                        payment.save()
                        shipment.payment_status = "PAID"
                        shipment.save()
                        
                        notifier = NotificationEngine()
                        notifier.send_pickup_sms(shipment.sender.email, shipment.tracking_code)
                        notifier.send_customs_email(shipment.sender.email, shipment.tracking_code)
                        
                        return Response({"message": "Payment confirmed and alerts sent"}, status=status.HTTP_200_OK)
                    else:
                        shipment.payment_status = "FAILED"
                        shipment.save()
                        return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
            except PaymentRecord.DoesNotExist:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class ShipmentTrackingView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter("tracking_code", OpenApiTypes.STR, OpenApiParameter.PATH)
        ],
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request, tracking_code):
        try:
            shipment = Shipment.objects.get(tracking_code=tracking_code)
            cache_key = f"track_{tracking_code}"
            location = cache.get(cache_key)

            if not location:
                location = {"lat": -1.9441, "lng": 30.0619, "city": "Kigali"}
                cache.set(cache_key, location, timeout=60)

            return Response({
                "tracking_code": tracking_code,
                "status": shipment.payment_status,
                "location": location
            }, status=status.HTTP_200_OK)
        except Shipment.DoesNotExist:
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        
class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "nid": getattr(request.user, 'the_16_digit_rwandan_nid_number', None)
        }, status=status.HTTP_200_OK)