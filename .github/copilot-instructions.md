# Copilot Instructions

## Project overview
- Django 6 project with three apps: core, domestic, international.
- Custom user model lives in core.models.IshemaLinkUserAccountModel and is wired via AUTH_USER_MODEL in settings.
- API endpoints are defined in ishemalink.urls; core provides auth/NID validation, domestic handles shipment tracking.

## Key patterns and conventions
- Views in core use Django REST Framework APIView/Response; request data is read manually (see core.views).
- Validation rules are centralized in core.validators and reused by views.
- Domestic shipment endpoints are async and use Django async ORM methods (aget/asave) plus asyncio.create_task for background SMS.
- Shipment tracking is stored in domestic.models.PackageShipmentTrackingModel; status is updated to ARRIVED_AT_HUB in the async flow.
- SMS sending is simulated with an async helper in domestic.notifications.
- Tests exist for validators in core.tests; use them as examples for new unit tests.

## Data and configuration
- Default database is SQLite at db.sqlite3.
- Settings module is ishemalink.settings; AUTH_USER_MODEL is set there.

## Common dev workflows
- Run server: python manage.py runserver
- Migrations: python manage.py makemigrations && python manage.py migrate
- Tests: python manage.py test

## Integration notes
- DRF is used (rest_framework) for API views in core.
- Async views and tasks rely on asyncio; keep the async/await style consistent when extending shipment flows.
