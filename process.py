#!/usr/bin/env python3
"""
AURA Smart Home Management System
Legacy ID processing script - no longer used in AURA system.
This file is kept for reference but the functionality has been moved to the smart home management system.
"""

import os
import base64
import json
import requests
import sys
from typing import Dict, Optional
from pathlib import Path


class IDProcessor:
    def __init__(self, api_key: str):
        """
        Initialize the ID processor with Grok API key.
        
        Args:
            api_key (str): Your XAI API key
        """
        self.api_key = api_key
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-2-vision-1212"  # Use the vision model for image processing
        
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image file to base64 string.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise Exception(f"Error encoding image: {str(e)}")
    
    def process_id_image(self, image_path: str) -> Dict[str, str]:
        """
        Process ID image and extract personal information.
        
        Args:
            image_path (str): Path to the ID image file
            
        Returns:
            Dict[str, str]: Dictionary containing extracted information
        """
        # Encode image to base64
        base64_image = self.encode_image_to_base64(image_path)
        
        # Prepare the prompt for ID information extraction
        prompt = """Please analyze this ID image and extract the following information in JSON format:
        {
            "first_name": "extracted first name",
            "last_name": "extracted last name", 
            "gender": "extracted gender (Male/Female/Other)",
            "birthday": "extracted birthday in YYYY-MM-DD format"
        }
        
        If any information is not clearly visible or readable, use "Not Found" as the value.
        Please respond with only the JSON object, no additional text."""
        
        # Prepare the request payload - try different formats
        # First, try with image in content array format
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "model": self.model,
            "stream": False,
            "temperature": 0.1
        }
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # Make API request
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            # Debug: Print response details if there's an error
            if response.status_code != 200:
                print(f"API Error - Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Try alternative format if first attempt fails
                print("Trying alternative request format...")
                alt_payload = {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{prompt}\n\n[Image attached: {base64_image[:50]}...]"
                        }
                    ],
                    "model": self.model,
                    "stream": False,
                    "temperature": 0.1,
                    "image": base64_image
                }
                
                response = requests.post(self.api_url, headers=headers, json=alt_payload)
                
                if response.status_code != 200:
                    print(f"Alternative format also failed - Status Code: {response.status_code}")
                    print(f"Response: {response.text}")
                    response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            
            # Extract the content from the response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                
                # Try to parse JSON from the response
                try:
                    # Clean the response to extract JSON
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    
                    extracted_info = json.loads(content)
                    return extracted_info
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, return the raw content
                    return {
                        "first_name": "Error parsing JSON",
                        "last_name": "Error parsing JSON",
                        "gender": "Error parsing JSON", 
                        "birthday": "Error parsing JSON",
                        "raw_response": content
                    }
            else:
                return {
                    "error": "No valid response from API",
                    "raw_response": response_data
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "first_name": "Error",
                "last_name": "Error",
                "gender": "Error",
                "birthday": "Error"
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "first_name": "Error",
                "last_name": "Error", 
                "gender": "Error",
                "birthday": "Error"
            }


def main():
    """
    Main function to demonstrate ID processing.
    """
    # Get API key from environment variable
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: Please set the XAI_API_KEY environment variable")
        print("Example: export XAI_API_KEY='your_api_key_here'")
        return
    
    # Initialize processor
    processor = IDProcessor(api_key)
    
    # Check if image path provided as command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Get image path from user input
        print("ID Image Processor with Grok API")
        print("=" * 40)
        image_path = input("Enter the path to your ID image: ").strip()
    
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return
    
    print(f"\nProcessing image: {image_path}")
    print("Please wait...")
    
    # Process the image
    result = processor.process_id_image(image_path)
    
    # Display results
    print("\nExtracted Information:")
    print("-" * 20)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()



