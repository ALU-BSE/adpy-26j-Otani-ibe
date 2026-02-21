from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from domestic.models import Shipment, PaymentRecord

User = get_user_model()

class IshemaLinkAuditTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='audit_tester',
            email='audit@test.com',
            password='StrongPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_webhook_transaction_not_found(self):
        response = self.client.post('/api/payments/webhook/', {
            "transaction_id": "NON-EXISTENT-ID",
            "status": "SUCCESS"
        }, format='json')
        self.assertEqual(response.status_code, 404)

    def test_tracking_shipment_not_found(self):
        response = self.client.get('/api/tracking/00000000-0000-0000-0000-000000000000/live/')
        self.assertEqual(response.status_code, 404)

    def test_create_shipment_invalid_data(self):
        response = self.client.post('/api/shipments/create/', {"weight_kg": -1}, format='json')
        self.assertEqual(response.status_code, 400)
