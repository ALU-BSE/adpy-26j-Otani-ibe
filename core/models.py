from django.db import models
from django.contrib.auth.models import AbstractUser

class IshemaLinkUserAccountModel(AbstractUser):
    this_user_is_either_an_agent_or_a_customer_type = models.CharField(
        max_length=20, 
        choices=[('AGENT', 'Agent'), ('CUSTOMER', 'Customer'), ('ADMIN', 'Admin')], 
        default='CUSTOMER'
    )
    
    the_sixteen_digit_rwandan_national_id_number_for_kyc = models.CharField(
        max_length=16, 
        unique=True, 
        null=True, 
        blank=True
    )
    
    the_phone_number_starting_with_plus_250 = models.CharField(
        max_length=13, 
        unique=True
    )

    def __str__(self):
        return self.username + " is registered as " + self.this_user_is_either_an_agent_or_a_customer_type