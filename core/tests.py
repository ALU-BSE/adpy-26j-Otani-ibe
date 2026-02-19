from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Shipment, PaymentRecord
from .services import BookingService
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import uuid

User = get_user_model()

class IshemaLinkIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="testadmin", 
            password="password123",
            the_16_digit_rwandan_nid_number="1199080012345678"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_create_shipment(self):
        url = reverse('shipment-create')
        data = {
            "shipment_type": "DOMESTIC",
            "origin": "Kigali",
            "destination": "Musanze",
            "weight_kg": 50,
            "phone": "0788000111"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tracking_code', response.data)

    def test_api_payment_webhook_success(self):
        service = BookingService()
        shipment = service.create_unified_booking(self.user, {
            "shipment_type": "DOMESTIC", 
            "weight_kg": 10, 
            "phone": "0788000111",
            "origin": "Kigali",
            "destination": "Musanze"
        })
        
        url = reverse('payment-webhook')
        data = {"transaction_id": shipment.payment.transaction_id, "status": "SUCCESS"}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        shipment.refresh_from_db()
        self.assertEqual(shipment.payment_status, "PAID")

    def test_api_track_shipment(self):
        service = BookingService()
        shipment = service.create_unified_booking(self.user, {
            "shipment_type": "DOMESTIC", 
            "weight_kg": 10, 
            "phone": "0788000111",
            "origin": "Kigali",
            "destination": "Musanze"
        })
        
        url = reverse('shipment-tracking', kwargs={'tracking_code': shipment.tracking_code})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('location', response.data)
    
    def test_api_status_check(self):
        url = '/api/status/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_api_who_am_i(self):
        url = reverse('who-am-i')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)

    def test_api_logout(self):
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

class IshemaLinkCoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testagent",
            password="password123",
            the_16_digit_rwandan_nid_number="1199080012345678"
        )
        self.service = BookingService()

    def test_domestic_tariff_calculation(self):
        data = {
            "shipment_type": "DOMESTIC",
            "origin": "Kigali",
            "destination": "Musanze",
            "weight_kg": 10,
            "phone": "0780000000"
        }
        shipment = self.service.create_unified_booking(self.user, data)
        self.assertEqual(shipment.tariff_amount, 5000)

    def test_international_tariff_calculation(self):
        data = {
            "shipment_type": "INTERNATIONAL",
            "origin": "Kigali",
            "destination": "Nairobi",
            "weight_kg": 10,
            "phone": "0780000000"
        }
        shipment = self.service.create_unified_booking(self.user, data)
        self.assertEqual(shipment.tariff_amount, 12000)

    def test_booking_creates_payment_record(self):
        data = {
            "shipment_type": "DOMESTIC",
            "origin": "Kigali",
            "destination": "Huye",
            "weight_kg": 5,
            "phone": "0780000000"
        }
        shipment = self.service.create_unified_booking(self.user, data)
        self.assertTrue(PaymentRecord.objects.filter(shipment=shipment).exists())
        self.assertEqual(shipment.payment_status, "PENDING")

    def test_nid_presence(self):
        self.assertEqual(len(self.user.the_16_digit_rwandan_nid_number), 16)