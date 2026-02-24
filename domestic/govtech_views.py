"""
Task 4: GovTech Integration — RRA & RURA
New file — zero modifications to existing code.
Reuses GovTechService already built in domestic/services.py
"""
import uuid
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import defusedxml.minidom as minidom
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from domestic.services import GovTechService
from domestic.models import Shipment, PaymentRecord



class EBMSignReceiptView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        shipment_id = request.data.get("shipment_id")

        if not amount or not shipment_id:
            return Response(
                {"error": "amount and shipment_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return Response(
                {"error": "amount must be a valid number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify shipment exists
        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return Response(
                {"error": f"Shipment {shipment_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate EBM signature via existing GovTechService
        ebm_signature = GovTechService.generate_ebm_receipt(
            amount=amount,
            shipment_id=shipment_id
        )

        # Persist EBM signature on shipment
        shipment.ebm_signature = ebm_signature
        shipment.save()

        return Response({
            "ebm_signature": ebm_signature,
            "shipment_id": shipment_id,
            "amount_rwf": amount,
            "issued_at": datetime.datetime.now().isoformat(),
            "issuer": "Rwanda Revenue Authority",
            "status": "SIGNED",
            "compliance": "RRA_EBM_COMPLIANT"
        }, status=status.HTTP_200_OK)


class RURAVerifyLicenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, license_no):
        if not license_no:
            return Response(
                {"error": "license_no is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify via existing GovTechService
        result = GovTechService.verify_rura_license(license_no)

        if result["valid"]:
            return Response({
                "license_number": license_no,
                "valid": True,
                "category": result.get("category", "Heavy Cargo"),
                "expiry": result.get("expiry", "2027-01-01"),
                "verified_at": datetime.datetime.now().isoformat(),
                "authority": "Rwanda Utilities Regulatory Authority",
                "dispatch_allowed": True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "license_number": license_no,
                "valid": False,
                "reason": result.get("reason", "License invalid"),
                "dispatch_allowed": False,
                "authority": "Rwanda Utilities Regulatory Authority"
            }, status=status.HTTP_200_OK)

class CustomsGenerateManifestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shipment_id = request.data.get("shipment_id")

        if not shipment_id:
            return Response(
                {"error": "shipment_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return Response(
                {"error": f"Shipment {shipment_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if shipment.shipment_type != "INTERNATIONAL":
            return Response(
                {"error": "Customs manifest only applies to INTERNATIONAL shipments"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build EAC-compliant XML
        manifest_xml = self._generate_xml(shipment)

        return Response({
            "manifest_id": f"EAC-{uuid.uuid4().hex[:8].upper()}",
            "shipment_id": shipment_id,
            "tracking_code": str(shipment.tracking_code),
            "origin": shipment.origin,
            "destination": shipment.destination,
            "weight_kg": str(shipment.weight_kg),
            "generated_at": datetime.datetime.now().isoformat(),
            "format": "EAC_XML_v2",
            "xml_manifest": manifest_xml,
            "status": "MANIFEST_READY"
        }, status=status.HTTP_200_OK)

    def _generate_xml(self, shipment):
        """Generates EAC-compliant customs XML."""
        root = Element("EACCustomsManifest")
        root.set("version", "2.0")
        root.set("xmlns", "http://eac.int/customs/2024")

        # Header
        header = SubElement(root, "ManifestHeader")
        SubElement(header, "ManifestID").text = f"EAC-{uuid.uuid4().hex[:8].upper()}"
        SubElement(header, "IssuedBy").text = "IshemaLink Rwanda"
        SubElement(header, "IssuedAt").text = datetime.datetime.now().isoformat()
        SubElement(header, "Country").text = "RW"

        # Shipment details
        details = SubElement(root, "ShipmentDetails")
        SubElement(details, "TrackingCode").text = str(shipment.tracking_code)
        SubElement(details, "Origin").text = shipment.origin
        SubElement(details, "Destination").text = shipment.destination
        SubElement(details, "WeightKG").text = str(shipment.weight_kg)
        SubElement(details, "TariffRWF").text = str(shipment.tariff_amount)
        SubElement(details, "PaymentStatus").text = shipment.payment_status

        # EBM compliance
        compliance = SubElement(root, "TaxCompliance")
        SubElement(compliance, "EBMSignature").text = shipment.ebm_signature or "PENDING"
        SubElement(compliance, "RRACompliant").text = "true" if shipment.ebm_signature else "false"

        # Pretty print XML
        raw = tostring(root, encoding="unicode")
        parsed = minidom.parseString(raw)
        return parsed.toprettyxml(indent="  ")


class GovAuditAccessLogView(APIView):
   
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Government audit access requires staff privileges"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Aggregate audit data from existing models
        shipments = Shipment.objects.select_related('sender').order_by('-id')[:100]

        audit_entries = []
        for shipment in shipments:
            try:
                payment = shipment.payment
                tx_id = payment.transaction_id
                confirmed = payment.is_confirmed
            except Exception:
                tx_id = "N/A"
                confirmed = False

            audit_entries.append({
                "shipment_id": shipment.id,
                "tracking_code": str(shipment.tracking_code),
                "type": shipment.shipment_type,
                "origin": shipment.origin,
                "destination": shipment.destination,
                "weight_kg": str(shipment.weight_kg),
                "tariff_rwf": str(shipment.tariff_amount),
                "payment_status": shipment.payment_status,
                "ebm_signature": shipment.ebm_signature or "NOT_SIGNED",
                "rra_compliant": bool(shipment.ebm_signature),
                "transaction_id": tx_id,
                "payment_confirmed": confirmed,
            })

        total = Shipment.objects.count()
        paid = Shipment.objects.filter(payment_status="PAID").count()
        signed = Shipment.objects.exclude(ebm_signature="").exclude(
            ebm_signature__isnull=True
        ).count()

        return Response({
            "generated_at": datetime.datetime.now().isoformat(),
            "authority": "IshemaLink — Government Audit Module",
            "summary": {
                "total_shipments": total,
                "paid_shipments": paid,
                "ebm_signed": signed,
                "compliance_rate": f"{(signed/total*100):.1f}%" if total > 0 else "0%"
            },
            "audit_log": audit_entries
        }, status=status.HTTP_200_OK)

