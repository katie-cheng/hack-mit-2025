#!/usr/bin/env python3
"""
Simple test script to debug Grok API calls
"""

import os
import requests
import json

def test_grok_api():
    """
    Test basic Grok API functionality
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: Please set the XAI_API_KEY environment variable")
        return
    
    # Test 1: Basic text-only request
    print("Test 1: Basic text request")
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you help me?"
            }
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Basic text request successful")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Basic text request failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Try different model names
    models_to_try = ["grok-2", "grok-3", "grok-2-vision-1212", "grok-2-image-1212", "grok-vision"]
    
    for model in models_to_try:
        print(f"Test 2: Testing model '{model}'")
        payload["model"] = model
        
        try:
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload)
            print(f"Model '{model}' - Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Model '{model}' works!")
                break
            else:
                print(f"❌ Model '{model}' failed: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ Model '{model}' error: {e}")
        print()
    
    # Test 3: Test image functionality with grok-2
    print("Test 3: Testing image functionality with grok-2")
    # Create a simple test image (1x1 pixel)
    import base64
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    image_payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What do you see in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{test_image}"
                        }
                    }
                ]
            }
        ],
        "model": "grok-2-vision-1212",
        "stream": False,
        "temperature": 0.1
    }
    
    try:
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=image_payload)
        print(f"Image test - Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Image functionality works with grok-2!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Image functionality failed: {response.text}")
    except Exception as e:
        print(f"❌ Image test error: {e}")

if __name__ == "__main__":
    test_grok_api()
