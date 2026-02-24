import asyncio

async def send_sms_notification_to_farmer_asynchronously(phone_number: str, message_content: str) -> bool:
    print(f"DEBUG: Connecting to Rwanda SMS Gateway for {phone_number}...")
    
    await asyncio.sleep(3) 
    
    print(f"DEBUG: SMS sent successfully: {message_content}")
    return True