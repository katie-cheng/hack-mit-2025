#!/usr/bin/env python3
"""
Test script for AURA Smart Home Management System
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_homeowner_registration():
    """Test homeowner registration"""
    print("🏠 Testing homeowner registration...")
    
    registration_data = {
        "name": "Test Homeowner",
        "phone_number": "+1234567890"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=registration_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Registration successful: {result['message']}")
        print(f"   Homeowner ID: {result['homeowner_id']}")
        return result['homeowner_id']
    else:
        print(f"❌ Registration failed: {response.text}")
        return None

def test_get_homeowners():
    """Test getting homeowners list"""
    print("\n👥 Testing homeowners list...")
    
    response = requests.get(f"{BASE_URL}/homeowners")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total_homeowners']} homeowners")
        for homeowner in result['homeowners']:
            print(f"   - {homeowner['name']} ({homeowner['phone_number']}) - ID: {homeowner['id'][:8]}")
    else:
        print(f"❌ Failed to get homeowners: {response.text}")

def test_get_home_status():
    """Test getting home status"""
    print("\n🏡 Testing home status...")
    
    response = requests.get(f"{BASE_URL}/home-status")
    
    if response.status_code == 200:
        result = response.json()
        status = result['status']
        print(f"✅ Home status retrieved:")
        print(f"   Battery: {status['battery_level']}%")
        print(f"   Thermostat: {status['thermostat_temp']}°F")
        print(f"   Market: {status['market_status']}")
        print(f"   Solar Charging: {status['solar_charging']}")
        print(f"   AC Running: {status['ac_running']}")
    else:
        print(f"❌ Failed to get home status: {response.text}")

def test_simulate_heatwave():
    """Test heatwave simulation"""
    print("\n🌡️ Testing heatwave simulation...")
    
    response = requests.post(f"{BASE_URL}/simulate-heatwave")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Heatwave simulation initiated: {result['message']}")
        print(f"   Call initiated: {result['call_initiated']}")
        if result.get('call_id'):
            print(f"   Call ID: {result['call_id']}")
    else:
        print(f"❌ Failed to simulate heatwave: {response.text}")

def test_reset_simulation():
    """Test simulation reset"""
    print("\n🔄 Testing simulation reset...")
    
    response = requests.post(f"{BASE_URL}/simulation/reset")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Simulation reset: {result['message']}")
    else:
        print(f"❌ Failed to reset simulation: {response.text}")

def main():
    """Run all tests"""
    print("🚀 AURA Smart Home Management System - Test Suite")
    print("=" * 60)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Voice service: {health['voice_service']}")
            print(f"   Simulator: {health['simulator']}")
            print(f"   Registered homeowners: {health['registered_homeowners']}")
        else:
            print(f"❌ Backend health check failed: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
        return
    
    # Run tests
    homeowner_id = test_homeowner_registration()
    test_get_homeowners()
    test_get_home_status()
    
    if homeowner_id:
        print("\n⏳ Waiting 2 seconds before simulation...")
        time.sleep(2)
        test_simulate_heatwave()
        
        print("\n⏳ Waiting 5 seconds before reset...")
        time.sleep(5)
        test_reset_simulation()
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()
