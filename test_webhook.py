#!/usr/bin/env python3
"""
Test script to simulate Vapi webhook events locally
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_webhook():
    """Test the webhook endpoint with simulated Vapi events"""
    
    # Your local backend URL
    webhook_url = "http://localhost:8000/vapi-webhook"
    
    # Simulate a call ended event
    test_payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": "test-call-123",
                "customer": {
                    "number": "+19252525115"  # Your test phone number
                }
            },
            "endedReason": "customer-ended-call",
            "endedAt": datetime.utcnow().isoformat()
        }
    }
    
    print("🧪 Testing webhook with simulated call ended event...")
    print(f"📞 Call ID: {test_payload['message']['call']['id']}")
    print(f"📱 Customer: {test_payload['message']['call']['customer']['number']}")
    print(f"🔚 Reason: {test_payload['message']['endedReason']}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"✅ Webhook response: {response.status_code}")
            print(f"📄 Response body: {response.text}")
            
        except Exception as e:
            print(f"❌ Webhook test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
