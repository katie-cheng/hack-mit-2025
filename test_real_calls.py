#!/usr/bin/env python3
"""
Test script for AURA with real phone calls
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_real_voice_calls():
    print("🚀 AURA Real Voice Call Test")
    print("=" * 50)
    
    # Test with Tony's phone number
    phone_number = "+19259892492"
    
    # Register homeowner with real phone number
    print(f"🏠 Registering homeowner with phone: {phone_number}")
    registration_data = {
        "name": "Tony Wang",
        "phone_number": phone_number
    }
    
    response = requests.post(f"{BASE_URL}/register", json=registration_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Registration successful: {result['message']}")
        print(f"   Homeowner ID: {result['homeowner_id']}")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    print(f"\n⏳ Waiting 2 seconds before simulation...")
    time.sleep(2)
    
    # Test heatwave simulation with real voice call
    print(f"🌡️ Testing heatwave simulation with real voice call to {phone_number}...")
    simulation_data = {
        "phone_number": phone_number
    }
    
    response = requests.post(f"{BASE_URL}/simulate-heatwave", json=simulation_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Heatwave simulation initiated: {result['message']}")
        print(f"   Call initiated: {result['call_initiated']}")
        if 'call_id' in result:
            print(f"   Call ID: {result['call_id']}")
    else:
        print(f"❌ Simulation failed: {response.text}")
        return
    
    print(f"\n⏳ Waiting 10 seconds for simulation to complete...")
    time.sleep(10)
    
    # Check home status
    print(f"🏡 Checking final home status...")
    response = requests.get(f"{BASE_URL}/home-status")
    if response.status_code == 200:
        result = response.json()
        status = result['status']
        print(f"✅ Final home status:")
        print(f"   Battery: {status['battery_level']}%")
        print(f"   Thermostat: {status['thermostat_temp']}°F")
        print(f"   Market: {status['market_status']}")
        print(f"   Solar Charging: {status['solar_charging']}")
        print(f"   AC Running: {status['ac_running']}")
    
    print(f"\n🎉 Real voice call test completed!")
    print(f"📞 Check your phone ({phone_number}) for the AURA calls!")

if __name__ == "__main__":
    test_real_voice_calls()
