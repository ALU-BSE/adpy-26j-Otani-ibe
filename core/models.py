from django.contrib.auth.models import AbstractUser
from django.db import models

class IshemaLinkUserAccountModel(AbstractUser):
    the_16_digit_rwandan_nid_number = models.CharField(max_length=16, unique=True, null=True, blank=True)
    this_user_is_either_an_agent_or_a_customer_type = models.CharField(max_length=20, default='CUSTOMER')

    is_identity_verified_by_system = models.BooleanField(default=False)
    phone_number_for_otp = models.CharField(max_length=15, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} - Verified: {self.is_identity_verified_by_system}"