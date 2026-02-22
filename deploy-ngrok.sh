#!/bin/bash

echo "========================================"
echo "🚀 Quick Deploy with ngrok"
echo "========================================"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found!"
    echo ""
    echo "Install ngrok:"
    echo "  brew install ngrok"
    echo "  Or download from: https://ngrok.com/download"
    echo ""
    exit 1
fi

# Check for API keys
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set!"
    echo ""
    read -p "Enter your OpenAI API key: " OPENAI_API_KEY
    export OPENAI_API_KEY
fi

if [ -z "$GOOGLE_GENERATIVE_AI_API_KEY" ]; then
    echo "⚠️  GOOGLE_GENERATIVE_AI_API_KEY not set!"
    echo ""
    read -p "Enter your Google Gemini API key: " GOOGLE_GENERATIVE_AI_API_KEY
    export GOOGLE_GENERATIVE_AI_API_KEY
fi

echo ""
echo "✅ API keys configured"
echo ""

# Start Flask server in background
echo "Starting Flask server on port 5001..."
cd "$(dirname "$0")"
/Users/apple/Documents/Personal/Devaa/Freelance/.venv/bin/python server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if ! curl -s http://localhost:5001 > /dev/null; then
    echo "❌ Server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "✅ Server running (PID: $SERVER_PID)"
echo ""

# Start ngrok
echo "Starting ngrok tunnel..."
echo ""
ngrok http 5001

# Cleanup on exit
kill $SERVER_PID 2>/dev/null
echo ""
echo "Server stopped."
