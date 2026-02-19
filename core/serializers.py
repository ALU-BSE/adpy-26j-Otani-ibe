from rest_framework import serializers

class ShipmentCreateSerializer(serializers.Serializer):
    shipment_type = serializers.ChoiceField(choices=['DOMESTIC', 'INTERNATIONAL'])
    origin = serializers.CharField(max_length=100)
    destination = serializers.CharField(max_length=100)
    weight_kg = serializers.DecimalField(max_digits=10, decimal_places=2)
    phone = serializers.CharField(max_length=15)

class PaymentWebhookSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=100)
    status = serializers.ChoiceField(choices=['SUCCESS', 'FAILED'])