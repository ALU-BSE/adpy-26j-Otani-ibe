# IshemaLink GovTech Compliance Report — Task 4

**Date:** 2026-02-21  
**Authority:** MINICOM, RRA, RURA  
**System:** IshemaLink National Logistics Platform

---

## 1. Implemented Government Endpoints

| Endpoint | Authority | Status |
|---|---|---|
| `POST /api/gov/ebm/sign-receipt/` | RRA | ✅ Live |
| `GET /api/gov/rura/verify-license/{license_no}/` | RURA | ✅ Live |
| `POST /api/gov/customs/generate-manifest/` | EAC Customs | ✅ Live |
| `GET /api/gov/audit/access-log/` | MINICOM/RRA | ✅ Live |

---

## 2. RRA EBM Integration

Every completed payment generates a digital EBM signature stored
on the shipment record. No shipment can be marked PAID without an
associated EBM signature.

**Sample EBM Signature:** `RRA-EBM-A5DF85086C`  
**Compliance field:** `Shipment.ebm_signature`  
**Trigger:** `POST /api/payments/webhook/` with `status: SUCCESS`

---

## 3. RURA License Verification

Before a driver is assigned to a shipment, their transport
authorization is verified via `GovTechService.verify_rura_license()`.
Dispatch is blocked if the license check fails.

**Response includes:**
- `valid: true/false`
- `dispatch_allowed: true/false`
- `expiry` date
- `category` (Heavy Cargo / Light Vehicle)

---

## 4. EAC Customs Manifest

International shipments generate an EAC-compliant XML manifest
including tracking code, weight, tariff, origin/destination,
and EBM signature for border control.

**Format:** EAC XML v2.0  
**Namespace:** `http://eac.int/customs/2024`  
**XML Security:** defusedxml (XXE-safe)

---

## 5. Audit Trail

`GET /api/gov/audit/access-log/` — Staff only  
Returns last 100 shipments with:
- EBM signature status
- RRA compliance flag
- Payment confirmation
- Compliance rate percentage

**Current compliance rate** is tracked live and reported to MINICOM.

---

## 6. Data Sovereignty

All government data remains within Rwanda at AOS/KtRN data centers.
No RRA or RURA data is transmitted outside Rwanda borders.
