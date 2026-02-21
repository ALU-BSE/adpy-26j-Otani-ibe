
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class IshemaLinkUserAccountModel(AbstractUser):
    USER_TYPES = [('AGENT', 'Agent'), ('CUSTOMER', 'Customer'), ('DRIVER', 'Driver')]
    the_16_digit_rwandan_nid_number = models.CharField(max_length=16, null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='CUSTOMER')
    is_identity_verified = models.BooleanField(default=False)

class Shipment(models.Model):
    SHIPMENT_TYPES = [('DOMESTIC', 'Domestic'), ('INTERNATIONAL', 'International')]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid/Processing'),
        ('DISPATCHED', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Payment Failed')
    ]
    
    tracking_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(IshemaLinkUserAccountModel, on_delete=models.CASCADE, related_name='shipments')
    shipment_type = models.CharField(max_length=20, choices=SHIPMENT_TYPES)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    tariff_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    ebm_signature = models.CharField(max_length=255, null=True, blank=True)
    
    driver_assigned = models.ForeignKey(
        IshemaLinkUserAccountModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'user_type': 'DRIVER'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentRecord(models.Model):
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=50, default='MTN_MOMO')
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
