from locust import HttpUser, task, between
import random

cities = [
    "Kigali", "Musanze", "Butare", "Gisenyi", "Rwamagana",
    "Nyagatare", "Rubavu", "Muhanga", "Huye", "Rusizi"
]

class ShipmentUser(HttpUser):
    wait_time = between(1, 2)
    
    username = "otaniibe"
    password = "otani12345"

    @task(1)
    def create_shipment(self):
        origin, destination = random.sample(cities, 2)
        
        prefix = random.choice(["078", "079", "073", "072"])
        number = random.randint(1000000, 9999999)
        phone = f"{prefix}{number}"
        
        weight = f"{random.uniform(0.5, 99.99):.2f}"
        
        payload = {
            "shipment_type": random.choice(["DOMESTIC", "INTERNATIONAL"]),
            "origin": origin,
            "destination": destination,
            "weight_kg": weight,
            "phone": phone,
        }
        
        response = self.client.post(
            "/api/shipments/create/",
            json=payload,
            auth=(self.username, self.password),
            name="POST /api/shipments/create/"
        )
        
        if response.status_code not in [200, 201]:
            print(f"something went wrong: {response.status_code} - {response.text}")

    @task(2)
    def check_status(self):
        self.client.get("/api/status/", name="GET /api/status/")