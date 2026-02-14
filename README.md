#  IshemaLink Logistics Backend

**Digitizing the courier market for rural farmers in Rwanda.**

## Overview

IshemaLink is a specialized logistics API built to bridge the gap between rural farmers and provincial markets. This backend handles secure user registration, asynchronous package tracking, and a smart caching system for shipping tariffs to ensure the platform remains fast even on slow rural mobile data networks.

## Security Decisions
1. Rate Limiting Strategy
Decision: Implemented a LoginAttemptThrottle with a limit of 5 attempts per minute.

Why: I chose this limit to balance user experience with security. A human agent may occasionally forget a password, but more than five attempts in a minute typically signals a Brute-Force or Credential Stuffing attack. By throttling at the application level, you preserve server resources and protect user accounts.

2. Token Expiry & Management
Decision: Access tokens expire in 15 minutes, while Refresh tokens expire in 24 hours.

Why: Short-lived access tokens ensure that if a token is intercepted, its utility is highly restricted. The 24-hour refresh window is designed to match a standard logistics shift, allowing agents to stay "LockedIn" to their work without repeated logins, provided their session remains active.

3. Encryption Standard
Decision: Utilized Fernet (AES-128) symmetric encryption for Rwandan National IDs.

Why: Unlike simple hashing, you need to occasionally view the ID for verification. Fernet ensures the data is "scrambled" at rest in the database, satisfying compliance requirements for sensitive PII.

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

## Security Demonstration Video
I have recorded a 6-minute technical walkthrough of the security implementation for IshemaLink. 

> [!IMPORTANT]
> **[Watch the IshemaLink Security Demo here](https://drive.google.com/file/d/1FszOEY5wdoDNDLTvAHOybR_BufwJu22r/view?usp=sharing)**



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