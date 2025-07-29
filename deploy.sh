#!/bin/bash

# MCP Server Deployment Script
# This script helps you set up and deploy your MCP server

set -e

echo "🚀 MCP Server Deployment Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

print_status "Python found: $(python3 --version)"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your API keys and IDs before continuing."
    echo "Required variables:"
    echo "  - OPENAI_API_KEY"
    echo "  - VECTOR_STORE_ID" 
    echo "  - ASSISTANT_ID"
    echo ""
    read -p "Press Enter after you've configured .env..."
fi

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Check environment variables
print_status "Checking environment configuration..."
source .env

if [ -z "$OPENAI_API_KEY" ]; then
    print_error "OPENAI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$VECTOR_STORE_ID" ]; then
    print_error "VECTOR_STORE_ID not set in .env file"
    exit 1
fi

if [ -z "$ASSISTANT_ID" ]; then
    print_warning "ASSISTANT_ID not set. Running setup script..."
    python setup_assistant.py
    print_warning "Please add the ASSISTANT_ID to your .env file and run this script again."
    exit 1
fi

# Test the server
print_status "Testing server configuration..."
python test_server.py

# Ask for deployment option
echo ""
echo "Choose deployment option:"
echo "1. Run locally (development)"
echo "2. Build Docker image"
echo "3. Deploy to Replit"
echo "4. Show deployment URLs"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        print_status "Starting local development server..."
        python main.py
        ;;
    2)
        print_status "Building Docker image..."
        docker build -t mcp-server-canyon .
        print_status "Docker image built successfully!"
        echo "To run: docker run -p 8000:8000 --env-file .env mcp-server-canyon"
        ;;
    3)
        print_status "Replit deployment instructions:"
        echo "1. Go to replit.com and create a new repl"
        echo "2. Import this GitHub repository"
        echo "3. Add secrets in Replit:"
        echo "   - OPENAI_API_KEY"
        echo "   - VECTOR_STORE_ID"
        echo "   - ASSISTANT_ID"
        echo "4. Click 'Run' button"
        echo "5. Your MCP server URL will be shown in the webview"
        ;;
    4)
        print_status "Deployment platforms:"
        echo ""
        echo "🔗 Replit: https://replit.com/new/github/your-username/mcp-server-canyon"
        echo "🔗 Railway: https://railway.app/new/github/your-username/mcp-server-canyon"
        echo "🔗 Render: https://render.com/deploy?repo=https://github.com/your-username/mcp-server-canyon"
        echo "🔗 Heroku: git push heroku main"
        echo ""
        echo "Remember to set environment variables on your chosen platform!"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

print_status "Deployment script completed!" 