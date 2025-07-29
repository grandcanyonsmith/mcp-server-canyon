#!/bin/bash
# Start script for Render deployment

echo "Starting MCP Server on Render..."
echo "Using simplified Flask implementation for initial deployment"

# Install dependencies
pip install -r requirements_flask.txt

# Start the simplified Flask server
python main_simple.py 