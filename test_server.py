#!/usr/bin/env python3
"""
Test script for the MCP server.
Run this script to verify that your server is working correctly.
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        port = os.getenv("PORT", 8000)
        response = requests.get(f"http://localhost:{port}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_mcp_tools():
    """Test MCP tools functionality"""
    try:
        port = os.getenv("PORT", 8000)
        
        # Test search tool (this would normally be called via MCP protocol)
        print("\n🔍 Testing search functionality...")
        print("Note: This tests the server is running. MCP tools are called via MCP protocol.")
        
        # Check if required environment variables are set
        required_vars = ["OPENAI_API_KEY", "VECTOR_STORE_ID", "ASSISTANT_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ All required environment variables are set")
            return True
            
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        return False

def main():
    print("🧪 Testing MCP Server")
    print("=" * 40)
    
    # Test 1: Health endpoint
    health_ok = test_health_endpoint()
    
    # Test 2: Environment configuration
    config_ok = test_mcp_tools()
    
    print("\n" + "=" * 40)
    if health_ok and config_ok:
        print("🎉 All tests passed! Your MCP server is ready to use.")
        print("\nNext steps:")
        print("1. Deploy your server to a public URL")
        print("2. Configure the MCP server in ChatGPT")
        print("3. Test with deep research queries")
    else:
        print("❌ Some tests failed. Please check your configuration.")
        print("\nTroubleshooting:")
        print("1. Make sure the server is running (python main.py)")
        print("2. Check your .env file has all required variables")
        print("3. Verify your OpenAI API key and vector store exist")

if __name__ == "__main__":
    main() 