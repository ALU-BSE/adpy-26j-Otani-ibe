from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = "Seed dummy data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        admin, created = User.objects.get_or_create(
            username="otaniibe",
            defaults={"is_staff": True, "is_superuser": True, "email": "admin@ishemalink.rw"}
        )
        if created:
            admin.set_password("otani12345")
            admin.save()
        self.stdout.write("Admin ready: otaniibe / otani12345")

        drivers = []
        for username in ["driver_mugisha","driver_uwimana","driver_habimana","driver_mukamana","driver_nshimiyimana"]:
            u, c = User.objects.get_or_create(username=username, defaults={"email": f"{username}@ishemalink.rw"})
            if c:
                u.set_password("driver12345")
                u.save()
            drivers.append(u)
        self.stdout.write("5 drivers ready")

        agents = []
        for username in ["agent_kigali","agent_musanze","agent_rubavu","agent_huye","agent_nyamagabe"]:
            u, c = User.objects.get_or_create(username=username, defaults={"email": f"{username}@ishemalink.rw"})
            if c:
                u.set_password("agent12345")
                u.save()
            agents.append(u)
        self.stdout.write("5 agents ready")

        from domestic.models import Shipment, PaymentRecord
        configs = [
            ("DOMESTIC","Kigali","Musanze",200,"PAID",0),
            ("DOMESTIC","Musanze","Kigali",350,"PAID",1),
            ("DOMESTIC","Rubavu","Kigali",500,"PAID",2),
            ("DOMESTIC","Huye","Kigali",150,"PAID",0),
            ("DOMESTIC","Nyamagabe","Kigali",1000,"PAID",3),
            ("DOMESTIC","Kigali","Butare",250,"PAID",1),
            ("DOMESTIC","Gisenyi","Kigali",400,"PENDING",None),
            ("DOMESTIC","Kigali","Musanze",180,"PENDING",None),
            ("DOMESTIC","Huye","Musanze",300,"FAILED",None),
            ("DOMESTIC","Rubavu","Huye",220,"PAID",4),
            ("INTERNATIONAL","Kigali","Nairobi",500,"PAID",2),
            ("INTERNATIONAL","Kigali","Mombasa",800,"PAID",0),
            ("INTERNATIONAL","Kigali","Kampala",300,"PAID",1),
            ("INTERNATIONAL","Rubavu","Bujumbura",450,"PAID",3),
            ("INTERNATIONAL","Kigali","Dar es Salaam",600,"PENDING",None),
            ("INTERNATIONAL","Musanze","Nairobi",350,"PAID",4),
            ("DOMESTIC","Nyamagabe","Kigali",750,"PAID",0),
            ("DOMESTIC","Kigali","Gisenyi",120,"PAID",2),
            ("INTERNATIONAL","Kigali","Kampala",200,"FAILED",None),
            ("DOMESTIC","Butare","Kigali",480,"PAID",1),
        ]
        for i, (stype, origin, dest, weight, status, didx) in enumerate(configs):
            rate = Decimal("500") if stype == "DOMESTIC" else Decimal("1200")
            tariff = Decimal(weight) * rate
            shipment = Shipment.objects.create(
                sender=agents[i % len(agents)],
                shipment_type=stype, origin=origin, destination=dest,
                weight_kg=Decimal(weight), tariff_amount=tariff,
                payment_status=status,
                driver_assigned=drivers[didx] if didx is not None else None,
                ebm_signature=f"RRA-EBM-{uuid.uuid4().hex[:10].upper()}" if status=="PAID" else None,
            )
            if status in ("PAID","FAILED"):
                PaymentRecord.objects.create(
                    shipment=shipment,
                    transaction_id=f"MOMO-SEED-{uuid.uuid4().hex[:8].upper()}",
                    amount=tariff, is_confirmed=(status=="PAID"),
                )
        total = Shipment.objects.count()
        paid = Shipment.objects.filter(payment_status="PAID").count()
        self.stdout.write(f"{total} shipments seeded ({paid} PAID)")
        self.stdout.write("Done! otaniibe/otani12345  |  driver_mugisha/driver12345  |  agent_kigali/agent12345")
