#!/usr/bin/env python3
"""
Helper script to create an OpenAI assistant with file search capabilities.
Run this script to set up the assistant for your MCP server.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def create_assistant():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Get vector store ID
    vector_store_id = os.getenv("VECTOR_STORE_ID")
    if not vector_store_id:
        print("Error: VECTOR_STORE_ID not found in environment variables")
        return None
    
    try:
        # Create an assistant with file search enabled
        assistant = client.beta.assistants.create(
            name="Vector Store Search Assistant",
            instructions="You are a helpful assistant that searches through documents in a vector store to answer questions. When users ask questions, search through the available documents and provide accurate, relevant responses based on the content found.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        
        print(f"✅ Assistant created successfully!")
        print(f"Assistant ID: {assistant.id}")
        print(f"Add this to your .env file:")
        print(f"ASSISTANT_ID={assistant.id}")
        
        return assistant.id
        
    except Exception as e:
        print(f"❌ Error creating assistant: {e}")
        return None

def list_vector_stores():
    """List available vector stores"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        vector_stores = client.beta.vector_stores.list()
        print("\n📁 Available Vector Stores:")
        for vs in vector_stores.data:
            print(f"  ID: {vs.id}")
            print(f"  Name: {vs.name}")
            print(f"  File Count: {vs.file_counts.total}")
            print(f"  Created: {vs.created_at}")
            print("  ---")
    except Exception as e:
        print(f"❌ Error listing vector stores: {e}")

if __name__ == "__main__":
    print("🚀 Setting up OpenAI Assistant for MCP Server")
    print("=" * 50)
    
    # Check if API key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        exit(1)
    
    # List vector stores first
    list_vector_stores()
    
    # Create assistant
    assistant_id = create_assistant()
    
    if assistant_id:
        print(f"\n🎉 Setup complete! Your MCP server is ready to use.")
        print(f"Remember to add ASSISTANT_ID={assistant_id} to your .env file")
    else:
        print("\n❌ Setup failed. Please check your configuration and try again.") 