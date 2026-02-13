from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from cryptography.fernet import Fernet
import random
from .models import SecurityAuditLog # Import the log model we just created

# TASK 3: Encryption Setup
SECRET_ENCRYPTION_KEY = b'LiRXX4Y6m-WLypvpT9inGOKKC13qq-A0M9G4nUpX2us='

def encrypt_nid(plain_text_nid):
    f = Fernet(SECRET_ENCRYPTION_KEY)
    return f.encrypt(plain_text_nid.encode()).decode()

def decrypt_nid(encrypted_nid):
    f = Fernet(SECRET_ENCRYPTION_KEY)
    return f.decrypt(encrypted_nid.encode()).decode()

# TASK 2: Identity Verification
class SendIdentityOTPView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        phone = request.data.get('phone_number_input')
        secret_code = str(random.randint(100000, 999999))
        cache.set(f"otp_check_{request.user.username}", secret_code, 300)
        
        print(f"--- [SMS SIMULATION] ---")
        print(f"To: {phone}")
        print(f"Message: Your IshemaLink Identity Code is {secret_code}")
        print(f"-----------------------")
        
        return Response({"message": "Code sent! Check terminal."})

# TASK 3: Verification & Scrambling
class CompleteIdentityVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code_input = request.data.get('otp_code_input')
        nid_input = request.data.get('nid_number_input')
        saved_code = cache.get(f"otp_check_{request.user.username}")
        
        if code_input != saved_code:
            return Response({"error": "Wrong OTP code"}, status=400)
        
        if nid_input and len(nid_input) == 16:
            user = request.user
            # Encrypt the NID before saving
            user.the_16_digit_rwandan_nid_number = encrypt_nid(nid_input)
            user.is_identity_verified_by_system = True
            user.save()
            return Response({"message": "Identity Verified and Encrypted successfully!"})
            
        return Response({"error": "NID must be 16 digits"}, status=400)

# TASK 4 & 5: Masking and Audit Logging
class ViewSecureProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        encrypted_data = user.the_16_digit_rwandan_nid_number
        
        if not encrypted_data:
            return Response({"message": "Not verified yet."})

        # Decrypt for processing
        real_nid = decrypt_nid(encrypted_data)
        
        # TASK 4: Masking for Privacy
        masked_nid = real_nid[:4] + "*" * 10 + real_nid[-2:]
        
        # TASK 5: Create the Audit Log Entry
        SecurityAuditLog.objects.create(
            user=user,
            action_performed="Accessed Masked National ID Profile"
        )
        
        return Response({
            "user": user.username,
            "nid": masked_nid,
            "status": "Verified (Access Logged)"
        })