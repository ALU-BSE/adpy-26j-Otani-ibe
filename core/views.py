from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class IshemaLinkTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = getattr(user, 'this_user_is_either_an_agent_or_a_customer_type', 'DRIVER')
        return token

class IshemaLinkTokenView(TokenObtainPairView):
    serializer_class = IshemaLinkTokenSerializer

class VeryStrictThrottle(AnonRateThrottle):
    rate = '2/minute' 

class SessionLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [VeryStrictThrottle] 

    def get(self, request):
        return Response({
            "message": "Login Page Active",
            "instructions": "Use the POST box below to write your username and password."
        })

    def post(self, request):
        username_input = request.data.get('username')
        password_input = request.data.get('password')
        
        user_match = authenticate(username=username_input, password=password_input)
        
        if user_match is not None:
            login(request, user_match)
            return Response({"message": "Session Login Successful!", "user": user_match.username})
        
        return Response({"error": "Invalid credentials"}, status=401)

class UniversalLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out"})

class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        method = "JWT Token" if request.auth else "Session Cookie"
        return Response({
            "username": request.user.username,
            "auth_method": method,
            "role": getattr(request.user, 'this_user_is_either_an_agent_or_a_customer_type', 'DRIVER')
        })