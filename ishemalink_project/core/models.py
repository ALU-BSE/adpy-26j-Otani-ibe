# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    TYPES_OF_PEOPLE = (
        ('AGENT', 'Agent'),
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=TYPES_OF_PEOPLE, default='CUSTOMER')
    
    nid_number = models.CharField(max_length=16, unique=True, null=True, blank=True)
    
    phone_number = models.CharField(max_length=13, unique=True)

    def __str__(self):
      return self.username