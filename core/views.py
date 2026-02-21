from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .models import Shipment, PaymentRecord
from .services import BookingService, GovTechMocks # Ensure you have GovTechMocks
import uuid

class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "username": request.user.username,
            "user_type": getattr(request.user, 'user_type', 'N/A'),
            "is_verified": getattr(request.user, 'is_identity_verified', False)
        })

class PaymentWebhookView(APIView):
    def post(self, request):
        tx_id = request.data.get("transaction_id")
        momo_status = request.data.get("status")
        
        try:
            with transaction.atomic():
                # Task 2: select_for_update prevents race conditions during high traffic
                payment = PaymentRecord.objects.select_for_update().get(transaction_id=tx_id)
                shipment = payment.shipment
                
                if momo_status == "SUCCESS" and not payment.is_confirmed:
                    payment.is_confirmed = True
                    payment.save()
                    
                    # Task 4: Generate EBM Signature immediately
                    shipment.ebm_signature = f"RRA-EBM-{uuid.uuid4().hex[:10].upper()}"
                    shipment.payment_status = "PAID"
                    shipment.save()
                    
                    return Response({"message": "Confirmed", "ebm": shipment.ebm_signature}, status=status.HTTP_200_OK)
                
                elif momo_status == "FAILED":
                    shipment.payment_status = "FAILED"
                    shipment.save()
                    return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
                    
            return Response({"message": "Already processed"}, status=status.HTTP_200_OK)
        except PaymentRecord.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)