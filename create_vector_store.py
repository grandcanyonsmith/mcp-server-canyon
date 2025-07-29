#!/usr/bin/env python3
"""
Simple script to create a vector store and assistant for the MCP server.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def create_vector_store_and_assistant():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Create a vector store
        print("📁 Creating vector store...")
        vector_store = client.beta.vector_stores.create(
            name="MCP Server Document Store"
        )
        print(f"✅ Vector store created: {vector_store.id}")
        
        # Create an assistant
        print("🤖 Creating assistant...")
        assistant = client.beta.assistants.create(
            name="MCP Vector Store Assistant",
            instructions="You are a helpful assistant that searches through documents to answer questions.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        print(f"✅ Assistant created: {assistant.id}")
        
        # Update .env file
        print("📝 Updating .env file...")
        env_content = f"""# OpenAI API Configuration
OPENAI_API_KEY={os.getenv("OPENAI_API_KEY")}

# Vector Store ID (created automatically)
VECTOR_STORE_ID={vector_store.id}

# Assistant ID (created automatically)
ASSISTANT_ID={assistant.id}

# Server Configuration
PORT=8000
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("🎉 Setup complete!")
        print(f"Vector Store ID: {vector_store.id}")
        print(f"Assistant ID: {assistant.id}")
        print("These values have been saved to your .env file")
        
        # Add a sample file
        print("\n📄 To add documents to your vector store:")
        print(f"1. Go to https://platform.openai.com/vector-stores/{vector_store.id}")
        print("2. Upload your PDF documents")
        print("3. Your MCP server will be able to search through them!")
        
        return vector_store.id, assistant.id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    create_vector_store_and_assistant() 