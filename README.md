# IshemaLink National Logistics Platform

**Author:** Obasi-Otani Ibe
**Institution:** African Leadership University, BSE
**Branch:** feature/grand-integration

---

## Overview

IshemaLink is a logistics management API built for Rwanda's national rollout. It handles shipment booking, mobile money payment processing, government compliance, and logistics analytics for 5,000+ concurrent field agents.

The platform integrates with Rwanda Revenue Authority (RRA) for EBM tax receipts, Rwanda Utilities Regulatory Authority (RURA) for transport license verification, and MTN/Airtel MoMo for mobile payments.

---

## Stack

- Django 6.0.2 with Django REST Framework
- PostgreSQL 15 (production), SQLite (development)
- Redis 7 for caching
- Gunicorn + Nginx with SSL/TLS
- Docker + Docker Compose
- JWT authentication via SimpleJWT

---

## Tasks Completed

**Task 1 - Grand Integration**
Unified booking endpoint, MoMo payment webhook, live shipment tracking, admin control tower dashboard, driver broadcast notifications.

**Task 2 - Harvest Stress Testing**
53-test pytest suite, Locust load testing script for 2,000 concurrent agents, Bandit security audit (0 high/medium issues).

**Task 3 - Production Readiness**
Dockerfile, docker-compose.prod.yml, Nginx SSL/TLS configuration, automated backup script, disaster recovery plan.

**Task 4 - GovTech Integration**
RRA EBM receipt signing, RURA transport license verification, EAC customs manifest generation, government audit log.

**Task 5 - Logistics Intelligence**
Route analytics, commodity breakdown, revenue heatmap, driver leaderboard, anonymized data export for MINICOM road planning.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/token/ | Get JWT access token |
| POST | /api/shipments/create/ | Book a shipment |
| POST | /api/payments/webhook/ | MoMo payment callback |
| GET | /api/tracking/{code}/live/ | Live shipment tracking |
| GET | /api/admin/dashboard/summary/ | Control tower dashboard |
| POST | /api/notifications/broadcast/ | Broadcast to drivers |
| POST | /api/gov/ebm/sign-receipt/ | RRA EBM signature |
| GET | /api/gov/rura/verify-license/{no}/ | RURA license check |
| POST | /api/gov/customs/generate-manifest/ | EAC customs XML |
| GET | /api/gov/audit/access-log/ | Government audit trail |
| GET | /api/analytics/routes/top/ | Top traffic corridors |
| GET | /api/analytics/export/ | Anonymized data export |
| GET | /api/health/deep/ | System health check |

Full API specification: [swagger.yaml](./swagger.yaml)

---

## Running Locally

```bash
git clone https://github.com/ALU-BSE/adpy-26j-Otani-ibe.git
cd adpy-26j-Otani-ibe
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8001
```

---

## Running Tests

```bash
pytest domestic/tests_task2.py --cov=domestic --cov=core --cov-report=term-missing
```

---

## Production Deployment

See [Deployment Manual](./docs/deployment/DEPLOYMENT_MANUAL.md) for step-by-step instructions to deploy on a clean Ubuntu 24 server.

---

## Documentation

| Document | Location |
|---|---|
| System Architecture | [docs/architecture/SYSTEM_ARCHITECTURE.md](./docs/architecture/SYSTEM_ARCHITECTURE.md) |
| Deployment Manual | [docs/deployment/DEPLOYMENT_MANUAL.md](./docs/deployment/DEPLOYMENT_MANUAL.md) |
| Disaster Recovery Plan | [docs/deployment/DISASTER_RECOVERY_PLAN.pdf](./docs/deployment/DISASTER_RECOVERY_PLAN.pdf) |
| Security Audit | [docs/security/SECURITY_AUDIT.md](./docs/security/SECURITY_AUDIT.md) |
| Testing Report | [docs/testing/TESTING_REPORT.md](./docs/testing/TESTING_REPORT.md) |
| GovTech Compliance | [docs/compliance/GOVTECH_COMPLIANCE_REPORT.md](./docs/compliance/GOVTECH_COMPLIANCE_REPORT.md) |
| Integration Report | [docs/reports/INTEGRATION_REPORT.md](./docs/reports/INTEGRATION_REPORT.md) |
| Scalability Plan | [docs/reports/SCALABILITY_PLAN.md](./docs/reports/SCALABILITY_PLAN.md) |
| Local Context Essay | [docs/reports/LOCAL_CONTEXT_ESSAY.md](./docs/reports/LOCAL_CONTEXT_ESSAY.md) |