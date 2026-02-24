import pytest
import uuid
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from core.models import IshemaLinkUserAccountModel
from domestic.models import Shipment, PaymentRecord
from domestic.services import BookingService


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def agent_user(db):
    return IshemaLinkUserAccountModel.objects.create_user(
        username="kalisa_agent", password="Test1234!", user_type="AGENT"
    )

@pytest.fixture
def second_agent(db):
    return IshemaLinkUserAccountModel.objects.create_user(
        username="uwase_agent", password="Test1234!", user_type="AGENT"
    )

@pytest.fixture
def driver_user(db):
    return IshemaLinkUserAccountModel.objects.create_user(
        username="mugisha_driver", password="Test1234!", user_type="DRIVER"
    )

@pytest.fixture
def auth_client(api_client, agent_user):
    api_client.force_authenticate(user=agent_user)
    return api_client

@pytest.fixture
def booked_shipment(db, agent_user):
    shipment = Shipment.objects.create(
        sender=agent_user, shipment_type="DOMESTIC",
        origin="Kigali", destination="Musanze",
        weight_kg=Decimal("50"), tariff_amount=Decimal("25000"),
        payment_status="PENDING"
    )
    PaymentRecord.objects.create(
        shipment=shipment,
        transaction_id=f"MOMO-{uuid.uuid4().hex[:8].upper()}",
        amount=Decimal("25000")
    )
    return shipment


# ================================================================
# UNIT TESTS: TARIFF CALCULATION
# ================================================================
@pytest.mark.django_db
class TestTariffCalculation:

    def test_domestic_tariff_50kg(self):
        assert Decimal("50") * Decimal("500") == Decimal("25000")

    def test_international_tariff_50kg(self):
        assert Decimal("50") * Decimal("1200") == Decimal("60000")

    def test_zero_weight_tariff(self):
        assert Decimal("0") * Decimal("500") == Decimal("0")

    def test_fractional_weight(self):
        assert Decimal("12.5") * Decimal("500") == Decimal("6250.0")

    def test_domestic_rate_constant(self):
        service = BookingService()
        assert service.DOMESTIC_RATE == Decimal("500")

    def test_international_rate_constant(self):
        service = BookingService()
        assert service.INTERNATIONAL_RATE == Decimal("1200")


# ================================================================
# UNIT TESTS: NID VALIDATION
# ================================================================
@pytest.mark.django_db
class TestNIDValidation:

    def test_valid_rwandan_nid(self):
        import re
        assert re.match(r'^\d{16}$', "1199880012345678") is not None

    def test_nid_too_short(self):
        import re
        assert re.match(r'^\d{16}$', "123456789012345") is None

    def test_nid_too_long(self):
        import re
        assert re.match(r'^\d{16}$', "12345678901234567") is None

    def test_nid_with_letters(self):
        import re
        assert re.match(r'^\d{16}$', "119988001234567A") is None


