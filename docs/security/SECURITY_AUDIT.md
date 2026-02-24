# IshemaLink Security Audit Report

**Tool:** Bandit v1.9.3 (SAST)
**Date:** 2026-02-21
**Standard:** OWASP Top 10, CWE
**Scope:** `domestic/` `core/`
**Total Lines Scanned:** 1,422

---

## Summary

| Severity | Before | After | Status |
|---|---|---|---|
| High | 0 | 0 | ✅ PASS |
| Medium | 1 | 0 | ✅ REMEDIATED |
| Low | 82 | 82 | ⚠️ ACCEPTED |

**Overall Risk Level: LOW — Approved for staging deployment**

---

## Issue Remediated

**ISSUE-001 — B318: XXE Attack via xml.dom.minidom**
- **Severity:** Medium | **Confidence:** High
- **CWE:** CWE-20 Improper Input Validation
- **Location:** `domestic/govtech_views.py:197`
- **Fix:** Replaced `xml.dom.minidom` with `defusedxml.minidom`
```python
# BEFORE (vulnerable)
from xml.dom import minidom

# AFTER (patched)
import defusedxml.minidom as minidom
```

---

## Security Test Results (pytest)

| Test | Rwanda Scenario | Result |
|---|---|---|
| `test_unauthenticated_cannot_create_shipment` | Unregistered agent attempts booking | ✅ PASSED |
| `test_unauthenticated_cannot_view_dashboard` | Unknown user accesses control tower | ✅ PASSED |
| `test_agent_cannot_see_sender_data_of_others` | Uwase views Kalisa's private shipment | ✅ PASSED |
| `test_sql_injection_returns_404_not_500` | Attacker injects SQL via tracking URL | ✅ PASSED |
| `test_fake_transaction_id_returns_404` | Spoofed Momo callback with fake ID | ✅ PASSED |
| `test_confirmed_payment_not_overwritten` | FAILED callback after SUCCESS payment | ✅ PASSED |

---

## Pre-Launch Security Checklist

- [ ] Set `DEBUG=False` in production settings
- [ ] Rotate `SECRET_KEY` — store in environment vault
- [ ] Add HMAC signature verification to `POST /api/payments/webhook/`
- [ ] Add rate limiting to `POST /api/token/` (brute force prevention)
- [ ] Restrict `CORS_ALLOWED_ORIGINS` to production domain only
- [ ] Enable `SECURE_SSL_REDIRECT` and `SECURE_HSTS_SECONDS`
