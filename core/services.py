import uuid
from django.db import transaction
from .models import Shipment, PaymentRecord

class MomoMockAdapter:
    def initiate_payment(self, phone, amount):
        fake_tx_id = f"MOMO-{uuid.uuid4().hex[:8].upper()}"
        return fake_tx_id

class BookingService:
    def __init__(self, payment_gateway=None):
        if payment_gateway is None:
            self.payment_gateway = MomoMockAdapter()
        else:
            self.payment_gateway = payment_gateway

    @transaction.atomic
    def create_unified_booking(self, user, data):
        weight = float(data.get('weight_kg', 0))
        
        if data.get('shipment_type') == 'DOMESTIC':
            tariff = weight * 500   
        else:
            tariff = weight * 1200  
        
        shipment = Shipment.objects.create(
            sender=user,
            shipment_type=data.get('shipment_type'),
            origin=data.get('origin'),
            destination=data.get('destination'),
            weight_kg=weight,
            tariff_amount=tariff
        )
        
        tx_id = self.payment_gateway.initiate_payment(data.get('phone'), tariff)
        PaymentRecord.objects.create(
            shipment=shipment,
            transaction_id=tx_id,
            amount=tariff
        )
        return shipment