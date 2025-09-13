#!/usr/bin/env python3
"""
Example usage of the ID Processor with Grok API
"""

import os
from process import IDProcessor

def example_usage():
    """
    Example of how to use the IDProcessor class programmatically.
    """
    # Set your API key (you can also set it as an environment variable)
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        print("Please set your XAI_API_KEY environment variable")
        print("Example: export XAI_API_KEY='your_api_key_here'")
        return
    
    # Initialize the processor
    processor = IDProcessor(api_key)
    
    # Example image path (replace with your actual image path)
    image_path = "path/to/your/id_image.jpg"
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        print("Please update the image_path variable with a valid image file")
        return
    
    # Process the image
    print(f"Processing ID image: {image_path}")
    result = processor.process_id_image(image_path)
    
    # Print the results
    print("\nExtracted Information:")
    print("=" * 30)
    for key, value in result.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    example_usage()
