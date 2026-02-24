class NotificationEngine:
    def send_pickup_sms(self, phone, tracking_code):
        print(f"SMS SENT to {phone}: Your shipment {tracking_code} is ready for pickup!")
        return True

    def send_customs_email(self, email, tracking_code):
        print(f"EMAIL SENT to {email}: Customs docs for {tracking_code} are attached.")
        return True