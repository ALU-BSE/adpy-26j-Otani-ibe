#  IshemaLink Logistics Backend

**Digitizing the courier market for rural farmers in Rwanda.**

## Overview

IshemaLink is a specialized logistics API built to bridge the gap between rural farmers and provincial markets. This backend handles secure user registration, asynchronous package tracking, and a smart caching system for shipping tariffs to ensure the platform remains fast even on slow rural mobile data networks.

## Tech Stack

- **Language**: Python 3.12  
- **Framework**: Django 6.0 + Django REST Framework  
- **Database**: SQLite (Development)  
- **Asynchronous Logic**: Python `asyncio`  
- **Caching**: Django LocMemCache  

## Key Features

- **Rwandan Identity Validation**: Custom validators ensure all users provide a valid 16-digit Rwandan NID and a correctly formatted phone number (`+250 7XX...`).
- **Async Status Updates**: When a package arrives at a hub like **Nyabugogo**, the system sends an SMS notification in the background without making the user wait for the network to respond.
- **Tariff Caching**: High-traffic shipping rates are stored in memory (Local Cache) to reduce database load and improve speed.
- **Paginated Manifests**: Efficient handling of large shipment volumes at border posts using pagination to limit data transfers.

##  Design Choices

- **Non-Blocking I/O**: Implemented `asyncio` for notifications to simulate real-world network constraints common in rural provinces, ensuring the API remains responsive.
- **Manual Pagination**: Chose a manual meta-response structure for pagination to provide mobile frontends.

##  Quick Start

### 1. Setup

```bash
pip install -r requirements.txt
python manage.py migrate

### 2. Run Server
```bash
python manage.py runserver

### 3. Seed Test Data
### Open the Django shell:

python manage.py shell

API Endpoints

POST /api/auth/register/ — Register a new agent or customer

GET /api/shipments/ — View the paginated shipment manifest

POST /api/shipments/<id>/update-status/ — Trigger an async status update

GET /api/pricing/tariffs/ — Retrieve cached shipping rates