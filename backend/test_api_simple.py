#!/usr/bin/env python3
"""
Simple API test to verify ModelScope connection
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.openai_client import openai_client

async def test_api():
    """Test the ModelScope API connection"""
    print("Testing ModelScope API connection...")

    try:
        # Simple test message
        messages = [
            {"role": "user", "content": "Hello, please respond with 'API test successful'"}
        ]

        print("Sending test request...")
        # Test with default model
        print("Testing with default model...")
        response = openai_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=50
        )
        print(f"Response: {response[:200]}...")

        print("API test completed!")

    except Exception as e:
        print(f"API test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())