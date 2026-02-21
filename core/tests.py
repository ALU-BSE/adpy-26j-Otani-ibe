from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Shipment, PaymentRecord

class IshemaLinkAuditTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser('otaniibe', 'test@test.com', 'otani12345')
        self.client.force_authenticate(user=self.user)

    def test_webhook_transaction_not_found(self):
        response = self.client.post('/api/payments/webhook/', {
            "transaction_id": "NON-EXISTENT-ID",
            "status": "SUCCESS"
        })
        self.assertEqual(response.status_code, 404)

    def test_tracking_shipment_not_found(self):
        response = self.client.get('/api/tracking/INVALID-CODE/live/')
        self.assertEqual(response.status_code, 404)

    def test_create_shipment_invalid_data(self):
        response = self.client.post('/api/shipments/create/', {"weight_kg": -1})
        self.assertEqual(response.status_code, 400)