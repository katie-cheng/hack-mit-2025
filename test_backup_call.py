#!/usr/bin/env python3
"""
Test call to backup number +19252525115
"""

import asyncio
import os
import time
import httpx
from datetime import datetime
from typing import Dict, Any


class AgentverseVoiceService:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
        
        if not self.api_key or not self.phone_number_id:
            print("⚠️ VAPI credentials not configured - voice calls will be simulated")
            self.simulate_mode = True
        else:
            print("✅ VAPI configured - making REAL calls")
            self.simulate_mode = False

    def send_warning_call(self, phone_number: str, homeowner_name: str = "Homeowner"):
        """Send a warning call about weather event"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        message = f"This is AURA. Our analyst agents have detected a 92% probability of a grid-straining heatwave event at 4 pm today. Would you like us to prepare your home?"
        
        if self.simulate_mode:
            print(f"📞 [SIMULATED] Warning call to {phone_number}")
            print(f"   Message: {message}")
            return {
                "success": True,
                "call_id": f"sim_{int(time.time())}",
                "message": "Warning call simulated successfully"
            }
        
        return self._make_vapi_call(phone_number, message, "warning")
    
    def send_resolution_call(self, phone_number: str, profit: float = 4.15):
        """Send a resolution call with final report"""
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            if phone_number.startswith('1') and len(phone_number) == 11:
                phone_number = '+' + phone_number
            elif len(phone_number) == 10:
                phone_number = '+1' + phone_number
        
        message = f"This is AURA with a final report. The home is now secure and operating on battery power. The energy sale was successful, generating a profit of ${profit:.2f}. The situation is managed."
        
        if self.simulate_mode:
            print(f"📞 [SIMULATED] Resolution call to {phone_number}")
            print(f"   Message: {message}")
            return {
                "success": True,
                "call_id": f"sim_{int(time.time())}",
                "message": "Resolution call simulated successfully"
            }
        
        return self._make_vapi_call(phone_number, message, "resolution")
    
    def _make_vapi_call(self, phone_number: str, message: str, call_type: str):
        """Make actual VAPI call"""
        try:
            url = "https://api.vapi.ai/call"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "phoneNumberId": self.phone_number_id,
                "customer": {
                    "number": phone_number
                },
                "assistant": {
                    "model": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo"
                    },
                    "voice": {
                        "provider": "11labs",
                        "voiceId": "21m00Tcm4TlvDq8ikWAM"
                    },
                    "firstMessage": message,
                    "endCallMessage": "Thank you for using AURA. Goodbye.",
                    "endCallPhrases": ["goodbye", "bye", "thank you", "thanks"]
                }
            }
            
            response = httpx.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                call_id = result.get("id", "unknown")
                call_status = result.get("status", "unknown")
                print(f"✅ {call_type.title()} call initiated successfully to {phone_number} (ID: {call_id}, Status: {call_status})")
                return {
                    "success": True,
                    "call_id": call_id,
                    "message": f"{call_type.title()} call initiated successfully"
                }
            else:
                error_msg = f"Failed to initiate {call_type} call: {response.text}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "message": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error initiating {call_type} call: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "message": error_msg
            }


async def test_backup_call():
    """Test call to backup number"""
    print("🧪 Testing Backup Call to +19252525115")
    print("=" * 50)
    
    # Set environment variables
    os.environ["VAPI_API_KEY"] = "12d842aa-4073-4298-bada-d22aaecd3cec"
    os.environ["VAPI_PHONE_NUMBER_ID"] = "7fad3e7f-a086-4e6d-b516-35a4c5523036"
    
    # Initialize voice service
    voice_service = AgentverseVoiceService()
    
    # Backup number
    phone_number = "+19252525115"
    
    print(f"📞 Testing with backup number: {phone_number}")
    
    # Step 1: Send permission call
    print(f"\n🚨 Step 1: Sending PERMISSION call to backup number")
    print("-" * 50)
    
    permission_result = voice_service.send_warning_call(phone_number, "Backup User")
    print(f"Permission Call Result:")
    print(f"  Success: {permission_result['success']}")
    print(f"  Call ID: {permission_result.get('call_id', 'N/A')}")
    print(f"  Message: {permission_result['message']}")
    
    # Wait for permission call to be answered
    print(f"\n⏳ Waiting 30 seconds for permission call to be answered...")
    await asyncio.sleep(30)
    
    # Step 2: Simulate pipeline execution
    print(f"\n🔍 Step 2: Simulating threat analysis and home actions")
    print("-" * 50)
    print("   - Analyzing threats for Austin, TX")
    print("   - Detected: 92% probability heatwave at 4 PM")
    print("   - Generating home actions...")
    print("   - Charging battery to 100%")
    print("   - Pre-cooling home to 68°F")
    print("   - Preparing for energy sale")
    print("   - Executing energy sale: $4.15 profit generated")
    print("   - Pipeline completed successfully")
    
    # Wait before sending completion call
    print(f"\n⏳ Waiting 10 seconds before sending completion call...")
    await asyncio.sleep(10)
    
    # Step 3: Send completion call
    print(f"\n✅ Step 3: Sending COMPLETION call to backup number")
    print("-" * 50)
    
    completion_result = voice_service.send_resolution_call(phone_number, profit=4.15)
    print(f"Completion Call Result:")
    print(f"  Success: {completion_result['success']}")
    print(f"  Call ID: {completion_result.get('call_id', 'N/A')}")
    print(f"  Message: {completion_result['message']}")
    
    # Summary
    print(f"\n📊 Backup Call Test Summary:")
    print(f"  Permission call: {'✅ Success' if permission_result['success'] else '❌ Failed'}")
    print(f"  Completion call: {'✅ Success' if completion_result['success'] else '❌ Failed'}")
    
    if permission_result['success'] and completion_result['success']:
        print(f"\n🎉 SUCCESS! Both backup calls were initiated successfully!")
        print(f"   You should receive 2 calls on {phone_number}")
        print(f"   1. Permission call asking for home preparation")
        print(f"   2. Completion call with final results")
    else:
        print(f"\n❌ Some backup calls failed. Check the error messages above.")
    
    print(f"\n✅ Backup call test completed!")


if __name__ == "__main__":
    asyncio.run(test_backup_call())