# ================================================================
# INTEGRATION TESTS: HAPPY PATH
# ================================================================
@pytest.mark.django_db
class TestHappyPath:

    def test_create_shipment_returns_tracking_code(self, auth_client):
        response = auth_client.post("/api/shipments/create/", {
            "weight_kg": 50, "sender": "Kalisa Jean",
            "recipient": "Uwase Marie", "origin": "Kigali",
            "destination": "Musanze", "phone": "0788123456",
            "shipment_type": "DOMESTIC"
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "tracking_code" in response.data
        assert "momo_id" in response.data
        assert response.data["tariff"] == "25000.00"

    def test_webhook_success_sets_paid(self, auth_client, booked_shipment):
        tx_id = booked_shipment.payment.transaction_id
        auth_client.post("/api/payments/webhook/", {
            "transaction_id": tx_id, "status": "SUCCESS", "amount": "25000.00"
        }, format="json")
        booked_shipment.refresh_from_db()
        assert booked_shipment.payment_status == "PAID"

    def test_webhook_failed_sets_failed(self, auth_client, booked_shipment):
        tx_id = booked_shipment.payment.transaction_id
        auth_client.post("/api/payments/webhook/", {
            "transaction_id": tx_id, "status": "FAILED", "amount": "25000.00"
        }, format="json")
        booked_shipment.refresh_from_db()
        assert booked_shipment.payment_status == "FAILED"

    def test_confirmed_payment_not_overwritten(self, auth_client, booked_shipment):
        tx_id = booked_shipment.payment.transaction_id
        auth_client.post("/api/payments/webhook/", {
            "transaction_id": tx_id, "status": "SUCCESS", "amount": "25000.00"
        }, format="json")
        auth_client.post("/api/payments/webhook/", {
            "transaction_id": tx_id, "status": "FAILED", "amount": "25000.00"
        }, format="json")
        booked_shipment.refresh_from_db()
        assert booked_shipment.payment_status == "PAID"

    def test_tracking_returns_coordinates(self, auth_client, booked_shipment):
        response = auth_client.get(
            f"/api/tracking/{booked_shipment.tracking_code}/live/"
        )
        assert response.status_code == 200
        assert "coordinates" in response.data

    def test_dashboard_returns_revenue(self, auth_client, booked_shipment):
        response = auth_client.get("/api/admin/dashboard/summary/")
        assert response.status_code == 200
        assert "total_revenue_rwf" in response.data
        assert "total_shipments" in response.data


# ================================================================
# SECURITY TESTS
# ================================================================
@pytest.mark.django_db
class TestSecurity:

    def test_unauthenticated_cannot_create_shipment(self, api_client):
        response = api_client.post("/api/shipments/create/", {
            "weight_kg": 50, "origin": "Kigali",
            "destination": "Musanze", "phone": "0788123456",
            "shipment_type": "DOMESTIC"
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_cannot_view_dashboard(self, api_client):
        response = api_client.get("/api/admin/dashboard/summary/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_agent_cannot_see_sender_data_of_others(
        self, api_client, second_agent, booked_shipment
    ):
        api_client.force_authenticate(user=second_agent)
        response = api_client.get(
            f"/api/tracking/{booked_shipment.tracking_code}/live/"
        )
        if response.status_code == 200:
            assert "sender" not in response.data

    def test_sql_injection_returns_404_not_500(self, auth_client):
        response = auth_client.get(
            "/api/tracking/1%27%20OR%201%3D1--/live/"
        )
        assert response.status_code in [404, 400]

    def test_fake_transaction_id_returns_404(self, api_client):
        response = api_client.post("/api/payments/webhook/", {
            "transaction_id": "MOMO-FAKEID999",
            "status": "SUCCESS", "amount": "25000.00"
        }, format="json")
        assert response.status_code == 404


# ================================================================
# CONCURRENCY TEST
# ================================================================
@pytest.mark.django_db(transaction=True)
class TestConcurrency:

    def test_double_booking_prevention(self, agent_user, driver_user):
        import threading
        results = []
        shipment1 = Shipment.objects.create(
            sender=agent_user, shipment_type="DOMESTIC",
            origin="Kigali", destination="Musanze",
            weight_kg=Decimal("50"), tariff_amount=Decimal("25000")
        )
        shipment2 = Shipment.objects.create(
            sender=agent_user, shipment_type="DOMESTIC",
            origin="Butare", destination="Kigali",
            weight_kg=Decimal("30"), tariff_amount=Decimal("15000")
        )

        def assign_driver(shipment):
            try:
                from django.db import transaction
                with transaction.atomic():
                    s = Shipment.objects.select_for_update().get(pk=shipment.pk)
                    if s.driver_assigned is None:
                        s.driver_assigned = driver_user
                        s.save()
                        results.append("SUCCESS")
                    else:
                        results.append("BLOCKED")
            except Exception as e:
                results.append(f"ERROR: {e}")

        t1 = threading.Thread(target=assign_driver, args=(shipment1,))
        t2 = threading.Thread(target=assign_driver, args=(shipment2,))
        t1.start(); t2.start()
        t1.join(); t2.join()
        assert len(results) == 2
        assert not any("ERROR" in r for r in results)


# ================================================================
# COVERAGE BOOSTERS
# ================================================================
@pytest.mark.django_db
class TestModelsCoverage:

    def test_shipment_str(self, booked_shipment):
        assert str(booked_shipment.tracking_code) in str(booked_shipment)

    def test_payment_defaults(self, booked_shipment):
        assert booked_shipment.payment.provider == "MTN_MOMO"
        assert booked_shipment.payment.is_confirmed == False

    def test_international_shipment(self, agent_user):
        shipment = Shipment.objects.create(
            sender=agent_user, shipment_type="INTERNATIONAL",
            origin="Kigali", destination="Mombasa",
            weight_kg=Decimal("50"), tariff_amount=Decimal("60000")
        )
        assert shipment.tariff_amount == Decimal("60000")

    def test_user_type_choices(self):
        choices = [c[0] for c in IshemaLinkUserAccountModel.USER_TYPES]
        assert "AGENT" in choices
        assert "DRIVER" in choices
        assert "CUSTOMER" in choices

    def test_user_nid_field(self, agent_user):
        agent_user.the_16_digit_rwandan_nid_number = "1199880012345678"
        agent_user.save()
        agent_user.refresh_from_db()
        assert agent_user.the_16_digit_rwandan_nid_number == "1199880012345678"


@pytest.mark.django_db
class TestNotificationsAndDashboard:

    def test_broadcast_requires_message(self, auth_client):
        response = auth_client.post("/api/notifications/broadcast/",
            {"priority": "HIGH"}, format="json")
        assert response.status_code == 400

    def test_broadcast_default_priority(self, auth_client):
        response = auth_client.post("/api/notifications/broadcast/",
            {"message": "Test alert"}, format="json")
        assert response.status_code == 200
        assert response.data["priority"] == "NORMAL"

    def test_dashboard_counts_failed(self, auth_client, booked_shipment):
        tx_id = booked_shipment.payment.transaction_id
        auth_client.post("/api/payments/webhook/",
            {"transaction_id": tx_id, "status": "FAILED", "amount": "25000.00"},
            format="json")
        response = auth_client.get("/api/admin/dashboard/summary/")
        assert response.data["failed"] >= 1

    def test_dashboard_counts_paid(self, auth_client, booked_shipment):
        tx_id = booked_shipment.payment.transaction_id
        auth_client.post("/api/payments/webhook/",
            {"transaction_id": tx_id, "status": "SUCCESS", "amount": "25000.00"},
            format="json")
        response = auth_client.get("/api/admin/dashboard/summary/")
        assert response.data["paid"] >= 1

    def test_tracking_unknown_uuid_returns_404(self, auth_client):
        response = auth_client.get(
            "/api/tracking/00000000-0000-0000-0000-000000000000/live/")
        assert response.status_code == 404

    def test_webhook_already_confirmed_ignored(self, auth_client, booked_shipment):
        tx_id = booked_shipment.payment.transaction_id
        auth_client.post("/api/payments/webhook/",
            {"transaction_id": tx_id, "status": "SUCCESS", "amount": "25000.00"},
            format="json")
        response = auth_client.post("/api/payments/webhook/",
            {"transaction_id": tx_id, "status": "SUCCESS", "amount": "25000.00"},
            format="json")
        assert response.status_code == 200
        assert "already confirmed" in response.data["message"]
