# domestic/views.py
from django.db import models

class Shipment(models.Model):
    
    tracking_number = models.CharField(max_length=50, unique=True)
    
    sender_name = models.CharField(max_length=100)
    
    receiver_phone = models.CharField(max_length=20)
    
    status = models.CharField(max_length=20, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return self.tracking_number