#!/usr/bin/env python3
"""
Test both warning and resolution calls
"""

import asyncio
import os
import time
import httpx
from datetime import datetime
from typing import Dict, Any


class AURAVoiceService:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
        
        if not self.api_key or not self.phone_number_id:
            print("❌ VAPI credentials not configured!")
            exit(1)
        else:
            print("✅ VAPI configured - making REAL calls")

    async def send_warning_call(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send the warning call to homeowner"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        # Create assistant context for the warning call
        assistant_context = f"""
You are AURA, an AI smart home management system. You are calling a homeowner about a potential weather event.

URGENT ALERT: {message}

INSTRUCTIONS:
1. Clearly communicate the urgent alert message above
2. Ask if they want you to prepare their home for the event
3. If they say "yes" or agree, respond: "Great. Executing resilience now. We'll give you a ring when we've made our plan."
4. If they say "no" or decline, respond: "Understood. We'll continue monitoring the situation and will contact you if conditions change."
5. Keep the conversation brief and professional
6. Always end with a clear next step

Remember: You are a helpful AI assistant managing their smart home. Be reassuring but urgent about the situation.
"""
        
        async with httpx.AsyncClient() as client:
            try:
                call_payload = {
                    "phoneNumberId": self.phone_number_id,
                    "customer": {"number": phone_number},
                    "assistant": {
                        "firstMessage": f"This is AURA. {message}",
                        "model": {
                            "provider": "xai",
                            "model": "grok-3",
                            "temperature": 0.1,
                            "messages": [
                                {"role": "system", "content": assistant_context},
                                {
                                    "role": "user",
                                    "content": message,
                                },
                            ],
                        },
                        "voice": {"provider": "11labs", "voiceId": "burt"},
                    },
                }

                print(f"📞 Making WARNING call to {phone_number}")
                
                response = await client.post(
                    "https://api.vapi.ai/call",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=call_payload,
                )

                if response.status_code == 201:
                    call_data = response.json()
                    return {
                        "success": True,
                        "call_id": call_data.get("id"),
                        "message": "Warning call initiated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code} - {response.text}"
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

    async def send_resolution_call(self, phone_number: str, profit: float = 4.15) -> Dict[str, Any]:
        """Send the resolution call with final report"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        # Create the resolution message
        resolution_message = f"This is AURA with a final report. The home is now secure and operating on battery power. The energy sale was successful, generating a profit of ${profit:.2f}. The situation is managed."
        
        # Create assistant context for the resolution call
        assistant_context = f"""
You are AURA, an AI smart home management system. You are calling a homeowner with a final report after successfully managing a weather event.

FINAL REPORT: {resolution_message}

INSTRUCTIONS:
1. Clearly communicate the final report message above
2. Provide a brief summary of what was accomplished:
   - Home is now secure and operating on battery power
   - Energy sale was successful
   - Profit generated: ${profit:.2f}
   - Situation is fully managed
3. Ask if they have any questions about the actions taken
4. Keep the conversation brief and professional
5. End with reassurance that their home is protected

Remember: You are providing a positive update about successful home protection. Be confident and reassuring.
"""
        
        async with httpx.AsyncClient() as client:
            try:
                call_payload = {
                    "phoneNumberId": self.phone_number_id,
                    "customer": {"number": phone_number},
                    "assistant": {
                        "firstMessage": resolution_message,
                        "model": {
                            "provider": "xai",
                            "model": "grok-3",
                            "temperature": 0.1,
                            "messages": [
                                {"role": "system", "content": assistant_context},
                                {
                                    "role": "user",
                                    "content": resolution_message,
                                },
                            ],
                        },
                        "voice": {"provider": "11labs", "voiceId": "burt"},
                    },
                }

                print(f"📞 Making RESOLUTION call to {phone_number}")
                
                response = await client.post(
                    "https://api.vapi.ai/call",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=call_payload,
                )

                if response.status_code == 201:
                    call_data = response.json()
                    return {
                        "success": True,
                        "call_id": call_data.get("id"),
                        "message": "Resolution call initiated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code} - {response.text}"
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }


async def test_both_calls():
    """Test both warning and resolution calls"""
    print("📞 Testing Both Warning and Resolution Calls")
    print("=" * 60)
    
    # Initialize voice service
    voice_service = AURAVoiceService()
    
    # Test number
    phone_number = "+19259892492"
    
    # Step 1: Send warning call
    print("\n🚨 Step 1: Sending WARNING call")
    print("-" * 40)
    
    warning_message = "Our analyst agents have detected a 92% probability of a grid-straining heatwave event at 4 pm today. Would you like us to prepare your home?"
    
    warning_result = await voice_service.send_warning_call(phone_number, warning_message)
    
    print(f"Warning Call Result:")
    print(f"Success: {warning_result.get('success', False)}")
    print(f"Call ID: {warning_result.get('call_id', 'N/A')}")
    print(f"Message: {warning_result.get('message', 'N/A')}")
    
    if warning_result.get('error'):
        print(f"Error: {warning_result.get('error')}")
    
    # Wait for warning call to be answered (30 seconds)
    print(f"\n⏳ Waiting 30 seconds for warning call to be answered...")
    await asyncio.sleep(30)
    
    # Step 2: Simulate home actions (battery charging, AC cooling, etc.)
    print(f"\n🏠 Step 2: Simulating home actions")
    print("-" * 40)
    print("   - Charging battery to 100%")
    print("   - Pre-cooling home to 68°F")
    print("   - Preparing for energy sale")
    print("   - Actions completed successfully")
    
    # Wait a bit more before sending resolution call
    print(f"\n⏳ Waiting 10 seconds before sending resolution call...")
    await asyncio.sleep(10)
    
    # Step 3: Send resolution call
    print(f"\n✅ Step 3: Sending RESOLUTION call")
    print("-" * 40)
    
    resolution_result = await voice_service.send_resolution_call(phone_number, profit=4.15)
    
    print(f"Resolution Call Result:")
    print(f"Success: {resolution_result.get('success', False)}")
    print(f"Call ID: {resolution_result.get('call_id', 'N/A')}")
    print(f"Message: {resolution_result.get('message', 'N/A')}")
    
    if resolution_result.get('error'):
        print(f"Error: {resolution_result.get('error')}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"Warning call: {'✅ Success' if warning_result.get('success') else '❌ Failed'}")
    print(f"Resolution call: {'✅ Success' if resolution_result.get('success') else '❌ Failed'}")
    
    print(f"\n✅ Both calls test completed!")


if __name__ == "__main__":
    asyncio.run(test_both_calls())
