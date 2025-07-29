#!/usr/bin/env python3
"""
Alternative MCP server implementation using Flask for Python 3.9+ compatibility.
This provides the same functionality as the FastMCP version but with broader compatibility.
"""

import os
import logging
import json
from typing import List, Dict, Any
from flask import Flask, request, jsonify, Response
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get vector store ID from environment
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

if not VECTOR_STORE_ID:
    raise ValueError("VECTOR_STORE_ID environment variable is required")

def search_documents(query: str) -> List[Dict[str, Any]]:
    """
    Search for relevant documents in the vector store.
    
    Args:
        query: The search query string
        
    Returns:
        Array of search results with id, title, text, and url
    """
    try:
        logger.info(f"Searching for: {query}")
        
        # Create a thread for the search
        thread = client.beta.threads.create()
        
        # Add the search query as a message
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Run the assistant with vector store
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=os.getenv("ASSISTANT_ID"),
            tool_resources={
                "file_search": {
                    "vector_store_ids": [VECTOR_STORE_ID]
                }
            }
        )
        
        # Get the messages
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        
        results = []
        
        if messages.data:
            latest_message = messages.data[0]
            if latest_message.content:
                content = latest_message.content[0]
                if hasattr(content, 'text'):
                    text_content = content.text.value
                    
                    # Extract file citations if available
                    citations = []
                    if hasattr(content.text, 'annotations'):
                        for annotation in content.text.annotations:
                            if hasattr(annotation, 'file_citation'):
                                citations.append(annotation.file_citation.file_id)
                    
                    # Create search results from the response
                    results.append({
                        "id": f"search_result_{thread.id}",
                        "title": f"Search result for: {query}",
                        "text": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                        "url": f"#search_{thread.id}"
                    })
                    
                    # Add individual file results if citations exist
                    for i, file_id in enumerate(citations):
                        results.append({
                            "id": file_id,
                            "title": f"Document {i+1}",
                            "text": f"Referenced document in search for: {query}",
                            "url": f"#file_{file_id}"
                        })
        
        # Clean up the thread
        try:
            client.beta.threads.delete(thread.id)
        except Exception as e:
            logger.warning(f"Failed to delete thread: {e}")
        
        logger.info(f"Found {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return [{
            "id": "error",
            "title": "Search Error",
            "text": f"An error occurred while searching: {str(e)}",
            "url": "#error"
        }]

def fetch_document(doc_id: str) -> Dict[str, Any]:
    """
    Fetch the full content of a document by its ID.
    
    Args:
        doc_id: The unique identifier for the document
        
    Returns:
        Document object with id, title, text, url, and metadata
    """
    try:
        logger.info(f"Fetching document: {doc_id}")
        
        # If it's a file ID, try to retrieve the file content
        if doc_id.startswith("file-"):
            try:
                file_info = client.files.retrieve(doc_id)
                file_content = client.files.content(doc_id)
                
                return {
                    "id": doc_id,
                    "title": file_info.filename,
                    "text": file_content.text if hasattr(file_content, 'text') else "Binary file content not available",
                    "url": f"#file_{doc_id}",
                    "metadata": {
                        "filename": file_info.filename,
                        "purpose": file_info.purpose,
                        "bytes": file_info.bytes,
                        "created_at": file_info.created_at
                    }
                }
            except Exception as e:
                logger.error(f"Error fetching file {doc_id}: {e}")
                return {
                    "id": doc_id,
                    "title": "File Not Found",
                    "text": f"Could not retrieve file with ID {doc_id}: {str(e)}",
                    "url": f"#file_{doc_id}",
                    "metadata": {"error": str(e)}
                }
        
        # For other IDs, create a thread and search for specific content
        thread = client.beta.threads.create()
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Please provide the full content related to ID: {doc_id}"
        )
        
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=os.getenv("ASSISTANT_ID"),
            tool_resources={
                "file_search": {
                    "vector_store_ids": [VECTOR_STORE_ID]
                }
            }
        )
        
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        
        result = {
            "id": doc_id,
            "title": f"Document {doc_id}",
            "text": "No content found",
            "url": f"#doc_{doc_id}",
            "metadata": {}
        }
        
        if messages.data:
            latest_message = messages.data[0]
            if latest_message.content:
                content = latest_message.content[0]
                if hasattr(content, 'text'):
                    result["text"] = content.text.value
                    result["title"] = f"Full content for {doc_id}"
        
        # Clean up the thread
        try:
            client.beta.threads.delete(thread.id)
        except Exception as e:
            logger.warning(f"Failed to delete thread: {e}")
        
        logger.info(f"Fetched document: {doc_id}")
        return result
        
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return {
            "id": doc_id,
            "title": "Fetch Error",
            "text": f"An error occurred while fetching document {doc_id}: {str(e)}",
            "url": f"#error_{doc_id}",
            "metadata": {"error": str(e)}
        }

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "vector_store_id": VECTOR_STORE_ID,
        "framework": "flask"
    })

# MCP Server-Sent Events endpoint
@app.route('/sse/', methods=['POST'])
def mcp_sse():
    """Handle MCP requests via Server-Sent Events"""
    try:
        data = request.get_json()
        
        # Basic MCP request handling
        if 'method' in data:
            method = data['method']
            params = data.get('params', {})
            
            if method == 'tools/call':
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                if tool_name == 'search':
                    query = arguments.get('query', '')
                    results = search_documents(query)
                    return jsonify({
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(results)
                            }
                        ]
                    })
                
                elif tool_name == 'fetch':
                    doc_id = arguments.get('id', '')
                    result = fetch_document(doc_id)
                    return jsonify({
                        "content": [
                            {
                                "type": "text", 
                                "text": json.dumps(result)
                            }
                        ]
                    })
            
            elif method == 'tools/list':
                return jsonify({
                    "tools": [
                        {
                            "name": "search",
                            "description": "Search for relevant documents in the vector store",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The search query string"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "fetch",
                            "description": "Fetch the full content of a document by its ID",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "The unique identifier for the document"
                                    }
                                },
                                "required": ["id"]
                            }
                        }
                    ]
                })
        
        return jsonify({"error": "Invalid request"}), 400
        
    except Exception as e:
        logger.error(f"MCP SSE error: {e}")
        return jsonify({"error": str(e)}), 500

# Simple tool endpoints for testing
@app.route('/search', methods=['POST'])
def search_endpoint():
    """Direct search endpoint for testing"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        results = search_documents(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch', methods=['POST'])
def fetch_endpoint():
    """Direct fetch endpoint for testing"""
    try:
        data = request.get_json()
        doc_id = data.get('id', '')
        result = fetch_document(doc_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False) 