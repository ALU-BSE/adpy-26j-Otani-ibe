# core/views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from .validators import validate_rwanda_nid
from django.core.cache import cache 

def system_status(request):
  info_to_show = {
      "status": "Running",
      "message": "IshemaLink API is working!",
      "database": "Connected"
  }
  return JsonResponse(info_to_show)

def api_root(request):
    return JsonResponse({"message": "Welcome to IshemaLink!"})

@api_view(['POST'])
@permission_classes([AllowAny]) 
def register_user(request):

    s = UserRegistrationSerializer(data=request.data)
    if s.is_valid() == True: 
        u = s.save()
        return Response({
            "id": u.id,
            "username": u.username,
            "message": "User registered successfully!"
        }, status=201) 
    else:
     return Response(s.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny]) 
def verify_nid(request):
    the_id = request.data.get('nid', '')
    check_result = validate_rwanda_nid(the_id)
    
    if check_result == True:
        return Response({"valid": True})
    else:
        return Response({
            "valid": False, 
            "error": "Invalid NID format. Must be 16 numeric digits starting with 1."
        }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def onboard_agent(request):
    id_box = request.data.get('nid_number')
    
    if id_box == None or id_box == "":
        return Response({"error": "NID is required for Agents"}, status=400)
    
    seri = UserRegistrationSerializer(data=request.data)
    if seri.is_valid() == True:
        seri.save(user_type='AGENT') 
        return Response({"message": "Agent Onboarded Successfully!"}, status=201)
    
    return Response(seri.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def see_prices(request):
    
    sticky_note = cache.get('shipping_prices')
    
    if sticky_note == None:

        print("--- FETCHING FROM DATABASE (SLOW) ---")
        price_data = {
            "Kigali_Zone1": 1500,
            "Provinces_Zone2": 2500,
            "EAC_Zone3": 5000
        }
        cache.set('shipping_prices', price_data, 3600)
        from_where = "Database (Slow)"
    else:
        price_data = sticky_note
        from_where = "Cache (Fast Memory)"
        
    return Response({
        "info": "Current Shipping Rates",
        "data_from": from_where,
        "rates": price_data
    })