from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Beginner logic: explicitly adding user data to the encrypted token
class IshemaLinkTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims for Task 1 requirement
        token['username'] = user.username
        token['user_type'] = getattr(user, 'this_user_is_either_an_agent_or_a_customer_type', 'DRIVER')
        
        return token

class IshemaLinkTokenView(TokenObtainPairView):
    serializer_class = IshemaLinkTokenSerializer