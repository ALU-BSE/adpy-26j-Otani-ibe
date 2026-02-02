import asyncio

async def sms_sender_function(phone_number, the_msg): # No more type hints
    
    print("--- START: Sending SMS to " + str(phone_number) + " ---")
    
    await asyncio.sleep(3) 
    
    print("--- SUCCESS: Notification sent: " + the_msg + " ---")
    
    return True