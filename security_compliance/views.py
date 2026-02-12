from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
import random

# Task 2: OTP Simulation
class SendOTPView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        # Beginner logic: make a simple 6 digit code
        random_code = str(random.randint(100000, 999999))
        
        # Store in cache for 5 minutes
        cache.set(f"otp_{phone_number}", random_code, 300)
        
        # We print it so you can see it in your terminal
        print(f"--- SECURITY OTP FOR {phone_number}: {random_code} ---")
        return Response({"message": f"OTP sent to {phone_number}. Check your terminal logs!"})

# Task 2: NID Validation
class VerifyNIDView(APIView):
    def post(self, request):
        nid_to_check = request.data.get('nid_number')
        
        # Must be exactly 16 digits
        if nid_to_check and len(nid_to_check) == 16 and nid_to_check.isdigit():
            return Response({"status": "Success", "message": "NID format is valid for Rwanda"})
        return Response({"status": "Error", "message": "NID must be exactly 16 numbers"}, status=400)