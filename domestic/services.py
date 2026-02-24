import uuid
import requests
from decimal import Decimal
from django.db import transaction
from .models import Shipment, PaymentRecord
from core.models import IshemaLinkUserAccountModel

class GovTechService:
    """Task 4: Handles communication with Rwandan Government APIs"""

    @staticmethod
    def verify_rura_license(license_number):
        """Simulates checking driver status with RURA"""
        if not license_number or len(str(license_number)) < 5:
            return {"valid": False, "reason": "Invalid License Format"}
        
        # Mocking a successful verification for Task 4
        return {"valid": True, "category": "Heavy Cargo", "expiry": "2027-01-01"}

    @staticmethod
    def generate_ebm_receipt(amount, shipment_id):
        """Simulates RRA EBM digital signature generation"""
        # Required for Task 4 compliance
        return f"RRA-EBM-{uuid.uuid4().hex[:12].upper()}"

from django.contrib.auth import get_user_model
User = get_user_model() # This ensures we use your IshemaLinkUserAccountModel

class BookingService:
    @transaction.atomic
    def create_unified_booking(self, user, data):
        # FIX: Ensure we are using the actual IshemaLinkUserAccountModel instance
        if not isinstance(user, IshemaLinkUserAccountModel):
            user = IshemaLinkUserAccountModel.objects.get(pk=user.pk)
            
        weight = Decimal(str(data.get('weight_kg', 0)))
        rate = Decimal('500') if data.get('shipment_type') == 'DOMESTIC' else Decimal('1200')
        tariff = weight * rate
        
        shipment = Shipment.objects.create(
            sender=user,
            shipment_type=data.get('shipment_type'),
            origin=data.get('origin'),
            destination=data.get('destination'),
            weight_kg=weight,
            tariff_amount=tariff
        )
        
        # Simulate Momo transaction ID generation
        tx_id = f"MOMO-{uuid.uuid4().hex[:8].upper()}"
        PaymentRecord.objects.create(
            shipment=shipment,
            transaction_id=tx_id,
            amount=tariff
        )
        return shipment

    def assign_driver_to_shipment(self, shipment_id, driver_user):
        """Task 4: Logic to ensure driver is valid before assignment via RURA"""
        from .models import Shipment
        try:
            shipment = Shipment.objects.get(id=shipment_id)
            
            # Verify with RURA first
            verification = GovTechService.verify_rura_license(driver_user.license_number)
            
            if verification["valid"]:
                shipment.driver_assigned = driver_user
                shipment.save()
                return True
            return False
        except Shipment.DoesNotExist:
            return False