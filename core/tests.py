from django.test import TestCase
from .validators import validate_rwandan_nid, validate_rwandan_phone

class TestMyRwandanValidators(TestCase):
    
    def test_if_the_nid_validator_works_correctly(self):
        self.assertTrue(validate_rwandan_nid("1199000000000000"))
        self.assertFalse(validate_rwandan_nid("123"))
        self.assertFalse(validate_rwandan_nid("2199000000000000"))

    def test_if_the_phone_validator_works_correctly(self):
        self.assertTrue(validate_rwandan_phone("+250788123456"))
        self.assertFalse(validate_rwandan_phone("0788123456"))
        self.assertFalse(validate_rwandan_phone("+250788123456789"))