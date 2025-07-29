# MCP Server for OpenAI Vector Store

A Model Context Protocol (MCP) server that integrates with OpenAI's vector stores, providing `search` and `fetch` capabilities for ChatGPT connectors and deep research.

## Features

- 🔍 **Search Tool**: Query documents in your OpenAI vector store
- 📄 **Fetch Tool**: Retrieve full document content by ID
- 🚀 **FastMCP Framework**: Built with FastMCP for optimal performance
- 🔒 **Secure**: Environment-based configuration with API key protection
- 📊 **Health Monitoring**: Built-in health check endpoint
- 🐳 **Containerized**: Docker support for easy deployment

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- OpenAI API key with access to Assistants API
- A vector store created in OpenAI with uploaded documents

### 2. Clone and Setup

```bash
git clone <your-repo-url>
cd mcp-server-canyon
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
OPENAI_API_KEY=sk-your-openai-api-key
VECTOR_STORE_ID=vs_your-vector-store-id
ASSISTANT_ID=asst_your-assistant-id
PORT=8000
```

### 4. Create Vector Store and Assistant

If you don't have a vector store yet:

1. Go to [OpenAI Platform](https://platform.openai.com/playground/assistants)
2. Create a new assistant with file search enabled
3. Upload documents to create a vector store
4. Note the vector store ID and assistant ID

Or use our helper script:

```bash
python setup_assistant.py
```

### 5. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000` (or your configured PORT).

## Deployment Options

### Replit (Recommended for Testing)

1. Import this repository to Replit
2. Add environment variables in Replit Secrets:
   - `OPENAI_API_KEY`
   - `VECTOR_STORE_ID`
   - `ASSISTANT_ID`
3. Click "Run" - Replit will handle the rest!

### Docker

```bash
# Build the image
docker build -t mcp-server-canyon .

# Run with environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e VECTOR_STORE_ID=your-vs-id \
  -e ASSISTANT_ID=your-assistant-id \
  mcp-server-canyon
```

### Railway

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically on push

### Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables

## API Endpoints

### Health Check
```
GET /health
```

Returns server status and configuration info.

### MCP Tools

The server implements the MCP protocol with these tools:

#### Search Tool
- **Purpose**: Search for relevant documents
- **Input**: `query` (string)
- **Output**: Array of search results with `id`, `title`, `text`, `url`

#### Fetch Tool
- **Purpose**: Retrieve full document content
- **Input**: `id` (string)
- **Output**: Document object with `id`, `title`, `text`, `url`, `metadata`

## ChatGPT Integration

### 1. Configure in ChatGPT

1. Go to ChatGPT Settings → Connectors
2. Add a new MCP server with your deployment URL
3. Enable the server for deep research

### 2. Use in Prompts API

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "o4-mini-deep-research",
    "input": [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Search for information about cats and their behavior"
          }
        ]
      }
    ],
    "tools": [
      {
        "type": "mcp",
        "server_label": "vector-store",
        "server_url": "https://your-deployment-url.com/sse/",
        "allowed_tools": ["search", "fetch"],
        "require_approval": "never"
      }
    ]
  }'
```

## Development

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:mcp.app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with MCP client or use in ChatGPT
```

## Configuration Options

| Environment Variable | Description | Required | Default |
|---------------------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes | - |
| `VECTOR_STORE_ID` | OpenAI vector store ID | Yes | - |
| `ASSISTANT_ID` | OpenAI assistant ID | Yes | - |
| `PORT` | Server port | No | 8000 |

## Security Notes

- Never commit your `.env` file or expose API keys
- Use environment variables for all sensitive configuration
- The server includes basic error handling and logging
- Consider implementing rate limiting for production use

## Troubleshooting

### Common Issues

**"VECTOR_STORE_ID environment variable is required"**
- Ensure your `.env` file exists and contains the vector store ID
- Check that the vector store exists in your OpenAI account

**"Assistant not found"**
- Run `python setup_assistant.py` to create an assistant
- Verify the assistant ID in your environment variables

**Search returns no results**
- Ensure your vector store contains uploaded documents
- Check that the assistant has access to the vector store

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- Check the [troubleshooting section](#troubleshooting)
- Review [OpenAI's MCP documentation](https://platform.openai.com/docs/guides/mcp)
- Open an issue in this repository 