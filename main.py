import os
import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get vector store ID from environment
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

if not VECTOR_STORE_ID:
    raise ValueError("VECTOR_STORE_ID environment variable is required")

# Initialize FastMCP
mcp = FastMCP("Vector Store MCP Server")

@mcp.tool()
def search(query: str) -> List[Dict[str, Any]]:
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
            assistant_id=os.getenv("ASSISTANT_ID"),  # You'll need to create an assistant
            tool_resources={
                "file_search": {
                    "vector_store_ids": [VECTOR_STORE_ID]
                }
            }
        )
        
        # Get the messages
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        
        # For now, return a simplified search result
        # In a real implementation, you'd parse the vector store search results
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

@mcp.tool()
def fetch(id: str) -> Dict[str, Any]:
    """
    Fetch the full content of a document by its ID.
    
    Args:
        id: The unique identifier for the document
        
    Returns:
        Document object with id, title, text, url, and metadata
    """
    try:
        logger.info(f"Fetching document: {id}")
        
        # If it's a file ID, try to retrieve the file content
        if id.startswith("file-"):
            try:
                file_info = client.files.retrieve(id)
                file_content = client.files.content(id)
                
                return {
                    "id": id,
                    "title": file_info.filename,
                    "text": file_content.text if hasattr(file_content, 'text') else "Binary file content not available",
                    "url": f"#file_{id}",
                    "metadata": {
                        "filename": file_info.filename,
                        "purpose": file_info.purpose,
                        "bytes": file_info.bytes,
                        "created_at": file_info.created_at
                    }
                }
            except Exception as e:
                logger.error(f"Error fetching file {id}: {e}")
                return {
                    "id": id,
                    "title": "File Not Found",
                    "text": f"Could not retrieve file with ID {id}: {str(e)}",
                    "url": f"#file_{id}",
                    "metadata": {"error": str(e)}
                }
        
        # For other IDs, create a thread and search for specific content
        thread = client.beta.threads.create()
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Please provide the full content related to ID: {id}"
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
            "id": id,
            "title": f"Document {id}",
            "text": "No content found",
            "url": f"#doc_{id}",
            "metadata": {}
        }
        
        if messages.data:
            latest_message = messages.data[0]
            if latest_message.content:
                content = latest_message.content[0]
                if hasattr(content, 'text'):
                    result["text"] = content.text.value
                    result["title"] = f"Full content for {id}"
        
        # Clean up the thread
        try:
            client.beta.threads.delete(thread.id)
        except Exception as e:
            logger.warning(f"Failed to delete thread: {e}")
        
        logger.info(f"Fetched document: {id}")
        return result
        
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return {
            "id": id,
            "title": "Fetch Error",
            "text": f"An error occurred while fetching document {id}: {str(e)}",
            "url": f"#error_{id}",
            "metadata": {"error": str(e)}
        }

# Health check endpoint
@mcp.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "vector_store_id": VECTOR_STORE_ID}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(mcp.app, host="0.0.0.0", port=port) 