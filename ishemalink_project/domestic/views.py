from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Shipment
import asyncio 
from django.core.paginator import Paginator 
from core.services import sms_sender_function

@api_view(['POST'])
@permission_classes([AllowAny])
def update_one_package(request, pk):
    item = Shipment.objects.get(id=pk)
    
    new_s = request.data.get('status')
    item.status = new_s
    item.save()
    
    sms_text = "Your package is now " + str(new_s)
    asyncio.create_task(sms_sender_function(item.receiver_phone, sms_text))
    
    return Response({"message": "Updated! Background SMS starting..."})

@api_view(['POST'])
@permission_classes([AllowAny])
def update_many_packages(request):
    ids_to_fix = request.data.get('ids') 
    the_status = request.data.get('status')
    
    for the_id in ids_to_fix:
        try:
           package = Shipment.objects.get(id=the_id)
           package.status = the_status
           package.save()
           asyncio.create_task(sms_sender_function(package.receiver_phone, "Bulk update: " + the_status))
        except:
           print("Something went wrong with id " + str(the_id))
           continue 
        
    return Response({"message": "Bulk update started for many items."})

@api_view(['GET'])
@permission_classes([AllowAny])
def list_shipments(request):
    all_items = Shipment.objects.all().order_by('-id')
    
    the_paginator = Paginator(all_items, 5) 
    
    page_num = request.GET.get('page', 1)
    page_data = the_paginator.get_page(page_num)
    
    final_list = []
    for s in page_data:
      temp_box = {
          "tracking_code": s.tracking_number,
          "status": s.status,
          "sender": s.sender_name
      }
      final_list.append(temp_box)
        
    return Response({
        "total": the_paginator.count,
        "pages": the_paginator.num_pages,
        "current": page_data.number,
        "next": page_data.has_next(),
        "data": final_list
    })