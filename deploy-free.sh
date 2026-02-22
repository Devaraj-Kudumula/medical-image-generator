#!/bin/bash

# INSTANT FREE DEPLOYMENT WITH NGROK
# ===================================

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  🚀 INSTANT FREE DEPLOYMENT - Medical Image Generator ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found!"
    echo ""
    echo "Installing ngrok..."
    brew install ngrok
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Failed to install ngrok"
        echo ""
        echo "Please install manually:"
        echo "  brew install ngrok"
        echo ""
        exit 1
    fi
fi

echo "✅ ngrok is ready!"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Set API keys
export OPENAI_API_KEY='YOUR_OPENAI_API_KEY'
export GOOGLE_GENERATIVE_AI_API_KEY='YOUR_GOOGLE_API_KEY'

echo "✅ API keys loaded"
echo ""

# Start Flask server in background
echo "🔧 Starting Flask server on port 5001..."
/Users/apple/Documents/Personal/Devaa/Freelance/.venv/bin/python server.py &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:5001 > /dev/null 2>&1; then
    echo "✅ Server is running (PID: $SERVER_PID)"
else
    echo "❌ Server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "🌐 CREATING PUBLIC URL..."
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Your website will be accessible at a public URL!"
echo "Share this URL with anyone to let them use your app."
echo ""
echo "Press Ctrl+C to stop the server and close the tunnel."
echo ""
echo "═══════════════════════════════════════════════════════"
echo ""

# Start ngrok
ngrok http 5001

# Cleanup on exit
echo ""
echo "🛑 Stopping server..."
kill $SERVER_PID 2>/dev/null
echo "✅ Server stopped. Goodbye!"
