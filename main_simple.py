#!/usr/bin/env python3
"""
Simplified MCP server for initial deployment to Render.
This version provides mock search/fetch functionality that can be extended later.
"""

import os
import logging
import json
from typing import List, Dict, Any
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

def search_documents(query: str) -> List[Dict[str, Any]]:
    """
    Mock search function for initial deployment.
    Replace this with real vector store search later.
    """
    logger.info(f"Searching for: {query}")
    
    # Mock search results
    results = [
        {
            "id": "doc_1",
            "title": f"Search result for: {query}",
            "text": f"This is a mock search result for the query '{query}'. Once you configure your OpenAI vector store, this will return real search results from your documents.",
            "url": "#doc_1"
        },
        {
            "id": "doc_2", 
            "title": "Sample Document",
            "text": "This is sample content that demonstrates how the MCP server returns search results. Upload documents to your OpenAI vector store to see real content here.",
            "url": "#doc_2"
        }
    ]
    
    logger.info(f"Found {len(results)} mock results")
    return results

def fetch_document(doc_id: str) -> Dict[str, Any]:
    """
    Mock fetch function for initial deployment.
    Replace this with real document retrieval later.
    """
    logger.info(f"Fetching document: {doc_id}")
    
    # Mock document content
    result = {
        "id": doc_id,
        "title": f"Document {doc_id}",
        "text": f"This is the full content for document {doc_id}. Once you configure your OpenAI vector store and upload documents, this will return the actual document content.",
        "url": f"#doc_{doc_id}",
        "metadata": {
            "type": "mock_document",
            "created": "2024-01-01",
            "size": len(f"Document {doc_id}") * 50
        }
    }
    
    logger.info(f"Fetched mock document: {doc_id}")
    return result

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "framework": "flask",
        "mode": "simplified",
        "message": "MCP server is running. Configure OpenAI vector store for full functionality."
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
                            "description": "Search for relevant documents (currently mock data - configure vector store for real search)",
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
                            "description": "Fetch the full content of a document by its ID (currently mock data)",
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

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with deployment info"""
    return jsonify({
        "message": "MCP Server for ChatGPT Integration",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "mcp": "/sse/",
            "search": "/search",
            "fetch": "/fetch",
            "oauth_config": "/.well-known/mcp_oauth_config",
            "oauth_authorize": "/oauth/authorize",
            "oauth_token": "/oauth/token"
        },
        "note": "This is a simplified version. Configure OpenAI vector store for full functionality."
    })

# OAuth 2.0 Endpoints for ChatGPT Connector

# Mock client credentials for demonstration
CLIENT_ID = "mcp_server_canyon_client"
CLIENT_SECRET = "mcp_server_canyon_secret_key_demo"

@app.route('/.well-known/mcp_oauth_config', methods=['GET'])
def mcp_oauth_config():
    """
    Returns the OAuth configuration for the MCP server.
    This endpoint is discovered by ChatGPT.
    """
    base_url = request.url_root.rstrip('/')
    return jsonify({
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "scopes": ["read", "write"],
        "client_id": CLIENT_ID,
        "grant_types_supported": ["authorization_code"],
        "response_types_supported": ["code"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "code_challenge_methods_supported": ["S256"],
        "issuer": base_url
    })

@app.route('/oauth/authorize', methods=['GET'])
def oauth_authorize():
    """
    Authorization endpoint for OAuth 2.0.
    In a real application, this would present a login/consent screen.
    For this demo, it auto-approves and redirects with an auth code.
    """
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    response_type = request.args.get('response_type')
    scope = request.args.get('scope', '')
    state = request.args.get('state', '')
    
    if client_id != CLIENT_ID or response_type != 'code':
        return jsonify({"error": "Invalid client_id or response_type"}), 400
    
    # Generate mock authorization code
    mock_auth_code = "mcp_auth_code_canyon_123456"
    
    # Store auth code temporarily (in real app, use proper storage)
    app.config['temp_auth_code'] = mock_auth_code
    
    # Redirect back to ChatGPT with the authorization code
    redirect_params = f"code={mock_auth_code}"
    if state:
        redirect_params += f"&state={state}"
    
    return redirect(f"{redirect_uri}?{redirect_params}")

@app.route('/oauth/token', methods=['POST'])
def oauth_token():
    """
    Token endpoint for OAuth 2.0.
    Exchanges the authorization code for an access token.
    """
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    redirect_uri = request.form.get('redirect_uri')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    
    # Validate the request
    if (grant_type != 'authorization_code' or 
        code != app.config.get('temp_auth_code') or
        client_id != CLIENT_ID or 
        client_secret != CLIENT_SECRET):
        return jsonify({"error": "invalid_grant"}), 400
    
    # Generate access token
    access_token = "mcp_access_token_canyon_abcdef123456"
    refresh_token = "mcp_refresh_token_canyon_ghijkl789012"
    expires_in = 3600  # 1 hour
    
    # Clear the authorization code after use
    app.config.pop('temp_auth_code', None)
    
    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "refresh_token": refresh_token,
        "scope": "read write"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False) 