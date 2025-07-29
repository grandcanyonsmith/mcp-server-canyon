# 🚀 Deploy to Render

Your MCP server is ready to deploy to Render! Here's how to do it:

## Option 1: Deploy via Render Dashboard (Recommended)

### Step 1: Prepare Your Repository

1. **Push to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial MCP server setup"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Go to [Render.com](https://render.com)** and sign in/create account
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `mcp-server-canyon` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements_flask.txt`
   - **Start Command**: `python main_simple.py`

### Step 3: Set Environment Variables

In the Render dashboard, add these environment variables:

- **OPENAI_API_KEY**: `your-openai-api-key-here`
- **PORT**: `10000`

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (usually 2-3 minutes)
3. Your MCP server will be available at: `https://your-service-name.onrender.com`

## Option 2: Deploy via render.yaml (Automatic)

1. **Make sure render.yaml is in your repo** (already created)
2. **Go to Render Dashboard** → **"New +"** → **"Blueprint"**
3. **Connect your GitHub repository**
4. **Render will automatically use the render.yaml configuration**

## Testing Your Deployment

Once deployed, test your server:

```bash
# Health check
curl https://your-service-name.onrender.com/health

# Test search
curl -X POST https://your-service-name.onrender.com/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test search"}'
```

## Connect to ChatGPT

1. **Get your Render URL**: `https://your-service-name.onrender.com`
2. **Add `/sse/` to the end**: `https://your-service-name.onrender.com/sse/`
3. **In ChatGPT Settings**:
   - Go to **Connectors**
   - Add **MCP Server**
   - **URL**: `https://your-service-name.onrender.com/sse/`
   - **Tools**: `search`, `fetch`
   - **Approval**: Set to "Never" for automatic use

## Current Status

✅ **Working**: Basic MCP server with mock search/fetch
🔄 **Next Step**: Configure OpenAI vector store for real document search

## Upgrading to Real Vector Store

Once deployed, you can upgrade to real vector store functionality:

1. Create a vector store in OpenAI dashboard
2. Upload your documents
3. Update environment variables in Render:
   - Add `VECTOR_STORE_ID`
   - Add `ASSISTANT_ID`
4. Switch to `main_flask.py` instead of `main_simple.py`

## Troubleshooting

**Build Fails**: Check that `requirements_flask.txt` is in your repo
**Server Won't Start**: Verify environment variables are set correctly
**Can't Connect**: Make sure the URL ends with `/sse/` for MCP connections

## Your Deployment URL

After deployment, your MCP server will be available at:
`https://[your-service-name].onrender.com/sse/`

Use this URL in ChatGPT connectors! 