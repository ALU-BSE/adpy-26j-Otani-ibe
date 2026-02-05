from django.db import models

class PackageShipmentTrackingModel(models.Model):
    # Using long, literal names as a "beginner" style choice
    tracking_number_generated_by_system = models.CharField(max_length=100, unique=True)
    current_package_status_right_now = models.CharField(max_length=50, default="PENDING")
    receiver_phone_number_for_sms = models.CharField(max_length=13)
    history_of_where_the_package_has_been = models.TextField(default="Package Created")

    def __str__(self):
        return self.tracking_number_generated_by_system