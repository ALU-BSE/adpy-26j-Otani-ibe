from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
import random

# Task 2: SMS OTP Simulation
class SendIdentityOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get('phone_number_input')
        
        # Beginner logic: make a simple 6-digit code
        secret_code = str(random.randint(100000, 999999))
        
        # Store in cache for 5 minutes (300 seconds)
        cache.set(f"otp_check_{request.user.username}", secret_code, 300)
        
        # We print it to the terminal so you can see it
        print(f"--- [SMS SIMULATION] ---")
        print(f"To: {phone}")
        print(f"Message: Your IshemaLink Identity Code is {secret_code}")
        print(f"-----------------------")
        
        return Response({"message": "Code sent! Please check your terminal console."})

# Task 2: Verify the Code and the NID
class CompleteIdentityVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code_from_user = request.data.get('otp_code_input')
        nid_from_user = request.data.get('nid_number_input')
        
        # 1. Check the OTP from the cache
        saved_code = cache.get(f"otp_check_{request.user.username}")
        
        if code_from_user != saved_code:
            return Response({"error": "Wrong or expired OTP code"}, status=400)
        
        # 2. Validate NID: Must be 16 digits
        if len(nid_from_user) == 16 and nid_from_user.isdigit():
            # Success! Update the user
            current_user = request.user
            current_user.the_16_digit_rwandan_nid_number = nid_from_user
            current_user.is_identity_verified_by_system = True
            current_user.save()
            
            return Response({
                "status": "Verified",
                "message": f"Identity confirmed for {current_user.username}. You can now handle cargo."
            })
        
        return Response({"error": "NID must be exactly 16 digits"}, status=400)